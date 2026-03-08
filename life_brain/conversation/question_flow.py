"""
Question Flow Engine — Deliver guided one-by-one Q&A sessions.

Orchestrates:
- Domain-specific question sequences
- Depth probing for incomplete answers
- Context-aware follow-ups
- Session progress tracking
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class QuestionType(str, Enum):
    """Types of questions in the flow."""
    CONTEXT_SETTER = "context_setter"      # Opens conversation, sets tone
    MAIN_QUESTION = "main_question"        # Core question for the topic
    DEPTH_PROBE = "depth_probe"            # Follow-up to understand more
    PERSPECTIVE_SHIFT = "perspective_shift"  # Different angle on same topic
    WRAP_UP = "wrap_up"                    # Closing reflection


@dataclass
class Question:
    """A single question in a conversation flow."""

    question_id: str                    # e.g., "C1_001", "R2_005"
    question_text: str                  # The actual question to ask
    question_type: QuestionType         # Type of question
    use_case_id: str                    # Which use case this belongs to
    depth_level: int                    # 0=surface, 1=medium, 2=deep
    follow_up_triggers: List[str]       # Keywords that trigger follow-ups
    follow_up_questions: List[str]      # Suggested follow-ups
    expert_commentary: str              # Advice from the assigned expert
    context: Optional[str] = None       # Optional context/setup


@dataclass
class QuestionSequence:
    """A sequence of questions for a use case."""

    use_case_id: str                    # e.g., "C1" (Interview Prep)
    title: str                          # e.g., "Interview Preparation"
    description: str                    # What this sequence helps with
    questions: List[Question] = field(default_factory=list)
    estimated_duration_min: int = 30    # Expected time
    difficulty: str = "intermediate"    # Difficulty level


@dataclass
class FlowState:
    """Current state of the question flow session."""

    use_case_id: str                    # Current use case
    sequence: QuestionSequence          # Question sequence being used
    current_question_index: int = 0     # Position in sequence
    answers: Dict[str, str] = field(default_factory=dict)  # question_id -> answer
    depth_levels: Dict[str, int] = field(default_factory=dict)  # question_id -> depth reached
    completed: bool = False             # Is flow complete?
    followups_used: int = 0             # How many follow-ups triggered


class QuestionFlowEngine:
    """Orchestrates guided question flows."""

    def __init__(self):
        """Initialize engine with question library."""
        self.sequences = self._build_sequences()
        self.current_state: Optional[FlowState] = None

    def _build_sequences(self) -> Dict[str, QuestionSequence]:
        """Build question sequences for each use case."""
        sequences = {}

        # === CAREER ===
        sequences["C1"] = QuestionSequence(
            use_case_id="C1",
            title="Interview Prep: Technical Interviews",
            description="Prepare for technical interviews with algorithm and system design practice",
            difficulty="intermediate",
            estimated_duration_min=45,
            questions=[
                Question(
                    question_id="C1_001",
                    question_text="What type of technical interviews are you preparing for? (Coding, system design, both?)",
                    question_type=QuestionType.CONTEXT_SETTER,
                    use_case_id="C1",
                    depth_level=0,
                    follow_up_triggers=["system design", "coding", "algorithm"],
                    follow_up_questions=[
                        "What companies are you targeting?",
                        "What's your current skill level with coding?",
                    ],
                    expert_commentary="Understanding the interview type helps Satya tailor preparation. Be specific about what you're targeting.",
                ),
                Question(
                    question_id="C1_002",
                    question_text="Tell me about a recent challenging problem you solved. Walk me through your thinking.",
                    question_type=QuestionType.MAIN_QUESTION,
                    use_case_id="C1",
                    depth_level=1,
                    follow_up_triggers=["stuck", "tried", "error", "approach"],
                    follow_up_questions=[
                        "What would you do differently if you solved it again?",
                        "How did you verify your solution was correct?",
                        "What was the key insight that made it click?",
                    ],
                    expert_commentary="Great interviews aren't about perfect solutions. They're about your thinking process. Show how you break down problems.",
                ),
                Question(
                    question_id="C1_003",
                    question_text="What's one algorithm or data structure that always trips you up?",
                    question_type=QuestionType.DEPTH_PROBE,
                    use_case_id="C1",
                    depth_level=2,
                    follow_up_triggers=["graphs", "trees", "dynamic", "hash"],
                    follow_up_questions=[
                        "Why do you think that one is tricky for you?",
                        "When would you use it in a real system?",
                    ],
                    expert_commentary="Interviewers often probe weak areas. Own them. Show learning ability, not perfection.",
                ),
                Question(
                    question_id="C1_004",
                    question_text="What have you learned from your interview prep so far?",
                    question_type=QuestionType.WRAP_UP,
                    use_case_id="C1",
                    depth_level=0,
                    follow_up_triggers=[],
                    follow_up_questions=[],
                    expert_commentary="Reflection is how learning sticks. Take a moment to notice progress.",
                ),
            ],
        )

        sequences["C2"] = QuestionSequence(
            use_case_id="C2",
            title="Interview Prep: Behavioral Questions",
            description="Master behavioral interview questions using STAR method",
            difficulty="beginner",
            estimated_duration_min=30,
            questions=[
                Question(
                    question_id="C2_001",
                    question_text="Think of a time when you had to deal with a difficult team member or conflict. What happened?",
                    question_type=QuestionType.MAIN_QUESTION,
                    use_case_id="C2",
                    depth_level=1,
                    follow_up_triggers=["disagreement", "conflict", "resolved"],
                    follow_up_questions=[
                        "What was your role in resolving it?",
                        "What did you learn from that situation?",
                    ],
                    expert_commentary="STAR Method: Situation, Task, Action, Result. Walk through all four clearly.",
                ),
                Question(
                    question_id="C2_002",
                    question_text="Tell me about a time you failed or made a mistake. How did you handle it?",
                    question_type=QuestionType.MAIN_QUESTION,
                    use_case_id="C2",
                    depth_level=1,
                    follow_up_triggers=["learned", "fixed", "mistake"],
                    follow_up_questions=[
                        "How would you prevent that mistake in the future?",
                    ],
                    expert_commentary="Failure questions are opportunities. Show self-awareness and growth mindset.",
                ),
                Question(
                    question_id="C2_003",
                    question_text="What's one achievement you're genuinely proud of? Why does it matter to you?",
                    question_type=QuestionType.WRAP_UP,
                    use_case_id="C2",
                    depth_level=0,
                    follow_up_triggers=[],
                    follow_up_questions=[],
                    expert_commentary="Own your achievements. Show impact, not just effort.",
                ),
            ],
        )

        # === RELATIONSHIPS ===
        sequences["R1"] = QuestionSequence(
            use_case_id="R1",
            title="Relationships: Deep Connections",
            description="Build meaningful connections through vulnerability and authenticity",
            difficulty="beginner",
            estimated_duration_min=35,
            questions=[
                Question(
                    question_id="R1_001",
                    question_text="Who is someone you feel truly understood by? What makes that connection special?",
                    question_type=QuestionType.CONTEXT_SETTER,
                    use_case_id="R1",
                    depth_level=0,
                    follow_up_triggers=["listen", "understand", "open"],
                    follow_up_questions=[
                        "What do you share with them that you don't with others?",
                    ],
                    expert_commentary="Connection happens through vulnerability. Safe people allow us to be fully ourselves.",
                ),
                Question(
                    question_id="R1_002",
                    question_text="What's something you've been hesitant to share with someone close to you?",
                    question_type=QuestionType.DEPTH_PROBE,
                    use_case_id="R1",
                    depth_level=2,
                    follow_up_triggers=["afraid", "judge", "shame"],
                    follow_up_questions=[
                        "What are you worried might happen if you shared it?",
                        "Who would be safe to share with?",
                    ],
                    expert_commentary="Shame thrives in secrecy. Shared shame loses power. Find one person to trust.",
                ),
                Question(
                    question_id="R1_003",
                    question_text="How will you deepen one relationship this week?",
                    question_type=QuestionType.WRAP_UP,
                    use_case_id="R1",
                    depth_level=0,
                    follow_up_triggers=[],
                    follow_up_questions=[],
                    expert_commentary="Connection requires action. What's one small step you can take?",
                ),
            ],
        )

        # === FINANCE ===
        sequences["F1"] = QuestionSequence(
            use_case_id="F1",
            title="Investing Basics: Building Wealth",
            description="Start investing and build long-term wealth through compound growth",
            difficulty="intermediate",
            estimated_duration_min=50,
            questions=[
                Question(
                    question_id="F1_001",
                    question_text="What's your investment goal? When do you need this money?",
                    question_type=QuestionType.CONTEXT_SETTER,
                    use_case_id="F1",
                    depth_level=0,
                    follow_up_triggers=["years", "retirement", "home"],
                    follow_up_questions=[
                        "How much are you planning to invest monthly?",
                    ],
                    expert_commentary="Time horizon drives strategy. Longer horizon = more risk tolerance.",
                ),
                Question(
                    question_id="F1_002",
                    question_text="What do you currently know about index funds vs. individual stocks?",
                    question_type=QuestionType.MAIN_QUESTION,
                    use_case_id="F1",
                    depth_level=1,
                    follow_up_triggers=["index", "diversified", "etf"],
                    follow_up_questions=[
                        "Why do you think indexing makes sense for most people?",
                    ],
                    expert_commentary="Start simple: low-cost index funds. Avoid picking individual stocks unless it's your profession.",
                ),
                Question(
                    question_id="F1_003",
                    question_text="What's your first step this month?",
                    question_type=QuestionType.WRAP_UP,
                    use_case_id="F1",
                    depth_level=0,
                    follow_up_triggers=[],
                    follow_up_questions=[],
                    expert_commentary="The best investment is the one you actually make. Small action beats perfect planning.",
                ),
            ],
        )

        return sequences

    def start_flow(self, use_case_id: str) -> Optional[Question]:
        """
        Start a new question flow for a use case.

        Returns first question if successful, None if use case not found.
        """
        if use_case_id not in self.sequences:
            return None

        sequence = self.sequences[use_case_id]
        self.current_state = FlowState(
            use_case_id=use_case_id,
            sequence=sequence,
        )

        return self.get_current_question()

    def get_current_question(self) -> Optional[Question]:
        """Get the current question in the flow."""
        if not self.current_state:
            return None

        if self.current_state.current_question_index >= len(self.current_state.sequence.questions):
            self.current_state.completed = True
            return None

        return self.current_state.sequence.questions[self.current_state.current_question_index]

    def submit_answer(self, answer_text: str) -> Optional[Question]:
        """
        Submit answer to current question and move to next.

        Returns next question, or None if flow complete.
        """
        if not self.current_state:
            return None

        current_q = self.get_current_question()
        if not current_q:
            return None

        # Store answer
        self.current_state.answers[current_q.question_id] = answer_text
        self.current_state.depth_levels[current_q.question_id] = current_q.depth_level

        # Move to next question
        self.current_state.current_question_index += 1

        return self.get_current_question()

    def get_progress(self) -> dict:
        """Get progress information for current flow."""
        if not self.current_state:
            return {}

        total = len(self.current_state.sequence.questions)
        current = self.current_state.current_question_index + 1

        return {
            "use_case_id": self.current_state.use_case_id,
            "use_case_title": self.current_state.sequence.title,
            "current_question": current,
            "total_questions": total,
            "percent_complete": (current / total) * 100,
            "time_estimate_min": self.current_state.sequence.estimated_duration_min,
        }

    def get_flow_summary(self) -> Optional[str]:
        """Get summary of completed flow."""
        if not self.current_state or not self.current_state.completed:
            return None

        summary_lines = [
            f"\n✅ Completed: {self.current_state.sequence.title}",
            f"Questions answered: {len(self.current_state.answers)}/{len(self.current_state.sequence.questions)}",
            f"\n📝 Summary of responses:",
        ]

        for q in self.current_state.sequence.questions:
            if q.question_id in self.current_state.answers:
                summary_lines.append(f"\nQ: {q.question_text}")
                answer = self.current_state.answers[q.question_id]
                # Truncate long answers
                if len(answer) > 150:
                    answer = answer[:150] + "..."
                summary_lines.append(f"A: {answer}")

        return "\n".join(summary_lines)

    def get_next_step(self) -> Optional[str]:
        """Get suggested next action after flow completion."""
        if not self.current_state or not self.current_state.completed:
            return None

        use_case_id = self.current_state.use_case_id

        # Suggest next steps based on use case
        next_steps = {
            "C1": "Now practice with actual coding problems. Try LeetCode or HackerRank.",
            "C2": "Record yourself answering these questions. Watch back and refine your storytelling.",
            "R1": "This week, reach out to one person and share something vulnerable. Notice how it feels.",
            "F1": "Open your brokerage account this week. Start with your first investment, no matter how small.",
        }

        return next_steps.get(use_case_id, "Great work! Keep reflecting and learning.")
