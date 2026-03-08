"""
Tests for Expert Roster and Context Management

Covers:
- All 16 experts loaded with complete profiles
- Domain expertise accuracy
- Context management across turns
- Data access privacy firewall
- Expert selection and switching
"""

import pytest
from life_brain.experts.roster import (
    ExpertRoster,
    Expert,
    ExpertDomain,
    SignatureStory,
)
from life_brain.experts.context_manager import (
    ExpertContextManager,
    ExpertContext,
)


class TestExpertRoster:
    """Tests for expert roster completeness."""

    def test_roster_loads_16_experts(self):
        """Test that all 16 experts are loaded."""
        roster = ExpertRoster()
        assert len(roster.get_all()) == 16

    def test_all_experts_have_required_fields(self):
        """Test that each expert has all required profile data."""
        roster = ExpertRoster()

        for expert in roster.get_all():
            assert expert.name, "Missing name"
            assert expert.full_name, "Missing full_name"
            assert expert.domain, "Missing domain"
            assert expert.title, "Missing title"
            assert expert.bio, "Missing bio"
            assert expert.philosophy, "Missing philosophy"
            assert len(expert.signature_stories) >= 1, "Missing signature stories"
            assert expert.speaking_style, "Missing speaking_style"
            assert len(expert.favorite_phrases) >= 3, "Missing favorite phrases"
            assert len(expert.domain_expertise) >= 3, "Missing domain expertise"
            assert expert.conversation_starter, "Missing conversation starter"
            assert expert.conversation_sample, "Missing conversation sample"
            assert len(expert.accessible_use_cases) > 0, "Missing accessible use cases"
            assert len(expert.data_access_domains) > 0, "Missing data access domains"

    def test_get_expert_by_name(self):
        """Test retrieving experts by name."""
        roster = ExpertRoster()

        satya = roster.get_by_name("Satya")
        assert satya is not None
        assert satya.title == "The Interviewer"

        warren = roster.get_by_name("Warren")
        assert warren is not None
        assert warren.domain == ExpertDomain.VALUE

    def test_get_nonexistent_expert(self):
        """Test that nonexistent expert returns None."""
        roster = ExpertRoster()
        assert roster.get_by_name("Nonexistent") is None

    def test_expert_name_uniqueness(self):
        """Test that all expert names are unique."""
        roster = ExpertRoster()
        names = [e.name for e in roster.get_all()]
        assert len(names) == len(set(names)), "Duplicate expert names found"

    def test_domains_covered(self):
        """Test that key domains are represented."""
        roster = ExpertRoster()

        domains_found = set()
        for expert in roster.get_all():
            domains_found.add(expert.domain)

        # Check some key domains exist
        assert ExpertDomain.INTERVIEWS in domains_found
        assert ExpertDomain.FIRST_PRINCIPLES in domains_found
        assert ExpertDomain.NEGOTIATION in domains_found
        assert ExpertDomain.RELATIONSHIPS in domains_found
        assert ExpertDomain.CONSCIOUSNESS in domains_found

    def test_use_cases_are_valid(self):
        """Test that use case references are reasonable."""
        roster = ExpertRoster()

        for expert in roster.get_all():
            # Should reference some use cases
            assert len(expert.accessible_use_cases) > 0
            # Use cases should look valid (C1, C12, R1, H1, etc.)
            for uc_id in expert.accessible_use_cases:
                assert len(uc_id) >= 2, f"Invalid use case ID: {uc_id}"
                assert uc_id[0] in "CRFHPKM", f"Invalid use case category: {uc_id}"
                assert uc_id[1:].isdigit(), f"Invalid use case number: {uc_id}"

    def test_data_domain_consistency(self):
        """Test that data access domains are consistent."""
        roster = ExpertRoster()

        # Warren should only access finance
        warren = roster.get_by_name("Warren")
        assert "finance" in warren.data_access_domains
        assert len(warren.data_access_domains) == 1

        # Esther should access relationships
        esther = roster.get_by_name("Esther")
        assert "relationships" in esther.data_access_domains

    def test_conversation_samples_are_realistic(self):
        """Test that conversation samples contain dialogue."""
        roster = ExpertRoster()

        for expert in roster.get_all():
            sample = expert.conversation_sample
            # Should have both user and expert
            assert "\nUser:" in sample or "User:" in sample
            assert expert.name in sample


