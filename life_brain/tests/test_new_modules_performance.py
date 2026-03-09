"""
Performance & load tests for modules added in the current sprint.

Tests verify:
- ConsensusResolver: bulk disagreement detection throughput
- TwoPassConflictSearch: large candidate pool handling
- ConversationalFramer: bulk framing performance
- StalenessDetector: collection-scale stale check
- DataExporter: large export/import round-trip timing

All tests use mocks — no real ChromaDB or network calls.
Timing thresholds are generous (wall-clock safe for CI).
"""

import time
import pytest
from unittest.mock import Mock

from life_brain.conversation.consensus_resolver import ConsensusResolver
from life_brain.truth_engine.two_pass_conflict_search import two_pass_conflict_search
from life_brain.conversation.conversational_framing import ConversationalFramer
from life_brain.truth_engine.staleness_detector import StalenessDetector
from life_brain.db.data_exporter import DataExporter


# ---------- Helpers ----------

def _make_query_result(n: int):
    """Build a mock ChromaDB query() result with n docs."""
    ids = [f"doc{i}" for i in range(n)]
    return {
        "ids": [ids],
        "documents": [[f"Content {i}" for i in range(n)]],
        "metadatas": [[{"company": "Google", "category": "revenue"} for _ in range(n)]],
        "distances": [[0.1 + (i * 0.01) for i in range(n)]],
    }


def _make_get_result(n: int):
    """Build a mock ChromaDB get() result with n docs."""
    ids = [f"struct{i}" for i in range(n)]
    return {
        "ids": ids,
        "documents": [f"Struct content {i}" for i in range(n)],
        "metadatas": [{"company": "Google", "category": "revenue"} for _ in range(n)],
    }


def _make_collection_mock(query_n: int = 10, get_n: int = 20):
    """Mock ChromaDB collection with configurable result sizes."""
    mock = Mock()
    mock.query.return_value = _make_query_result(query_n)
    mock.get.return_value = _make_get_result(get_n)
    return mock


# ---------- ConsensusResolver Performance ----------

class TestConsensusResolverPerformance:
    """Throughput tests for consensus resolution."""

    def test_detect_disagreement_100_pairs(self):
        """detect_disagreement() must handle 100 pairs in < 200ms."""
        resolver = ConsensusResolver()
        pairs = [
            ("Quit your job and build the startup. Risk is opportunity.",
             "Never risk what you have. Stay conservative and protect savings."),
        ] * 100

        start = time.monotonic()
        for a, b in pairs:
            resolver.detect_disagreement(a, b)
        elapsed = time.monotonic() - start

        assert elapsed < 0.2, f"100 disagreement checks took {elapsed:.3f}s (> 200ms)"

    def test_generate_resolution_50_pairs(self):
        """generate_resolution() must handle 50 expert pairs in < 1s."""
        resolver = ConsensusResolver()
        start = time.monotonic()
        for i in range(50):
            resolver.generate_resolution(
                "Elon", "Quit and build the startup. Take the risk.",
                "Warren", "Never risk what you have. Stay safe and protect capital.",
            )
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"50 resolutions took {elapsed:.3f}s (> 1s)"

    def test_extract_position_200_calls(self):
        """extract_position() must process 200 responses in < 300ms."""
        resolver = ConsensusResolver()
        responses = [
            "Build aggressively. Quit, invest, and risk everything.",
            "Stay safe. Never risk what you have. Protect savings.",
            "Interesting approach. Need more context before deciding.",
        ] * 67  # ~200 total

        start = time.monotonic()
        for i, text in enumerate(responses):
            resolver.extract_position(f"Expert{i}", text)
        elapsed = time.monotonic() - start

        assert elapsed < 0.3, f"200 position extractions took {elapsed:.3f}s (> 300ms)"


# ---------- TwoPassConflictSearch Performance ----------

