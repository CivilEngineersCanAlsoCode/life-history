"""
Atomic nugget extraction — parse raw answer into MECE nuggets.

Rule: one subject + one predicate = one nugget
Metrics ALWAYS separate nuggets
"""

from typing import List, Optional
from dataclasses import dataclass
from life_brain.utils.claude_cli import Anthropic  # Claude CLI, no API key needed


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
        import json

        try:
            # Call Claude API with extraction prompt
            prompt = NUGGET_EXTRACTION_PROMPT.format(raw_answer=raw_answer)

            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse JSON response
            response_text = response.content[0].text
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("[")
                json_end = response_text.rfind("]") + 1
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.find("[")
                json_end = response_text.rfind("]") + 1
                response_text = response_text[json_start:json_end]

            nugget_dicts = json.loads(response_text)

            # Convert to Nugget objects
            nuggets = []
            for nugget_dict in nugget_dicts:
                # Validate required fields
                if "subject" not in nugget_dict or "predicate" not in nugget_dict:
                    continue

                # Assign atom_type if not provided
                atom_type = nugget_dict.get("atom_type", "FACT")
                confidence = float(nugget_dict.get("confidence", 0.9))

                nugget = Nugget(
                    subject=nugget_dict["subject"],
                    predicate=nugget_dict["predicate"],
                    atom_type=atom_type,
                    confidence=confidence
                )
                nuggets.append(nugget)

            return nuggets

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse nugget extraction response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to extract nuggets: {e}")

    def validate_nugget_independence(self, nuggets: List[Nugget]) -> bool:
        """
        Verify nuggets are independent (removing one doesn't break others).

        Args:
            nuggets: List of nuggets to validate

        Returns:
            True if all nuggets are independent
        """
        if len(nuggets) <= 1:
            return True

        # Check for problematic dependencies between nuggets
        for i, nugget1 in enumerate(nuggets):
            nugget1_text = f"{nugget1.subject} {nugget1.predicate}".lower()

            for j, nugget2 in enumerate(nuggets):
                if i == j:
                    continue

                nugget2_text = f"{nugget2.subject} {nugget2.predicate}".lower()

                # Check if nugget1 appears to depend on nugget2
                # (high term overlap combined with sequential structure)
                common_words = set(nugget1_text.split()) & set(nugget2_text.split())

                # If >50% of words overlap, they might be dependent
                overlap_ratio = len(common_words) / max(len(nugget1_text.split()), 1)

                if overlap_ratio > 0.5:
                    # Use LLM to determine if truly independent
                    try:
                        response = self.client.messages.create(
                            model="claude-opus-4-6",
                            max_tokens=50,
                            messages=[{
                                "role": "user",
                                "content": f"""Can these nuggets exist independently?

Nugget 1: {nugget1_text}
Nugget 2: {nugget2_text}

Answer ONLY 'yes' or 'no':"""
                            }]
                        )
                        answer = response.content[0].text.strip().lower()
                        if "no" in answer:
                            return False
                    except Exception:
                        # On error, conservatively flag as potentially dependent
                        return False

        return True

    def extract_atoms_from_raw(self, raw_answer: str) -> dict:
        """
        Extract structured atoms (entities, numbers, verbs) from raw text.

        Used for structural CE validation.

        Returns:
            {entities: [...], numbers: [...], verbs: [...], dates: [...]}
        """
        import re
        import spacy

        try:
            # Load spaCy model
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(raw_answer)

            # Extract entities (PERSON, ORG, GPE, PRODUCT, etc.)
            entities = [
                {"text": ent.text, "label": ent.label_}
                for ent in doc.ents
            ]

            # Extract verbs (VERB tags)
            verbs = [
                token.text
                for token in doc
                if token.pos_ == "VERB"
            ]

            # Extract numbers
            numbers = re.findall(r'\d+\.?\d*', raw_answer)

            # Extract dates (simple pattern matching)
            date_patterns = [
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # DD-MM-YYYY or MM/DD/YYYY
                r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',    # YYYY-MM-DD
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
            ]
            dates = []
            for pattern in date_patterns:
                dates.extend(re.findall(pattern, raw_answer, re.IGNORECASE))

            return {
                "entities": entities,
                "numbers": numbers,
                "verbs": verbs,
                "dates": dates,
                "token_count": len(doc),
                "sentence_count": len(list(doc.sents))
            }

        except Exception as e:
            # Fallback: basic regex extraction if spaCy fails
            numbers = re.findall(r'\d+\.?\d*', raw_answer)
            dates = re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', raw_answer)

            return {
                "entities": [],
                "numbers": numbers,
                "verbs": [],
                "dates": dates,
                "token_count": len(raw_answer.split()),
                "sentence_count": len(re.split(r'[.!?]+', raw_answer))
            }
