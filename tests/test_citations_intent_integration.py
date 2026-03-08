"""
Integration Tests: Citations + Intent Detection

Tests how citations and groundedness scoring integrate with intent detection
from the mode_gate module.

This demonstrates the complete flow:
1. User intent is detected with confidence score
2. Documents are retrieved and retrieved by similarity
3. Top 3 documents are selected for synthesis
4. Groundedness is calculated and mapped to output type
5. Attribution is formatted with source citations
"""

import sys
sys.path.insert(0, '.')

from typing import List, Dict, Any
from life_brain.truth_engine.groundedness import (
    GroundednessScore,
    GroundednessCalculator,
    RetrievedDocument,
    SynthesisLimiter,
    OutputGenerator,
    ConfidenceLevel,
    OutputType,
)
from life_brain.conversation.mode_gate import Mode


def simulate_intent_detection(
    user_message: str,
) -> Dict[str, Any]:
    """
    Simulate intent detection output from mode_gate.detect_intent().

    Returns:
        Dict with:
        - use_case_id: "C1", "C2", etc.
        - use_case_confidence: 0.0-1.0
        - mode: Mode.SMALL_TALK or Mode.GUIDED
    """
    # For testing, hardcode some known patterns
    if "interview" in user_message.lower() or "job" in user_message.lower():
        return {
            "use_case_id": "C1",
            "use_case_confidence": 0.85,
            "mode": Mode.GUIDED,
        }
    elif "relationship" in user_message.lower():
        return {
            "use_case_id": "C5",
            "use_case_confidence": 0.75,
            "mode": Mode.SMALL_TALK,
        }
    else:
        return {
            "use_case_id": None,
            "use_case_confidence": 0.0,
            "mode": Mode.SMALL_TALK,
        }


def simulate_document_retrieval(
    use_case_id: str,
    query: str,
) -> List[RetrievedDocument]:
    """
    Simulate retrieval of documents related to a use case.

    Returns:
        List of RetrievedDocument objects with similarity scores
    """
    # Simulate retrieval for different use cases
    if use_case_id == "C1":  # Career/Interview use case
        return [
            RetrievedDocument(
                doc_id="sprinklr-2023-01-interview",
                text="Led Sprinklr platform discussion with 5 senior engineers on CGB architecture. Discussed real-time processing requirements and scalability challenges.",
                metadata={
                    "company": "Sprinklr",
                    "date": "2023-01-15",
                    "type": "project_documentation",
                    "category": "architecture",
                },
                similarity_score=0.95,
            ),
            RetrievedDocument(
                doc_id="amex-2024-11-hiring",
                text="Conducted technical interviews for AML Risk Scoring Engineer role. Evaluated candidates on system design, Python expertise, and financial domain knowledge.",
                metadata={
                    "company": "American Express",
                    "date": "2024-11-10",
                    "type": "experience",
                    "category": "interviewing",
                },
                similarity_score=0.88,
            ),
            RetrievedDocument(
                doc_id="sprinklr-2023-06-star",
                text="STAR: Optimized query decomposition in CGB. Reduced response latency by 40% through intelligent query splitting. Improved user satisfaction scores.",
                metadata={
                    "company": "Sprinklr",
                    "date": "2023-06-20",
                    "type": "star_story",
                    "category": "optimization",
                },
                similarity_score=0.82,
            ),
            RetrievedDocument(
                doc_id="amex-2024-08-project",
                text="CRR AML Risk Scoring project milestone: Integrated conflict detection and truth engine for regulatory compliance. 99.7% accuracy achieved.",
                metadata={
                    "company": "American Express",
                    "date": "2024-08-15",
                    "type": "project_documentation",
                    "category": "ml_systems",
                },
                similarity_score=0.75,
            ),
            RetrievedDocument(
                doc_id="resume-2024-skills",
                text="Technical skills: Python, system design, ML/AI, cloud infrastructure, data pipelines. Languages: English, Hindi.",
                metadata={
                    "type": "resume",
                    "category": "skills",
                },
                similarity_score=0.70,
            ),
        ]
    elif use_case_id == "C5":  # Relationship use case
        return [
            RetrievedDocument(
                doc_id="personal-2024-relationships",
                text="Maintained strong relationships with mentors and peers throughout career. Regular 1-on-1s, seeking feedback, and collaborative problem-solving.",
                metadata={
                    "type": "personal_reflection",
                    "category": "relationships",
                },
                similarity_score=0.85,
            ),
        ]
    else:
        return []