class TestTwoPassConflictSearchPerformance:
    """Performance tests for two-pass conflict search."""

    def test_pass1_100_candidates_returned(self):
        """System must handle 100 candidates from Pass 1 without crash."""
        mock = _make_collection_mock(query_n=100, get_n=0)
        candidates, p1, p2 = two_pass_conflict_search(
            collection=mock,
            query_text="revenue metric",
            query_embedding=None,
            atom_type="story",  # No pass 2
            metadata_filters={},
        )
        assert p1 == 100
        assert len(candidates) == 100

    def test_union_200_candidates_deduped(self):
        """Union of Pass 1 (100) + Pass 2 (100) with 0 overlap = 200 unique."""
        mock = _make_collection_mock(query_n=100, get_n=100)
        candidates, p1, p2 = two_pass_conflict_search(
            collection=mock,
            query_text="revenue metric",
            query_embedding=None,
            atom_type="metric",
            metadata_filters={"company": "Google"},
        )
        # 100 semantic (doc0..doc99) + 100 structural (struct0..struct99) = 200
        assert len(candidates) == 200
        assert p1 == 100
        assert p2 == 100

    def test_full_dedup_when_all_overlap(self):
        """When Pass 1 and Pass 2 return same IDs, dedup yields only Pass 1 count."""
        ids = [f"doc{i}" for i in range(50)]
        mock = Mock()
        mock.query.return_value = {
            "ids": [ids],
            "documents": [[f"Content {i}" for i in range(50)]],
            "metadatas": [[{}] * 50],
            "distances": [[0.1] * 50],
        }
        mock.get.return_value = {
            "ids": ids,  # Same IDs
            "documents": [f"Content {i}" for i in range(50)],
            "metadatas": [{}] * 50,
        }
        candidates, p1, p2 = two_pass_conflict_search(
            collection=mock,
            query_text="metric test",
            query_embedding=None,
            atom_type="metric",
            metadata_filters={"company": "Google"},
        )
        # All 50 found in Pass 1 → Pass 2 adds 0 new (all dupes)
        assert len(candidates) == 50
        assert p2 == 0

    def test_throughput_100_searches_under_500ms(self):
        """100 two-pass searches against mock collection in < 500ms."""
        mock = _make_collection_mock(query_n=5, get_n=5)
        start = time.monotonic()
        for _ in range(100):
            two_pass_conflict_search(
                collection=mock,
                query_text="revenue growth metric",
                query_embedding=None,
                atom_type="metric",
                metadata_filters={"company": "Google"},
            )
        elapsed = time.monotonic() - start
        assert elapsed < 0.5, f"100 two-pass searches took {elapsed:.3f}s (> 500ms)"


# ---------- ConversationalFramer Performance ----------

class TestConversationalFramerPerformance:
    """Performance tests for question framing."""

    def test_frame_1000_questions_in_200ms(self):
        """Frame 1000 questions across all modes in < 200ms."""
        framer = ConversationalFramer()
        use_cases = ["C1", "R2", "H3", "P1", "F2", "M1", "CR2", "P4"]
        start = time.monotonic()
        for i in range(1000):
            uc = use_cases[i % len(use_cases)]
            framer.frame_question(
                use_case_id=uc,
                question_text=f"Question number {i}?",
                question_index=i % 8,
                total_questions=8,
                opener_index=i % 4,
            )
        elapsed = time.monotonic() - start
        assert elapsed < 0.2, f"1000 framings took {elapsed:.3f}s (> 200ms)"

    def test_render_question_consistency(self):
        """render_question() must produce consistent output for same inputs."""
        framer = ConversationalFramer()
        outputs = [
            framer.render_question("C3", "Biggest achievement?", 2, 8, opener_index=0)
            for _ in range(100)
        ]
        assert len(set(outputs)) == 1  # All identical

    def test_mode_lookup_1000_calls_fast(self):
        """get_mode() dict lookup must handle 1000 calls in < 50ms."""
        framer = ConversationalFramer()
        keys = ["C1", "R3", "H2", "P2", "F4", "M2", "CR1", "P5", "UNKNOWN"] * 112
        start = time.monotonic()
        for k in keys[:1000]:
            framer.get_mode(k)
        elapsed = time.monotonic() - start
        assert elapsed < 0.05, f"1000 mode lookups took {elapsed:.3f}s (> 50ms)"


# ---------- StalenessDetector Performance ----------