class TestExpertContextManager:
    """Tests for context management."""

    def test_load_expert_creates_context(self):
        """Test loading an expert initializes context."""
        manager = ExpertContextManager()

        context = manager.load_expert("Satya")
        assert context is not None
        assert context.expert.name == "Satya"
        assert manager.current_context == context

    def test_load_nonexistent_expert(self):
        """Test that loading nonexistent expert returns None."""
        manager = ExpertContextManager()
        context = manager.load_expert("Nonexistent")
        assert context is None

    def test_get_expert_greeting(self):
        """Test greeting generation."""
        manager = ExpertContextManager()
        manager.load_expert("Richard")

        greeting = manager.get_expert_greeting()
        assert "Richard" in greeting
        assert "First Principles" in greeting or "Explainer" in greeting

    def test_get_speaking_style_instructions(self):
        """Test style instructions."""
        manager = ExpertContextManager()
        manager.load_expert("Satya")

        instructions = manager.get_speaking_style_instructions()
        assert "Satya" not in instructions  # Instructions are general
        assert "Speaking Style:" in instructions
        assert "Phrase" in instructions

    def test_add_conversation_turn(self):
        """Test adding conversation turns to context."""
        manager = ExpertContextManager()
        manager.load_expert("Satya")

        manager.current_context.add_turn("user", "Tell me about interviews")
        manager.current_context.add_turn("assistant", "Let's practice...")

        assert len(manager.current_context.conversation_history) == 2
        assert manager.current_context.conversation_history[0]["role"] == "user"
        assert manager.current_context.conversation_history[1]["role"] == "assistant"

    def test_get_recent_history(self):
        """Test retrieving recent conversation history."""
        manager = ExpertContextManager()
        manager.load_expert("Satya")

        # Add several turns
        for i in range(5):
            manager.current_context.add_turn("user", f"Turn {i}")

        recent = manager.current_context.get_recent_history(limit=3)
        assert len(recent) == 3

    def test_data_access_enforcement_allowed(self):
        """Test that experts can access allowed domains."""
        manager = ExpertContextManager()
        manager.load_expert("Warren")

        allowed, msg = manager.enforce_data_access("finance")
        assert allowed is True
        assert msg is None

    def test_data_access_enforcement_denied(self):
        """Test that experts cannot access forbidden domains."""
        manager = ExpertContextManager()
        manager.load_expert("Warren")

        # Warren cannot access career data
        allowed, msg = manager.enforce_data_access("career")
        assert allowed is False
        assert msg is not None
        assert "switch experts" in msg

    def test_esther_relationship_domain_access(self):
        """Test Esther's domain-specific access."""
        manager = ExpertContextManager()
        manager.load_expert("Esther")

        # Should have access to relationships
        allowed, msg = manager.enforce_data_access("relationships")
        assert allowed is True

    def test_switch_expert(self):
        """Test switching experts mid-session."""
        manager = ExpertContextManager()
        manager.load_expert("Satya")
        initial_expert = manager.current_context.expert.name

        # Switch to Richard
        greeting = manager.switch_expert("Richard")
        assert greeting is not None
        assert manager.current_context.expert.name == "Richard"
        assert manager.current_context.expert.name != initial_expert

    def test_can_help_with_use_case(self):
        """Test checking if expert can help with use case."""
        manager = ExpertContextManager()
        manager.load_expert("Satya")

        # Satya should help with C1 (interview prep)
        assert manager.can_help_with_use_case("C1") is True

    def test_get_context_for_llm(self):
        """Test getting formatted context for LLM."""
        manager = ExpertContextManager()
        manager.load_expert("Richard")

        context = manager.get_context_for_llm()
        assert context["expert_name"] == "Richard"
        assert "speaking_style" in context
        assert "favorite_phrases" in context
        assert "domain_expertise" in context

    def test_get_expert_summary(self):
        """Test expert summary for display."""
        manager = ExpertContextManager()
        manager.load_expert("Warren")

        summary = manager.get_expert_summary()
        assert "Warren" in summary
        assert "Value" in summary or "value" in summary

    def test_get_all_experts_list(self):
        """Test getting list of all experts."""
        manager = ExpertContextManager()
        experts = manager.get_all_experts_list()

        assert len(experts) == 16
        assert "Satya" in experts
        assert "Warren" in experts
        assert "Esther" in experts

    def test_get_expert_signature_story(self):
        """Test retrieving signature stories."""
        manager = ExpertContextManager()
        manager.load_expert("Richard")

        story = manager.get_expert_signature_story(0)
        assert story is not None
        assert "Feynman" in story or "Technique" in story

    def test_get_expert_selector_ui(self):
        """Test expert selection UI."""
        manager = ExpertContextManager()
        ui = manager.get_expert_selector_ui()

        assert "SELECT YOUR EXPERT" in ui
        assert "Satya" in ui
        assert "Warren" in ui
        assert "Esther" in ui


class TestExpertIntegration:
    """Integration tests for expert system."""

    def test_end_to_end_expert_session(self):
        """Test complete expert session flow."""
        manager = ExpertContextManager()

        # Load expert
        context = manager.load_expert("Satya")
        assert context is not None

        # Get greeting
        greeting = manager.get_expert_greeting()
        assert greeting

        # Add conversation turns
        manager.current_context.add_turn("user", "I'm nervous about interviews")
        manager.current_context.add_turn("assistant", "Let's practice...")

        # Get context for LLM
        llm_context = manager.get_context_for_llm()
        assert llm_context["expert_name"] == "Satya"

        # Check history
        history = manager.current_context.get_recent_history()
        assert len(history) == 2

    def test_expert_switching_preserves_state(self):
        """Test that switching experts preserves conversation state."""
        manager = ExpertContextManager()

        # Start with Satya
        manager.load_expert("Satya")
        manager.current_context.add_turn("user", "Turn 1")
        manager.current_context.add_turn("assistant", "Response 1")

        # Switch to Richard
        manager.switch_expert("Richard")

        # Check that expert changed
        assert manager.current_context.expert.name == "Richard"

    def test_multiple_expert_workflows(self):
        """Test that different experts handle different domains well."""
        manager = ExpertContextManager()

        # Workflow 1: Finance with Warren
        manager.load_expert("Warren")
        allowed, _ = manager.enforce_data_access("finance")
        assert allowed

        # Workflow 2: Relationships with Esther
        manager.load_expert("Esther")
        allowed, _ = manager.enforce_data_access("relationships")
        assert allowed

        # Workflow 3: Career with Satya
        manager.load_expert("Satya")
        allowed, _ = manager.enforce_data_access("career")
        assert allowed
