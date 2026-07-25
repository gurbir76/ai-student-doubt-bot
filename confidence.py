def calculate_response_confidence(
    source: str,
    routing_type: str,
    routing_reason: str,
    preferred_source_count: int = 0,
    retrieved_source_count: int = 0,
):
    """
    Returns a simple, explainable response confidence level.

    This is not model self-confidence.
    It is based on retrieval and routing signals.
    """

    if routing_type == "guardrail":
        return {
            "confidence": "Not Applicable",
            "reason": "Response was handled by a rule-based guardrail.",
        }

    score = 0
    reasons = []

    # 1. Source evidence
    if source and source not in {
        "None",
        "No relevant source found",
        "Knowledge base",
    }:
        score += 2
        reasons.append("Relevant course source found")

    # 2. Direct topic/source coverage
    if preferred_source_count > 0:
        if retrieved_source_count >= preferred_source_count:
            score += 2
            reasons.append("Expected topic sources were retrieved")
        else:
            score += 1
            reasons.append("Only part of the expected source coverage was retrieved")

    # 3. Routing suitability
    if routing_type in {"simple", "advanced"}:
        score += 1
        reasons.append("Question was routed through the expected model path")

    # Convert score to confidence band
    if score >= 4:
        confidence = "High"
    elif score >= 2:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "confidence": confidence,
        "reason": "; ".join(reasons) if reasons else "Limited supporting evidence",
    }