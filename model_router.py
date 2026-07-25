import re


BASIC_MODEL = "llama-3.1-8b-instant"
ADVANCED_MODEL = "llama-3.3-70b-versatile"


SIMPLE_CONCEPT_KEYWORDS = [
    "what is",
    "define",
    "meaning of",
    "explain briefly",
    "formula for",
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


COMPARISON_KEYWORDS = [
    "difference between",
    "compare",
    "versus",
    "vs",
]


TOPIC_KEYWORDS = [
    "mean",
    "median",
    "mode",
    "variance",
    "standard deviation",
    "probability",
    "conditional probability",
    "normal distribution",
    "hypothesis testing",
    "p-value",
    "correlation",
    "regression",
    "linear regression",
]


def contains_numbers(text: str) -> bool:
    return bool(re.search(r"\d", text))


def is_multi_part_question(text: str) -> bool:
    separators = [" and ", ", and ", ";", "\n"]
    return any(separator in text for separator in separators)


def count_topic_matches(text: str) -> int:
    matched_topics = []
    sorted_topics = sorted(TOPIC_KEYWORDS, key=len, reverse=True)

    for topic in sorted_topics:
        if topic in text:
            if not any(
                topic in existing or existing in topic
                for existing in matched_topics
            ):
                matched_topics.append(topic)

    return len(matched_topics)


def route_model(question: str) -> dict:
    clean_question = question.lower().strip()

    if not clean_question:
        return {
            "model": BASIC_MODEL,
            "route": "simple",
            "reason": "Empty or unclear question",
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

    has_comparison_keyword = any(
        keyword in clean_question
        for keyword in COMPARISON_KEYWORDS
    )

    multi_part = is_multi_part_question(clean_question)
    topic_count = count_topic_matches(clean_question)

    if topic_count >= 2 and (
        has_comparison_keyword
        or multi_part
        or has_complex_keyword
    ):
        return {
            "model": ADVANCED_MODEL,
            "route": "advanced",
            "reason": "Multi-topic comparison or explanation question",
        }

    if has_numbers and (
        has_complex_keyword
        or multi_part
        or len(clean_question.split()) > 10
    ):
        return {
            "model": ADVANCED_MODEL,
            "route": "advanced",
            "reason": "Numerical or multi-step reasoning question",
        }

    if has_complex_keyword and (
        multi_part
        or len(clean_question.split()) > 12
    ):
        return {
            "model": ADVANCED_MODEL,
            "route": "advanced",
            "reason": "Complex explanation or analytical question",
        }

    if (
        has_simple_keyword
        and topic_count <= 1
        and len(clean_question.split()) <= 15
    ):
        return {
            "model": BASIC_MODEL,
            "route": "simple",
            "reason": "Simple conceptual Business Statistics question",
        }

    return {
        "model": ADVANCED_MODEL,
        "route": "advanced",
        "reason": "Defaulted to stronger model for answer quality",
    }