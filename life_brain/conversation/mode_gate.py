"""
Mode Gate — Detect whether user wants small talk or guided structured conversation.

Also: Intent detection to proactively suggest experts even in small talk.
"""

from typing import Optional, Tuple, Dict, Any
from enum import Enum
from anthropic import Anthropic
import logging

logger = logging.getLogger(__name__)


class Mode(str, Enum):
    SMALL_TALK = "small_talk"
    GUIDED = "guided"


class IntentDetector:
    """Detects user intent and suggests relevant experts."""

    def __init__(self):
        self.client = Anthropic()
        self.expert_suggested_in_session = False  # Track if we've already suggested an expert

    def detect_mode(self, user_message: str) -> Mode:
        """
        Detect if user wants small talk or structured guidance.

        Logic:
          - If message has strong keywords (interview, salary, relationship, health)
            → suggest use case directly (GUIDED implicit)
          - Else → ask user to choose [A] Bas baatein [B] Kuch record karna

        Args:
            user_message: User's opening message

        Returns:
            Mode.SMALL_TALK or Mode.GUIDED
        """
        domain, confidence = detect_keywords_simple(user_message)
        if confidence > 0.7:
            return Mode.GUIDED
        else:
            return Mode.SMALL_TALK

    def detect_intent(self, small_talk_message: str) -> Tuple[Optional[str], float]:
        """
        Detect use case from small talk (even casual messages).

        Args:
            small_talk_message: User's casual message

        Returns:
            Tuple of (use_case_id, confidence) or (None, 0.0) if no match
        """
        from life_brain.conversation.use_cases import find_use_cases_by_keywords, get_use_case

        # Extract keywords from message
        words = small_talk_message.lower().split()

        # Find matching use cases
        matching_uc_ids = find_use_cases_by_keywords(words)

        if not matching_uc_ids:
            logger.debug(f"No use cases matched for message: {small_talk_message}")
            return (None, 0.0)

        # Use Claude to rank top 3 candidates by semantic relevance
        try:
            candidates = [get_use_case(uc_id) for uc_id in matching_uc_ids[:5]]
            candidates = [c for c in candidates if c]  # Filter out None

            if not candidates:
                return (None, 0.0)

            # Single top candidate
            if len(candidates) == 1:
                confidence = 0.8
                logger.debug(f"Single use case match: {candidates[0]['id']} (confidence: {confidence})")
                return (candidates[0]['id'], confidence)

            # Multiple candidates - use Claude to rank
            candidate_descriptions = "\n".join([
                f"{i+1}. [{c['id']}] {c['title']} — {c['description'][:100]}"
                for i, c in enumerate(candidates)
            ])

            prompt = f"""Given this user message, which use case is most relevant?

User message: "{small_talk_message}"

Candidates:
{candidate_descriptions}

Respond with ONLY the use case ID (e.g., "C1") of the best match. If none are relevant, respond "NONE"."""

            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )

            best_uc_id = response.content[0].text.strip()

            if best_uc_id == "NONE":
                return (None, 0.0)

            # Validate it's a valid ID from our candidates
            valid_ids = {c['id'] for c in candidates}
            if best_uc_id not in valid_ids:
                logger.warning(f"Claude returned invalid ID: {best_uc_id}")
                # Fallback to first candidate
                best_uc_id = candidates[0]['id']

            confidence = 0.75  # Medium-high confidence from LLM
            logger.debug(f"LLM matched use case: {best_uc_id} (confidence: {confidence})")
            return (best_uc_id, confidence)

        except Exception as e:
            logger.error(f"Error in detect_intent: {e}")
            # Fallback: return first match with lower confidence
            if matching_uc_ids:
                return (matching_uc_ids[0], 0.5)
            return (None, 0.0)

    def should_suggest_expert(self, intent_confidence: float) -> bool:
        """
        Determine if we should suggest an expert.

        Args:
            intent_confidence: Confidence score from detect_intent

        Returns:
            True if should suggest (confidence > 0.7 and not suggested before)
        """
        # Only suggest once per session
        if self.expert_suggested_in_session:
            logger.debug("Expert already suggested in this session, skipping")
            return False

        # Only suggest if confidence is high enough
        if intent_confidence < 0.7:
            logger.debug(f"Intent confidence {intent_confidence} below threshold 0.7")
            return False

        logger.debug(f"Should suggest expert: confidence={intent_confidence}")
        return True

    def mark_expert_suggested(self) -> None:
        """Mark that we've suggested an expert in this session."""
        self.expert_suggested_in_session = True
        logger.debug("Marked expert as suggested in this session")

    def format_mode_prompt(self) -> str:
        """
        Format the mode selection prompt for user.

        Returns:
            Hinglish prompt: "Kya chal raha hai? [A] Bas baatein [B] Kuch record karna"
        """
        return """
Kya chal raha hai?

[A] Bas baatein (Free talk — passive capture, confidence: 0.6)
[B] Kuch record karna (Guided — structured with expert)

Select A or B:
        """.strip()


