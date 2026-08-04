"""Simple, explainable response-assurance scoring.

This is not model self-confidence and it is not a factual guarantee.
It combines question-to-source relevance, answer grounding,
source availability, and guardrail outcome.
"""

from __future__ import annotations

import numpy as np


def _cosine_similarity(vector_a, vector_b) -> float:
    a = np.asarray(vector_a, dtype=float)
    b = np.asarray(vector_b, dtype=float)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator == 0:
        return 0.0

    similarity = float(np.dot(a, b) / denominator)
    return max(0.0, min(1.0, similarity))


def _semantic_similarity(
    first_text: str,
    second_text: str,
    embedding_model,
) -> float:
    if not first_text or not second_text or embedding_model is None:
        return 0.0

    embeddings = embedding_model.encode(
        [first_text, second_text],
        convert_to_numpy=True,
    )

    return _cosine_similarity(
        embeddings[0],
        embeddings[1],
    )


def calculate_question_source_similarity(
    question: str,
    context: str,
    embedding_model,
) -> float:
    """Measure whether the retrieved context is relevant to the question."""

    return _semantic_similarity(
        question,
        context,
        embedding_model,
    )


def calculate_grounding_similarity(
    answer: str,
    context: str,
    embedding_model,
) -> float:
    """Measure whether the generated answer is grounded in retrieved context."""

    return _semantic_similarity(
        answer,
        context,
        embedding_model,
    )


def classify_hallucination_risk(score: int) -> str:
    if score >= 90:
        return "Low"
    if score >= 70:
        return "Medium"
    return "High"


def calculate_runtime_assurance(
    *,
    source: str,
    question_source_similarity: float,
    grounding_similarity: float,
    guardrail_pass: bool,
    recognised_topic_match: bool = False,
) -> dict:
    """
    Runtime score:
    - question-to-source relevance: 35 points
    - answer-to-source grounding: 35 points
    - source availability: 15 points
    - guardrail compliance: 15 points
    """

    valid_source = bool(source) and source not in {
        "None",
        "No relevant source found",
        "Knowledge base",
    }

    source_score = 15 if valid_source else 0

    # A deterministic topic-to-source match is stronger evidence than
    # embedding similarity alone. This prevents supported terminology
    # such as H0/H1, Type I/II error and z-score from being penalised.
    if recognised_topic_match and valid_source:
        relevance_score = 35
    elif question_source_similarity >= 0.60:
        relevance_score = 35
    elif question_source_similarity >= 0.45:
        relevance_score = 25
    elif question_source_similarity >= 0.35:
        relevance_score = 10
    else:
        relevance_score = 0

    # Answers often paraphrase the source, especially worked numerical
    # solutions. Similarity >= 0.50 is treated as meaningful grounding.
    if grounding_similarity >= 0.75:
        grounding_score = 35
    elif grounding_similarity >= 0.50:
        grounding_score = 25
    elif grounding_similarity >= 0.35:
        grounding_score = 10
    else:
        grounding_score = 0

    guardrail_score = 15 if guardrail_pass else 0

    assurance_score = (
        relevance_score
        + grounding_score
        + source_score
        + guardrail_score
    )

    hallucination_risk = classify_hallucination_risk(
        assurance_score
    )

    relevance_basis = (
        "recognised topic mapped to approved source"
        if recognised_topic_match and valid_source
        else "semantic question-source similarity"
    )

    reasons = [
        (
            f"Question-source relevance {relevance_score}/35 "
            f"({relevance_basis})"
        ),
        f"Answer grounding {grounding_score}/35",
        f"Source availability {source_score}/15",
        f"Guardrail compliance {guardrail_score}/15",
    ]

    return {
        "assurance_score": assurance_score,
        "hallucination_risk": hallucination_risk,
        "relevance_score": relevance_score,
        "grounding_score": grounding_score,
        "source_score": source_score,
        "guardrail_score": guardrail_score,
        "question_source_similarity": round(
            question_source_similarity,
            3,
        ),
        "grounding_similarity": round(
            grounding_similarity,
            3,
        ),
        "assurance_reason": "; ".join(reasons),
    }


def calculate_rule_based_assurance(
    *,
    routing_reason: str,
    source: str,
) -> dict:
    """Score deterministic rule-based responses."""

    reason = (routing_reason or "").lower()
    source_text = (source or "").lower()

    is_failure_or_unsupported = (
        "technical" in reason
        or "error" in reason
        or "error" in source_text
        or "no relevant knowledge-base source" in reason
        or "no relevant source found" in source_text
        or "unsupported topic" in reason
    )

    if is_failure_or_unsupported:
        return {
            "assurance_score": 15,
            "hallucination_risk": "High",
            "relevance_score": 0,
            "grounding_score": 0,
            "source_score": 0,
            "guardrail_score": 15,
            "question_source_similarity": None,
            "grounding_similarity": None,
            "assurance_reason": (
                "The approved knowledge base did not contain sufficiently "
                "relevant evidence for this question."
            ),
        }

    return {
        "assurance_score": 100,
        "hallucination_risk": "Low",
        "relevance_score": 35,
        "grounding_score": 35,
        "source_score": 15,
        "guardrail_score": 15,
        "question_source_similarity": None,
        "grounding_similarity": None,
        "assurance_reason": (
            "Deterministic rule-based response; no model-generated factual "
            "answer was used."
        ),
    }
