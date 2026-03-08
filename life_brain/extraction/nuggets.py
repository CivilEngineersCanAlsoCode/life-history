"""
Atomic nugget extraction — parse raw answer into MECE nuggets.

Rule: one subject + one predicate = one nugget
Metrics ALWAYS separate nuggets
"""

from typing import List, Optional
from dataclasses import dataclass
from anthropic import Anthropic


@dataclass
class Nugget:
    """Atomic knowledge unit: subject + predicate."""
    subject: str
    predicate: str
    atom_type: str  # METRIC, FACT, STORY, DECISION, LESSON
    confidence: float = 0.9


NUGGET_EXTRACTION_PROMPT = """
Break this answer into atomic nuggets.

RULE: one subject + one predicate = one nugget
RULE: Metrics ALWAYS separate nuggets (keep exact numbers)
RULE: Each nugget must be independent (can remove one without breaking others)

EXAMPLE:
Raw: "CGB mein challenge tha ki data siloed tha. I integrated 14 APIs. Latency 48h → 15min."
Nuggets:
- Subject: CGB | Predicate: data was siloed (FACT)
- Subject: I | Predicate: integrated 14 government APIs (METRIC)
- Subject: latency | Predicate: reduced from 48 hours to 15 minutes (METRIC)

RAW ANSWER:
{raw_answer}

NUGGETS (JSON format):
[
  {{"subject": "...", "predicate": "...", "atom_type": "FACT|METRIC|STORY|DECISION|LESSON"}},
  ...
]
"""


class NuggetExtractor:
    """Extracts MECE nuggets from raw answers."""

    def __init__(self):
        self.client = Anthropic()

    def identify_nuggets(self, raw_answer: str) -> List[Nugget]:
        """
        Break raw answer into atomic nuggets using LLM.

        Args:
            raw_answer: User's raw unstructured answer (Hinglish or English)

        Returns:
            List of Nugget objects
        """
        # TODO: Implement
        # 1. Call Claude API with NUGGET_EXTRACTION_PROMPT
        # 2. Parse JSON response → List[Nugget]
        # 3. Validate: each nugget has subject + predicate
        # 4. Assign atom_type if not provided
        # 5. Return nuggets list
        pass

    def validate_nugget_independence(self, nuggets: List[Nugget]) -> bool:
        """
        Verify nuggets are independent (removing one doesn't break others).

        Args:
            nuggets: List of nuggets to validate

        Returns:
            True if all nuggets are independent
        """
        # TODO: Implement
        # Check that no nugget depends on understanding another nugget
        # Use semantic similarity — if nuggets share too many concepts → flag
        pass

    def extract_atoms_from_raw(self, raw_answer: str) -> dict:
        """
        Extract structured atoms (entities, numbers, verbs) from raw text.

        Used for structural CE validation.

        Returns:
            {entities: [...], numbers: [...], verbs: [...], dates: [...]}
        """
        # TODO: Implement using spaCy NLP
        # Extract entities, numbers, verbs, date patterns
        # Return structured atom dict
        pass
