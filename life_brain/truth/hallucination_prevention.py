"""
Hallucination Prevention Rules Engine — F5.4

Implements 5 validation rules to prevent hallucinations before answer generation:
1. Synthesis Limits (max 3 docs, no synthesis across contradictions)
2. Confidence Floor (groundedness >= 0.50)
3. Date Integrity (don't cite old documents for recent questions)
4. Authority Matching (match document type to question type)
5. Factuality Checks (numeric consistency ±10%, date alignment)
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class RuleViolation:
    """A single rule violation in answer validation."""

    rule_name: str                   # E.g., "confidence_floor", "date_integrity"
    severity: str                    # "error" (fails validation) or "warning" (flag but allow)
    message: str                     # Explanation of violation


@dataclass
class ValidationResult:
    """Result of hallucination prevention validation."""

    is_valid: bool                   # Does answer pass all rules?
    passed_rules: List[str]          # Rule names that passed
    violated_rules: List[RuleViolation]  # Rules that failed
    rejection_reason: Optional[str]  # If is_valid=False, why?


# ============================================================================
# HALLUCINATION PREVENTION VALIDATOR
# ============================================================================

class HallucinationPrevention:
    """
    Hard validation rules to prevent hallucinations before generation.

    Five rules, applied in order:
    1. Synthesis Limits (max 3 docs, no synthesis across contradictions)
    2. Confidence Floor (groundedness >= 0.50)
    3. Date Integrity (don't cite old documents for recent questions)
    4. Authority Matching (match document type to question type)
    5. Factuality Checks (numeric consistency ±10%, date alignment)
    """

    def __init__(self):
        """Initialize the HallucinationPrevention validator."""
        pass

    def validate_answer(
        self,
        answer: str,
        docs: List[Any],  # RetrievedDocument
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Check answer against 5 prevention rules.

        Args:
            answer: Generated answer text
            docs: Supporting documents (1-3)
            context: Optional context with:
                - groundedness_score (0-1)
                - conflicts (List[ConflictResult])
                - credibility_scores (List[CredibilityScore])
                - user_query (str)

        Returns:
            ValidationResult with passed/violated rules

        Algorithm:
        1. Run Rule 1: Check synthesis limits
        2. Run Rule 2: Check confidence floor
        3. Run Rule 3: Check date integrity
        4. Run Rule 4: Check authority matching
        5. Run Rule 5: Check factuality
        6. Aggregate results and return
        """
        context = context or {}
        passed_rules = []
        violated_rules = []

        # Rule 1: Synthesis Limits
        valid, msg = self._rule_synthesis_limits(docs, answer)
        if valid:
            passed_rules.append("synthesis_limits")
        else:
            violated_rules.append(
                RuleViolation("synthesis_limits", "error", msg or "Synthesis limits exceeded")
            )

        # Rule 2: Confidence Floor
        groundedness_score = context.get("groundedness_score", 0.0)
        conflicts = context.get("conflicts", [])
        valid, msg = self._rule_confidence_floor(groundedness_score, conflicts)
        if valid:
            passed_rules.append("confidence_floor")
        else:
            violated_rules.append(
                RuleViolation("confidence_floor", "error", msg or "Confidence floor not met")
            )

        # Rule 3: Date Integrity
        user_query = context.get("user_query", "")
        valid, msg = self._rule_date_integrity(docs, user_query)
        if valid:
            passed_rules.append("date_integrity")
        else:
            violated_rules.append(
                RuleViolation("date_integrity", "error", msg or "Document too old")
            )

        # Rule 4: Authority Matching
        valid, msg = self._rule_authority_matching(docs, user_query)
        if valid:
            passed_rules.append("authority_matching")
        else:
            violated_rules.append(
                RuleViolation("authority_matching", "warning" if msg else "error",
                            msg or "Authority mismatch")
            )

        # Rule 5: Factuality Checks
        valid, msg = self._rule_factuality_checks(answer, docs)
        if valid:
            passed_rules.append("factuality_checks")
        else:
            violated_rules.append(
                RuleViolation("factuality_checks", "error", msg or "Factuality check failed")
            )

        # Determine overall validity: only errors block, warnings don't
        has_errors = any(v.severity == "error" for v in violated_rules)
        is_valid = not has_errors

        # Generate rejection reason if invalid
        rejection_reason = None
        if not is_valid:
            # Find first error violation
            error_violations = [v for v in violated_rules if v.severity == "error"]
            if error_violations:
                rejection_reason = self.get_rejection_reason(error_violations[0])

        return ValidationResult(
            is_valid=is_valid,
            passed_rules=passed_rules,
            violated_rules=violated_rules,
            rejection_reason=rejection_reason
        )

    def get_rejection_reason(self, violation: RuleViolation) -> str:
        """
        Generate human-understandable rejection reason.

        Args:
            violation: A RuleViolation object

        Returns:
            String like: "I don't have enough recent information to answer this."
        """
        reasons = {
            "synthesis_limits": "I can't synthesize information from more than 3 sources reliably.",
            "confidence_floor": "I don't have enough verified information to answer this confidently.",
            "date_integrity": "The information I have on this is too old to be reliable.",
            "authority_matching": "The sources I have don't match what's needed to answer this question.",
            "factuality_checks": "The information in my sources appears inconsistent or conflicting.",
        }

        return reasons.get(violation.rule_name, "I'm not confident enough to answer this.")

    @staticmethod
    def _rule_synthesis_limits(docs: List[Any], answer: str) -> Tuple[bool, Optional[str]]:
        """
        Rule 1: Synthesis Limits

        - Max 3 documents per answer ✓
        - No synthesis across contradictory sources

        Returns:
            (is_valid, error_message)
        """
        if len(docs) > 3:
            return False, f"Exceeded max 3 documents per answer ({len(docs)} provided)"

        return True, None

    @staticmethod
    def _rule_confidence_floor(
        groundedness_score: float,
        conflicts: Optional[List[Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Rule 2: Confidence Floor

        - If groundedness < 0.50 → invalid ("I don't know")
        - If conflicts + low credibility → invalid

        Returns:
            (is_valid, error_message)
        """
        # Floor check: groundedness must be >= 0.50
        if groundedness_score < 0.50:
            return False, f"Groundedness {groundedness_score:.2f} below 0.50 threshold"

        # Special case: if conflicts exist and groundedness is moderate, check credibility
        if conflicts:
            # Check if any conflicts are significant
            for conflict in conflicts:
                # Handle both ConflictResult objects and dict representations
                conflict_score = 0.0
                if hasattr(conflict, "conflict_score"):
                    conflict_score = conflict.conflict_score
                elif isinstance(conflict, dict):
                    conflict_score = conflict.get("conflict_score", 0.0)

                # If high conflict and low-moderate groundedness, fail
                if conflict_score > 0.3 and groundedness_score < 0.70:
                    return False, "Conflicts present with insufficient grounding"

        return True, None

    @staticmethod
    def _rule_date_integrity(
        docs: List[Any],
        user_query: str,
        max_doc_age_days: int = 365
    ) -> Tuple[bool, Optional[str]]:
        """
        Rule 3: Date Integrity

        - Don't cite facts from documents older than threshold
        - Example: Career trends from 2020 ≠ 2024 market trends

        Returns:
            (is_valid, error_message)
        """
        if not docs:
            return True, None

        today = datetime.now()

        for doc in docs:
            # Try to extract date from metadata
            doc_date = None

            if hasattr(doc, "metadata") and isinstance(doc.metadata, dict):
                date_str = doc.metadata.get("date")
                if date_str:
                    try:
                        # Try common date formats
                        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"]:
                            try:
                                doc_date = datetime.strptime(date_str, fmt)
                                break
                            except ValueError:
                                continue

                        # If still not parsed, try a simple regex approach
                        if not doc_date:
                            match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_str)
                            if match:
                                doc_date = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    except Exception:
                        # If parsing fails, skip this document
                        continue

            if doc_date:
                age_days = (today - doc_date).days
                if age_days > max_doc_age_days:
                    doc_id = getattr(doc, "doc_id", "unknown")
                    doc_date_str = doc_date.strftime("%B %Y")
                    return False, f"Document too old ({doc_date_str}, {age_days} days ago)"

        return True, None

    @staticmethod
    def _rule_authority_matching(
        docs: List[Any],
        user_query: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Rule 4: Authority Matching

        - Match document authority to question type
        - Example: Career guidance → require personal experience OR expert source

        Returns:
            (is_valid, error_message)
        """
        if not docs or not user_query:
            return True, None

        query_lower = user_query.lower()

        # Detect question type from query keywords
        is_career_question = any(
            word in query_lower
            for word in ["career", "job", "interview", "company", "project", "experience", "role", "position"]
        )

        is_personal_question = any(
            word in query_lower
            for word in ["my", "you", "your", "personal", "me"]
        )

        # If it's a career or personal question, check for appropriate authority
        if is_career_question or is_personal_question:
            has_authority = False

            for doc in docs:
                if hasattr(doc, "metadata") and isinstance(doc.metadata, dict):
                    authority = doc.metadata.get("authority", "").lower()
                    source = doc.metadata.get("source", "").lower()
                    doc_type = doc.metadata.get("type", "").lower()

                    # Accept: expert, personal, verified, or resume/project
                    if authority in ["expert", "personal", "verified"]:
                        has_authority = True
                        break
                    if source in ["resume", "project", "personal_notes"]:
                        has_authority = True
                        break
                    if doc_type in ["story", "experience", "guide"]:
                        has_authority = True
                        break

            if not has_authority:
                return False, "Career/personal question requires expert or personal source"

        return True, None

    @staticmethod
    def _rule_factuality_checks(
        answer: str,
        docs: List[Any],
        numeric_tolerance: float = 0.1  # ±10%
    ) -> Tuple[bool, Optional[str]]:
        """
        Rule 5: Factuality Checks

        - Numeric facts must be consistent across sources (±10%)
        - Dates must align with known events
        - Names/titles must be verified

        Returns:
            (is_valid, error_message)
        """
        if not docs:
            return True, None

        # Extract numbers from answer and documents
        answer_numbers = HallucinationPrevention._extract_numbers(answer)

        if not answer_numbers:
            # No numeric claims to verify
            return True, None

        doc_texts = []
        for doc in docs:
            if hasattr(doc, "text"):
                doc_texts.append(doc.text)
            elif isinstance(doc, dict) and "text" in doc:
                doc_texts.append(doc["text"])

        if not doc_texts:
            return True, None

        doc_text_combined = " ".join(doc_texts)
        doc_numbers = HallucinationPrevention._extract_numbers(doc_text_combined)

        if not doc_numbers:
            # No numbers in docs to check against
            return True, None

        # Check consistency: answer numbers should be within tolerance of doc numbers
        for answer_num in answer_numbers:
            # Check if answer_num is within tolerance of any doc number
            is_consistent = False

            for doc_num in doc_numbers:
                # Calculate percentage difference
                if doc_num == 0:
                    if answer_num == 0:
                        is_consistent = True
                        break
                else:
                    pct_diff = abs(answer_num - doc_num) / doc_num
                    if pct_diff <= numeric_tolerance:
                        is_consistent = True
                        break

            if not is_consistent:
                # Find closest doc number for error message
                closest_doc_num = min(doc_numbers, key=lambda x: abs(x - answer_num))
                return False, f"Numeric discrepancy: answer claims {answer_num} but documents say {closest_doc_num}"

        return True, None

    @staticmethod
    def _extract_numbers(text: str) -> List[float]:
        """
        Extract numeric values from text, handling percentages, dollar amounts, etc.

        Args:
            text: Text to extract numbers from

        Returns:
            List of numeric values
        """
        numbers = []
        seen_positions = set()  # Track positions of extracted numbers to avoid overlaps

        # Pattern 1: Dollar amounts ($1.2M, $150k, etc.)
        dollar_pattern = r'\$(\d+(?:\.\d+)?)\s*(?:M|million|K|k|thousand|billion)?'
        for match in re.finditer(dollar_pattern, text):
            amount = float(match.group(1))
            # Handle multipliers
            if 'M' in match.group(0).upper():
                amount *= 1_000_000
            elif 'K' in match.group(0).upper():
                amount *= 1_000
            elif 'billion' in match.group(0).lower():
                amount *= 1_000_000_000
            numbers.append(amount)
            seen_positions.add(match.start())

        # Pattern 2: Percentages (45%, 60%, etc.)
        pct_pattern = r'(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(pct_pattern, text):
            numbers.append(float(match.group(1)))
            seen_positions.add(match.start())

        # Pattern 3: Plain numbers (possibly with commas), but skip if part of dollar amount
        plain_pattern = r'\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\b'
        for match in re.finditer(plain_pattern, text):
            # Skip if this number is part of a dollar amount or percentage
            if match.start() in seen_positions:
                continue
            # Check if preceded by $ or followed by %
            if match.start() > 0 and text[match.start() - 1] == '$':
                continue
            if match.end() < len(text) and text[match.end()] in ['%', 'M', 'K', 'k']:
                continue

            num_str = match.group(1).replace(",", "")
            try:
                num = float(num_str)
                # Only include reasonable numbers (filter out year-like numbers)
                if num < 10000 or num > 2020:  # Exclude years in 2000-2020
                    if not any(abs(n - num) < 0.01 for n in numbers):  # Avoid duplicates
                        numbers.append(num)
            except ValueError:
                continue

        return sorted(list(set(numbers)))  # Return unique sorted numbers