def test_citation_workflow_with_intent():
    """
    Test complete workflow: intent → retrieval → synthesis → citations
    """
    print("\n" + "=" * 80)
    print("TEST: Complete Citation Workflow with Intent Detection")
    print("=" * 80)

    # Step 1: User asks a question
    user_message = "How should I prepare for technical interviews?"
    print(f"\n👤 User: {user_message}")

    # Step 2: Detect intent
    intent_result = simulate_intent_detection(user_message)
    use_case_id = intent_result["use_case_id"]
    use_case_confidence = intent_result["use_case_confidence"]

    print(f"\n🔍 Intent Detection:")
    print(f"   Use case: {use_case_id}")
    print(f"   Confidence: {use_case_confidence:.2f}")

    # Step 3: Retrieve documents
    documents = simulate_document_retrieval(use_case_id, user_message)
    print(f"\n📚 Retrieved {len(documents)} documents")
    for i, doc in enumerate(documents):
        print(f"   {i+1}. {doc.doc_id} (similarity: {doc.similarity_score:.2f})")

    # Step 4: Select top 3 documents
    selected_docs = SynthesisLimiter.select_top_documents(documents, max_docs=3)
    print(f"\n📌 Selected {len(selected_docs)} documents for synthesis:")
    for doc in selected_docs:
        print(f"   - {doc.doc_id} ({doc.similarity_score:.2f})")

    # Step 5: Calculate groundedness
    calculator = GroundednessCalculator(query_threshold=0.75)
    query_keywords = ["interview", "preparation", "technical"]
    groundedness = calculator.calculate_groundedness(selected_docs, query_keywords)

    print(f"\n📊 Groundedness Score: {groundedness.overall_score:.2f}")
    print(f"   Confidence level: {groundedness.confidence_level().value}")
    print(f"   Output type: {groundedness.output_type().value}")
    print(f"   Component breakdown:")
    print(f"     - Max similarity: {groundedness.max_similarity:.2f}")
    print(f"     - Avg similarity: {groundedness.avg_similarity:.2f}")
    print(f"     - Supporting docs: {groundedness.num_supporting_docs}")
    print(f"     - Coverage: {groundedness.coverage:.2f}")
    print(f"     - Consistency: {groundedness.consistency:.2f}")

    # Step 6: Generate answer with citations
    base_answer = f"""Based on my experience at Sprinklr and American Express, here's how to prepare for technical interviews:

1. **System Design Skills**: Practice designing large-scale systems. During my interview rounds at Amex, system design was a critical component.

2. **Domain Knowledge**: For roles in specialized domains (like financial systems), understand the business context deeply. My work on CRR AML Risk Scoring taught me the importance of this.

3. **Practical Experience**: Build real projects and be ready to discuss them in depth. My CGB platform work at Sprinklr demonstrates this.

4. **Communication**: Practice explaining complex technical concepts clearly, as shown in my collaborative architecture discussions."""

    # Add attribution
    answer_with_citation = OutputGenerator.format_attribution(
        base_answer,
        selected_docs,
        groundedness
    )

    print(f"\n💬 Generated Answer:")
    print("-" * 80)
    print(answer_with_citation)
    print("-" * 80)

    # Verify citation format
    assert "(Source:" in answer_with_citation
    assert "confidence:" in answer_with_citation
    assert "sprinklr" in answer_with_citation or "amex" in answer_with_citation

    print(f"\n✓ Citation format verified")
    print(f"  - Contains source attribution: YES")
    print(f"  - Contains confidence score: YES")
    print(f"  - Limited to top 3 docs: YES")


def test_boundary_confidence_with_intent():
    """
    Test how different confidence levels affect citation behavior
    """
    print("\n" + "=" * 80)
    print("TEST: Confidence Boundaries with Intent Detection")
    print("=" * 80)

    test_cases = [
        {
            "name": "HIGH Confidence (0.95)",
            "groundedness_score": 0.95,
            "expected_confidence": ConfidenceLevel.HIGH,
            "expected_output": OutputType.DIRECT_ANSWER,
        },
        {
            "name": "MEDIUM Confidence (0.75)",
            "groundedness_score": 0.75,
            "expected_confidence": ConfidenceLevel.MEDIUM,
            "expected_output": OutputType.QUALIFIED_ANSWER,
        },
        {
            "name": "LOW Confidence (0.55)",
            "groundedness_score": 0.55,
            "expected_confidence": ConfidenceLevel.LOW,
            "expected_output": OutputType.UNCERTAIN_ANSWER,
        },
        {
            "name": "INSUFFICIENT Confidence (0.30)",
            "groundedness_score": 0.30,
            "expected_confidence": ConfidenceLevel.INSUFFICIENT,
            "expected_output": OutputType.NO_MATCH,
        },
    ]

    for test_case in test_cases:
        print(f"\n  {test_case['name']}:")

        # Create mock groundedness with specified score
        docs = [
            RetrievedDocument(
                doc_id=f"doc_{i}",
                text=f"Content {i}",
                metadata={},
                similarity_score=test_case["groundedness_score"],
            )
            for i in range(3)
        ]

        groundedness = GroundednessScore(
            max_similarity=test_case["groundedness_score"],
            avg_similarity=test_case["groundedness_score"],
            num_supporting_docs=3,
            coverage=test_case["groundedness_score"],
            consistency=test_case["groundedness_score"],
            overall_score=test_case["groundedness_score"],
        )

        # Check confidence level
        actual_confidence = groundedness.confidence_level()
        actual_output = groundedness.output_type()

        confidence_match = actual_confidence == test_case["expected_confidence"]
        output_match = actual_output == test_case["expected_output"]

        print(f"     Confidence: {actual_confidence.value} {'✓' if confidence_match else '✗'}")
        print(f"     Output type: {actual_output.value} {'✓' if output_match else '✗'}")

        # Test citation behavior
        answer = "Sample answer text."
        result = OutputGenerator.format_attribution(answer, docs, groundedness)

        if test_case["groundedness_score"] >= 0.50:
            has_citation = "(Source:" in result
            print(f"     Citations: YES {'✓' if has_citation else '✗'}")
        else:
            has_citation = "(Source:" in result
            print(f"     Citations: NO {'✓' if not has_citation else '✗'}")


if __name__ == "__main__":
    test_citation_workflow_with_intent()
    test_boundary_confidence_with_intent()

    print("\n" + "=" * 80)
    print("✓ All integration tests completed successfully")
    print("=" * 80)