def detect_keywords_simple(message: str) -> Tuple[str, float]:
    """
    Simple keyword-based intent detection (fallback).

    Returns:
        Tuple of (domain, confidence)
    """
    msg_lower = message.lower()

    # Domain keywords (domain -> keywords list)
    keywords_map = {
        "career": ["interview", "job", "role", "position", "project", "promotion", "boss", "manager", "work", "salary", "offer", "raise", "skill"],
        "relationships": ["friend", "boyfriend", "girlfriend", "wife", "husband", "partner", "conflict", "breakup", "family", "relationship"],
        "health": ["health", "fitness", "sleep", "diet", "anxiety", "stress", "energy", "mental", "exercise", "wellness"],
        "finance": ["money", "investment", "budget", "loan", "spend", "save", "financial", "expense", "income"],
        "goals": ["goal", "dream", "plan", "achieve", "ambition", "target"],
        "personal_growth": ["learn", "grow", "improve", "change", "habit", "skill", "strength", "weakness"],
    }

    # Score each domain
    scores = {}
    for domain, keywords in keywords_map.items():
        matches = sum(1 for kw in keywords if kw in msg_lower)
        scores[domain] = matches

    # Get top domain
    if sum(scores.values()) == 0:
        return ("none", 0.0)  # No keywords found

    top_domain = max(scores, key=scores.get)
    max_matches = scores[top_domain]
    total_keywords = sum(len(kws) for kws in keywords_map.values())

    # Confidence: max_matches / total_keywords (or 0.7+ if strong match)
    confidence = max_matches / 10.0  # Heuristic: 3+ matches → 0.3+, 7+ → 0.7+
    confidence = min(confidence, 1.0)

    return (top_domain, confidence)


def conversation_entry(
    user_message: str,
    detector: Optional[IntentDetector] = None
) -> Dict[str, Any]:
    """
    Main entry point for conversation.

    Flow:
    1. Create IntentDetector if not provided
    2. Detect mode (GUIDED if keywords, else ask)
    3. If GUIDED: suggest top use case
    4. If SMALL_TALK: detect intent, suggest expert if confidence > 0.7

    Args:
        user_message: User's initial message
        detector: Optional existing IntentDetector instance (for session continuity)

    Returns:
        Dict with:
        - mode: Mode.SMALL_TALK or Mode.GUIDED
        - use_case_id: Matched use case ID (if any)
        - use_case_confidence: Confidence score
        - expert_suggestion: Expert intro prompt (if suggested)
        - next_action: What system should do next
        - system_message: Response to show user
    """
    if detector is None:
        detector = IntentDetector()

    # Step 1: Detect mode
    mode = detector.detect_mode(user_message)
    logger.info(f"Detected mode: {mode} for message: {user_message[:50]}...")

    result = {
        "mode": mode,
        "use_case_id": None,
        "use_case_confidence": 0.0,
        "expert_suggestion": None,
        "next_action": None,
        "system_message": None,
        "detector": detector,  # Return detector for session continuity
    }

    if mode == Mode.GUIDED:
        # Step 2a: User is ready for structured conversation
        # Use semantic matching to show top use cases
        from life_brain.conversation.semantic_matcher import SemanticMatcher

        matcher = SemanticMatcher()
        matches = matcher.get_top_matches(user_message, top_n=10, min_score=0.0)

        if matches:
            use_case_display = matcher.format_top_10_display(matches)
            result["next_action"] = "show_top_use_cases"
            result["system_message"] = f"Samjha! Tujhe structured guidance chahiye. Neeche dekh — kya relevant lag raha hai?\n\n{use_case_display}"
            result["top_matches"] = [(uid, uc) for uid, uc, score in matches]
        else:
            full_catalog = matcher.format_full_catalog()
            result["next_action"] = "show_full_catalog"
            result["system_message"] = f"Samjha! Kaunsa topic choose karna chahoge?\n\n{full_catalog}"

        logger.debug(f"Guided mode: showing {len(matches) if matches else 'full'} use cases")
        return result

    # Step 2b: Small talk mode - detect intent
    use_case_id, confidence = detector.detect_intent(user_message)
    result["use_case_id"] = use_case_id
    result["use_case_confidence"] = confidence

    if use_case_id and detector.should_suggest_expert(confidence):
        # Step 3: Suggest expert
        from life_brain.conversation.use_cases import get_use_case
        from life_brain.conversation.experts import get_expert

        use_case = get_use_case(use_case_id)
        if use_case:
            expert_name = use_case.get("expert")
            expert = get_expert(expert_name)

            if expert:
                expert_intro = f"""Sunta hun. Lagta hai {expert.get('real_name', expert_name)} ({expert.get('role')})
is baare mein kafi helpful ho sakte hain.

"{expert.get('opener')}"

Kya main unhe introduce karun?"""

                result["expert_suggestion"] = expert_intro
                result["next_action"] = "suggest_expert"
                result["system_message"] = expert_intro
                detector.mark_expert_suggested()
                logger.info(f"Suggesting expert: {expert_name}")
                return result

    # Step 4: Continue with small talk (no high-confidence use case found)
    result["next_action"] = "continue_small_talk"
    result["system_message"] = "Haan, suna. Aur batao — kya chal raha hai?"
    logger.debug("Small talk mode: continuing conversation without expert suggestion")
    return result
