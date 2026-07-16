import re


BASIC_MODEL = "llama-3.1-8b-instant"
ADVANCED_MODEL = "llama-3.3-70b-versatile"


SIMPLE_CONCEPT_KEYWORDS = [
    "what is",
    "define",
    "meaning of",
    "explain briefly",
    "formula for",
    "difference between",
    "mean",
    "median",
    "mode",
    "variance",
    "standard deviation",
    "probability",
    "correlation",
    "regression",
    "p-value",
    "hypothesis",
]


COMPLEX_REASONING_KEYWORDS = [
    "calculate",
    "solve",
    "find",
    "step by step",
    "show steps",
    "derive",
    "interpret",
    "compare",
    "analyse",
    "analyze",
    "why",
    "how",
    "numerical",
    "given the following",
    "dataset",
    "data set",
    "sample data",
    "explain in detail",
]


def contains_numbers(text: str) -> bool:
    """
    Returns True if the question contains one or more numeric values.
    """
    return bool(re.search(r"\d", text))


def is_multi_part_question(text: str) -> bool:
    """
    Detects whether the question appears to contain multiple instructions.
    """
    separators = [" and ", ", and ", ";", "\n"]
    return any(separator in text for separator in separators)


def route_model(question: str) -> dict:
    """
    Selects the Groq-hosted model based on question complexity.

    Returns:
        {
            "model": "...",
            "route": "simple" or "advanced",
            "reason": "..."
        }
    """

    clean_question = question.lower().strip()

    if not clean_question:
        return {
            "model": BASIC_MODEL,
            "route": "simple",
            "reason": "Empty or unclear question"
        }

    has_numbers = contains_numbers(clean_question)

    has_complex_keyword = any(
        keyword in clean_question
        for keyword in COMPLEX_REASONING_KEYWORDS
    )

    has_simple_keyword = any(
        keyword in clean_question
        for keyword in SIMPLE_CONCEPT_KEYWORDS
    )

    multi_part = is_multi_part_question(clean_question)

    # Advanced route for numerical or multi-step reasoning questions
    if has_numbers and (
        has_complex_keyword
        or multi_part
        or len(clean_question.split()) > 10
    ):
        return {
            "model": ADVANCED_MODEL,
            "route": "advanced",
            "reason": "Numerical or multi-step reasoning question"
        }

    # Advanced route for detailed analysis or interpretation
    if has_complex_keyword and (
        multi_part
        or len(clean_question.split()) > 12
    ):
        return {
            "model": ADVANCED_MODEL,
            "route": "advanced",
            "reason": "Complex explanation or analytical question"
        }

    # Simple route for direct conceptual questions
    if has_simple_keyword and len(clean_question.split()) <= 15:
        return {
            "model": BASIC_MODEL,
            "route": "simple",
            "reason": "Simple conceptual Business Statistics question"
        }

    # Safe default
    return {
        "model": ADVANCED_MODEL,
        "route": "advanced",
        "reason": "Defaulted to stronger model for answer quality"
    }