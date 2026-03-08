"""
Conversation Flows — Main conversation path implementations.

Implements:
- small_talk_flow(): Free-form conversation with passive capture
- guided_flow(): Structured conversation with expert guidance
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from dataclasses import dataclass, field

from life_brain.conversation.mode_gate import IntentDetector
from life_brain.conversation.experts import get_expert
from life_brain.conversation.use_cases import get_use_case

logger = logging.getLogger(__name__)


@dataclass
class FlowState:
    """State maintained during a conversation flow."""
    mode: str  # "small_talk" or "guided"
    messages: List[Dict[str, str]] = field(default_factory=list)
    current_use_case_id: Optional[str] = None
    current_expert: Optional[str] = None
    captured_nuggets: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.6  # Confidence for captured info
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_activity_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())





def small_talk_flow(
    user_message: str,
    detector: Optional[IntentDetector] = None,
    state: Optional[FlowState] = None
) -> Dict[str, Any]:
    """
    Free-form casual conversation with passive capture.

    Flow:
    1. User sends casual message
    2. System responds conversationally
    3. Passively extract information (confidence: 0.6)
    4. Suggest expert if intent detected (once per session)
    5. Continue conversation or offer structured mode

    Args:
        user_message: User's message
        detector: Optional existing IntentDetector (for session continuity)
        state: Optional FlowState (for multi-turn continuity)

    Returns:
        Dict with:
        - system_message: Response to user
        - next_action: What happens next
        - captured_nuggets: Any passively captured information
        - expert_suggestion: Expert introduction (if appropriate)
        - state: Updated FlowState for next turn
    """
    if detector is None:
        detector = IntentDetector()

    if state is None:
        state = FlowState(mode="small_talk")

    # Update state
    state.messages.append({"role": "user", "content": user_message})
    state.last_activity_at = datetime.utcnow().isoformat()

    # Step 1: Detect intent even in small talk
    use_case_id, confidence = detector.detect_intent(user_message)
    logger.debug(f"Intent detected in small talk: {use_case_id} (confidence: {confidence})")

    result = {
        "mode": "small_talk",
        "system_message": None,
        "next_action": "continue_small_talk",
        "captured_nuggets": [],
        "expert_suggestion": None,
        "state": state,
    }

    # Step 2: Suggest expert if high confidence and not suggested yet
    if use_case_id and detector.should_suggest_expert(confidence):
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
                result["system_message"] = expert_intro
                result["next_action"] = "suggest_expert"
                detector.mark_expert_suggested()
                state.current_use_case_id = use_case_id
                logger.info(f"Expert suggestion in small talk: {expert_name}")
                return result

    # Step 3: Passive capture (simplified - would use ML extraction in production)
    # For now, just log the message as potential nugget
    if len(user_message) > 20:
        captured = {
            "raw_text": user_message,
            "confidence": 0.6,  # Small talk confidence
            "source": "small_talk_passive",
            "timestamp": datetime.utcnow().isoformat()
        }
        state.captured_nuggets.append(captured)
        logger.debug(f"Passively captured: {user_message[:50]}... (confidence: 0.6)")

    # Step 4: Respond conversationally
    response = f"Haan, suna. {user_message[:30]}{'...' if len(user_message) > 30 else ''}. Aur batao — kya chal raha hai?"

    result["system_message"] = response
    result["captured_nuggets"] = state.captured_nuggets

    logger.info(f"Small talk flow: continuing conversation")
    return result


def guided_flow(
    use_case_id: str,
    expert_name: Optional[str] = None,
    state: Optional[FlowState] = None
) -> Dict[str, Any]:
    """
    Structured conversation with expert guidance.

    Flow:
    1. User selects or system suggests use case
    2. Expert introduced (or system acts as guide)
    3. One-by-one guided questions asked
    4. User answers extracted as high-confidence (0.9) Q&A pairs
    5. Validate with MECE + conflict checks
    6. After 3-5 questions, offer to wrap or continue

    Args:
        use_case_id: ID of selected use case (e.g., "C1")
        expert_name: Optional expert to guide (if None, system acts as guide)
        state: Optional FlowState for multi-turn continuity

    Returns:
        Dict with:
        - system_message: First question or expert intro
        - next_action: Expect answer or proceed
        - current_use_case: Use case details
        - current_expert: Expert details
        - state: Updated FlowState
    """
    if state is None:
        state = FlowState(mode="guided")

    state.current_use_case_id = use_case_id
    state.current_expert = expert_name

    use_case = get_use_case(use_case_id)
    if not use_case:
        raise ValueError(f"Unknown use case: {use_case_id}")

    result = {
        "mode": "guided",
        "system_message": None,
        "next_action": "expect_answer",
        "current_use_case": use_case,
        "current_expert": None,
        "state": state,
    }

    # Load expert if specified, otherwise use default from use case
    if expert_name is None and use_case.get("expert"):
        expert_name = use_case.get("expert")

    expert = None
    if expert_name:
        expert = get_expert(expert_name)
        result["current_expert"] = expert

    logger.info(f"Starting guided flow: use_case={use_case_id}, expert={expert_name}")

    # Prepare opening message
    use_case_title = use_case.get("title", "Structured conversation")

    if expert:
        opening = f"""Bilkul! Main tumhe {expert.get('real_name')} se milwata hun.

