"""
Tests for Question Flow Engine

Covers:
- Question sequence loading
- Flow initiation and progression
- Answer submission and tracking
- Progress reporting
"""

import pytest
from life_brain.conversation.question_flow import (
    QuestionFlowEngine,
    QuestionType,
    Question,
    QuestionSequence,
)


class TestQuestionFlowEngine:
    """Tests for question flow engine."""

    def test_engine_initializes_with_sequences(self):
        """Test that engine loads sequences."""
        engine = QuestionFlowEngine()
        assert engine.sequences is not None
        assert len(engine.sequences) > 0

    def test_start_flow_with_valid_use_case(self):
        """Test starting a flow with valid use case."""
        engine = QuestionFlowEngine()
        question = engine.start_flow("C1")

        assert question is not None
        assert question.use_case_id == "C1"
        assert engine.current_state is not None
        assert engine.current_state.completed is False

    def test_start_flow_with_invalid_use_case(self):
        """Test that invalid use case returns None."""
        engine = QuestionFlowEngine()
        question = engine.start_flow("INVALID")
        assert question is None

    def test_get_first_question_context_setter(self):
        """Test that first question is context setter."""
        engine = QuestionFlowEngine()
        question = engine.start_flow("C1")

        assert question is not None
        assert question.question_type == QuestionType.CONTEXT_SETTER
        assert question.depth_level == 0

    def test_submit_answer_moves_to_next(self):
        """Test submitting answer moves to next question."""
        engine = QuestionFlowEngine()
        engine.start_flow("C1")

        first_q = engine.get_current_question()
        answer_text = "I'm preparing for coding interviews"

        next_q = engine.submit_answer(answer_text)

        # Should move to next question
        assert next_q is not None
        assert next_q != first_q
        assert first_q.question_id in engine.current_state.answers
        assert engine.current_state.answers[first_q.question_id] == answer_text

    def test_flow_completes_after_all_questions(self):
        """Test that flow completes when all questions answered."""
        engine = QuestionFlowEngine()
        engine.start_flow("C2")  # Has 3 questions

        # Answer all questions
        while True:
            q = engine.get_current_question()
            if q is None:
                break
            engine.submit_answer(f"Answer to {q.question_id}")

        assert engine.current_state.completed is True
        assert engine.get_current_question() is None

    def test_answers_are_stored(self):
        """Test that answers are properly stored."""
        engine = QuestionFlowEngine()
        engine.start_flow("C1")

        q1 = engine.get_current_question()
        answer1 = "Coding interviews for FAANG"
        engine.submit_answer(answer1)

        q2 = engine.get_current_question()
        answer2 = "I solved a problem using BFS"
        engine.submit_answer(answer2)

        assert engine.current_state.answers[q1.question_id] == answer1
        assert engine.current_state.answers[q2.question_id] == answer2

    def test_get_progress(self):
        """Test progress reporting."""
        engine = QuestionFlowEngine()
        engine.start_flow("C2")

        progress = engine.get_progress()
        assert "use_case_id" in progress
        assert progress["use_case_id"] == "C2"
        assert "current_question" in progress
        assert "total_questions" in progress
        assert progress["current_question"] == 1

        # Submit one answer
        engine.submit_answer("Some answer")
        progress = engine.get_progress()
        assert progress["current_question"] == 2

    def test_progress_percent_complete(self):
        """Test percent complete calculation."""
        engine = QuestionFlowEngine()
        engine.start_flow("C2")

        progress = engine.get_progress()
        total = progress["total_questions"]

        # At start, should be 1/3 = 33%
        assert progress["percent_complete"] == (1 / total) * 100

        # After first answer
        engine.submit_answer("Answer 1")
        progress = engine.get_progress()
        assert progress["percent_complete"] == (2 / total) * 100

    def test_get_flow_summary(self):
        """Test flow summary generation."""
        engine = QuestionFlowEngine()
        engine.start_flow("C2")

        # Answer all questions
        while True:
            q = engine.get_current_question()
            if q is None:
                break
            engine.submit_answer(f"Answer to {q.question_id}")

        summary = engine.get_flow_summary()
        assert summary is not None
        assert "Completed" in summary
        assert "Behavioral" in summary or "C2" in summary
        assert "Questions answered" in summary

    def test_get_summary_before_completion(self):
        """Test that summary is None before completion."""
        engine = QuestionFlowEngine()
        engine.start_flow("C1")

        summary = engine.get_flow_summary()
        assert summary is None

    def test_get_next_step(self):
        """Test next step suggestions."""
        engine = QuestionFlowEngine()
        engine.start_flow("C1")

        # Complete flow
        while engine.get_current_question() is not None:
            engine.submit_answer("Answer")

        next_step = engine.get_next_step()
        assert next_step is not None
        assert isinstance(next_step, str)
        assert len(next_step) > 0

    def test_multiple_use_cases(self):
        """Test starting different use cases."""
        engine = QuestionFlowEngine()

        # Start with C1
        engine.start_flow("C1")
        assert engine.current_state.use_case_id == "C1"

        # Switch to C2
        engine.start_flow("C2")
        assert engine.current_state.use_case_id == "C2"

        # Switch to R1
        engine.start_flow("R1")
        assert engine.current_state.use_case_id == "R1"

    def test_question_structure(self):
        """Test that questions have required fields."""
        engine = QuestionFlowEngine()
        engine.start_flow("C1")

        q = engine.get_current_question()
        assert q is not None
        assert q.question_id
        assert q.question_text
        assert q.question_type in QuestionType
        assert q.use_case_id == "C1"
        assert q.depth_level >= 0
        assert q.follow_up_triggers is not None
        assert q.expert_commentary

    def test_question_types_diversity(self):
        """Test that sequences include various question types."""
        engine = QuestionFlowEngine()
        engine.start_flow("C1")

        types_found = set()
        while True:
            q = engine.get_current_question()
            if q is None:
                break
            types_found.add(q.question_type)
            engine.submit_answer("Answer")

        # Should have multiple question types
        assert len(types_found) > 1
        assert QuestionType.CONTEXT_SETTER in types_found or QuestionType.MAIN_QUESTION in types_found

    def test_depth_levels_increase(self):
        """Test that questions generally increase in depth."""
        engine = QuestionFlowEngine()
        engine.start_flow("C1")

        depths = []
        while True:
            q = engine.get_current_question()
            if q is None:
                break
            depths.append(q.depth_level)
            engine.submit_answer("Answer")

        # First question should be shallowest
        assert depths[0] == 0