class TestStalenessDetectorPerformance:
    """Performance tests for staleness detection."""

    def test_check_collection_500_docs(self):
        """Staleness check of 500 docs must complete in < 200ms."""
        from datetime import datetime, timedelta
        mock = Mock()
        old_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        fresh_date = datetime.now().strftime("%Y-%m-%d")
        metas = [
            {"domain": "finance", "date": old_date} if i % 2 == 0
            else {"domain": "finance", "date": fresh_date}
            for i in range(500)
        ]
        mock.get.return_value = {
            "ids": [f"doc{i}" for i in range(500)],
            "documents": [f"Content {i}" for i in range(500)],
            "metadatas": metas,
        }
        detector = StalenessDetector(collection=mock)

        start = time.monotonic()
        result = detector.check_collection_for_stale()
        elapsed = time.monotonic() - start

        assert elapsed < 0.2, f"500 doc staleness check took {elapsed:.3f}s (> 200ms)"
        # ~250 docs should be stale (old dates, finance=365d window)
        assert result.stale_count >= 200

    def test_is_stale_100_checks_fast(self):
        """100 is_stale() calls must complete in < 50ms."""
        from datetime import datetime, timedelta
        detector = StalenessDetector(collection=None)
        old_date = (datetime.now() - timedelta(days=500)).strftime("%Y-%m-%d")

        start = time.monotonic()
        for _ in range(100):
            detector.is_stale({"domain": "finance", "date": old_date})
        elapsed = time.monotonic() - start

        assert elapsed < 0.05


# ---------- DataExporter Performance ----------

class TestDataExporterPerformance:
    """Performance tests for data export/import."""

    def _make_large_collection(self, n: int):
        """Mock collection with n documents."""
        mock = Mock()
        mock.get.return_value = {
            "ids": [f"doc{i}" for i in range(n)],
            "documents": [f"Career content {i} — detailed text about experiences." for i in range(n)],
            "metadatas": [{"domain": "career", "company": "Google", "date": "2024-01-01"} for _ in range(n)],
        }
        return mock

    def test_export_1000_docs_under_500ms(self):
        """Export of 1000 documents must complete in < 500ms."""
        exporter = DataExporter(collection=self._make_large_collection(1000))
        start = time.monotonic()
        result, error = exporter.export_all()
        elapsed = time.monotonic() - start

        assert error is None
        assert result.total_documents == 1000
        assert elapsed < 0.5, f"Export of 1000 docs took {elapsed:.3f}s (> 500ms)"

    def test_import_500_records_under_1s(self):
        """Import of 500 records must complete in < 1s."""
        mock = Mock()
        mock.upsert.return_value = None
        exporter = DataExporter(collection=mock)

        records = [
            {"doc_id": f"d{i}", "text": f"Content {i}", "metadata": {"domain": "career"}}
            for i in range(500)
        ]

        start = time.monotonic()
        result = exporter.import_from_dict({"records": records})
        elapsed = time.monotonic() - start

        assert result.successful == 500
        assert elapsed < 1.0, f"Import of 500 records took {elapsed:.3f}s (> 1s)"

    def test_export_to_json_string_1000_docs(self):
        """to_json() serialization of 1000 docs must be < 500ms."""
        exporter = DataExporter(collection=self._make_large_collection(1000))
        result, _ = exporter.export_all()

        start = time.monotonic()
        json_str = result.to_json()
        elapsed = time.monotonic() - start

        assert len(json_str) > 0
        assert elapsed < 0.5

    def test_round_trip_200_docs(self):
        """Export + import round-trip for 200 docs must be < 1s total."""
        exporter = DataExporter(collection=self._make_large_collection(200))

        start = time.monotonic()
        result, _ = exporter.export_all()

        import_mock = Mock()
        import_mock.upsert.return_value = None
        importer = DataExporter(collection=import_mock)
        import_result = importer.import_from_dict(result.to_dict())
        elapsed = time.monotonic() - start

        assert import_result.successful == 200
        assert elapsed < 1.0, f"Round-trip 200 docs took {elapsed:.3f}s (> 1s)"