{expert.get('opener')}"""
    else:
        opening = f"Chaliye, {use_case_title} par samajhte hain.\n\nShuru karte hain:"

    # Start with first question
    questions = use_case.get("questions", [])
    if questions:
        first_question = questions[0] if isinstance(questions, list) else questions
        opening += f"\n\n{first_question}"
        state.messages.append({"role": "system", "content": first_question})

    result["system_message"] = opening
    state.last_activity_at = datetime.utcnow().isoformat()

    return result


def process_guided_answer(
    user_answer: str,
    state: FlowState,
    expert_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process user's answer in guided flow.

    Args:
        user_answer: User's answer to current question
        state: Current FlowState
        expert_name: Expert guiding conversation

    Returns:
        Dict with:
        - system_message: Expert's response / next question
        - extracted_qa: Q&A pair extracted from answer
        - next_action: Continue or wrap-up
        - state: Updated state
    """
    if state.mode != "guided":
        raise ValueError("process_guided_answer only works in guided mode")

    # Log the answer
    state.messages.append({"role": "user", "content": user_answer})
    state.last_activity_at = datetime.utcnow().isoformat()

    result = {
        "system_message": None,
        "extracted_qa": None,
        "next_action": "continue",
        "state": state,
    }

    # In production, this would:
    # 1. Extract Q&A pair from answer
    # 2. Run MECE validation
    # 3. Check for conflicts
    # 4. Store to ChromaDB

    # For now, just acknowledge and ask next question
    expert = None
    if expert_name:
        expert = get_expert(expert_name)

    if expert:
        response = f"{expert.get('depth_trigger', 'Interesting.')} \n\nAur batao — kya aur?"
    else:
        response = "Theek hai. Aur kya aur detail de sakte ho?"

    result["system_message"] = response
    logger.debug(f"Processed guided answer: {user_answer[:50]}...")

    return result


def wrap_up_flow(state: FlowState) -> Dict[str, Any]:
    """
    Wrap up a flow and prepare for exit or transition.

    Args:
        state: Current FlowState

    Returns:
        Dict with:
        - summary: Summary of captured information
        - next_action: End or switch mode
        - state: Final state
    """
    result = {
        "summary": None,
        "next_action": "end",
        "state": state,
    }

    if state.mode == "small_talk":
        summary = f"Captured {len(state.captured_nuggets)} pieces of information. Kya tum chahte ho ke detailed recording karein?"
    else:
        summary = f"Extracted {len(state.captured_nuggets)} Q&A pairs from {state.current_use_case_id}. Process ho gaya!"

    result["summary"] = summary
    logger.info(f"Flow wrapped up: {state.mode} mode, {len(state.captured_nuggets)} captures")

    return result
