QUALITY_CRITERIA = {
    "correctness": "Is the answer factually and statistically correct?",
    "relevance": "Does the answer directly address the student's question?",
    "grounding": "Is the answer supported by the approved knowledge base?",
    "clarity": "Is the answer understandable for the target student level?",
    "completeness": "Does the answer provide sufficient explanation, formula, or example?",
    "source_quality": "Are the retrieved and displayed sources relevant?",
    "scope_compliance": "Does the answer remain within the approved Business Statistics scope?",
}


ROOT_CAUSE_CATEGORIES = [
    "RETRIEVAL_ERROR",
    "KNOWLEDGE_GAP",
    "MODEL_ERROR",
    "PROMPT_ERROR",
    "ROUTING_ERROR",
    "GUARDRAIL_ERROR",
    "UI_OR_CONTEXT_ERROR",
]


GOVERNANCE_OWNERS = {
    "subject_correctness": "Faculty / SME",
    "knowledge_base": "Academic Owner",
    "prompt_logic": "Technical Owner",
    "retrieval_quality": "Technical Owner",
    "model_routing": "Technical Owner",
    "wrong_answer_review": "Faculty + Technical Owner",
    "deployment": "Technical Owner",
    "feedback_monitoring": "Project Team",
}


def get_quality_rating(total_score: int) -> str:
    """
    Converts a 0-14 quality score into a governance rating.
    """
    if total_score >= 12:
        return "Good"
    elif total_score >= 8:
        return "Needs Review"
    else:
        return "Poor"


def get_review_priority(feedback_value: str, quality_score=None) -> str:
    """
    Determines review priority for a chatbot response.
    """

    if feedback_value == "not_helpful":
        return "High"

    if quality_score is not None and quality_score < 8:
        return "High"

    if quality_score is not None and quality_score < 12:
        return "Medium"

    return "Low"