class TestQuestionSequences:
    """Tests for question sequences."""

    def test_c1_sequence_completeness(self):
        """Test that C1 has proper sequence."""
        engine = QuestionFlowEngine()
        sequence = engine.sequences.get("C1")

        assert sequence is not None
        assert sequence.use_case_id == "C1"
        assert len(sequence.questions) > 0
        assert sequence.estimated_duration_min > 0

    def test_c2_sequence_completeness(self):
        """Test that C2 has proper sequence."""
        engine = QuestionFlowEngine()
        sequence = engine.sequences.get("C2")

        assert sequence is not None
        assert sequence.use_case_id == "C2"
        assert "Behavioral" in sequence.title or "behavioral" in sequence.title

    def test_r1_sequence_relationships(self):
        """Test that R1 sequence is about relationships."""
        engine = QuestionFlowEngine()
        sequence = engine.sequences.get("R1")

        assert sequence is not None
        assert sequence.use_case_id == "R1"
        assert "Relationship" in sequence.title

    def test_f1_sequence_finance(self):
        """Test that F1 sequence is about finance."""
        engine = QuestionFlowEngine()
        sequence = engine.sequences.get("F1")

        assert sequence is not None
        assert sequence.use_case_id == "F1"
        assert "Invest" in sequence.title

    def test_all_sequences_have_questions(self):
        """Test that all sequences have questions."""
        engine = QuestionFlowEngine()

        for use_case_id, sequence in engine.sequences.items():
            assert len(sequence.questions) > 0, f"{use_case_id} has no questions"


class TestQuestionFlowIntegration:
    """Integration tests for question flow."""

    def test_end_to_end_interview_prep_flow(self):
        """Test complete interview prep flow."""
        engine = QuestionFlowEngine()

        # Start flow
        q1 = engine.start_flow("C1")
        assert q1 is not None
        assert "interview" in q1.question_text.lower() or "interview" in q1.expert_commentary.lower()

        # Get progress
        progress = engine.get_progress()
        assert progress["percent_complete"] == pytest.approx(25, abs=1)

        # Answer all questions
        answers = [
            "I'm preparing for system design interviews at Google",
            "I solved LeetCode problems on graphs and dynamic programming",
            "Binary search and tree problems trip me up",
            "I learned the importance of asking clarifying questions",
        ]

        for answer in answers:
            engine.submit_answer(answer)

        # Check completion
        assert engine.current_state.completed is True

        # Get summary
        summary = engine.get_flow_summary()
        assert summary is not None
        assert len(engine.current_state.answers) == len(answers)

    def test_end_to_end_relationships_flow(self):
        """Test complete relationships flow."""
        engine = QuestionFlowEngine()
        engine.start_flow("R1")

        # Complete the flow
        while engine.get_current_question() is not None:
            engine.submit_answer("Thoughtful answer about relationships")

        # Verify completion
        assert engine.current_state.completed is True
        summary = engine.get_flow_summary()
        assert "Completed" in summary
        assert "Relationships" in summary
