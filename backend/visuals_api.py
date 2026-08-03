def detect_visual_type(question: str, answer: str = "") -> str | None:
    """
    Return a visual only when the student's original question explicitly
    names a supported Business Statistics topic.

    The generated answer is intentionally ignored. This prevents an
    unrelated retrieved document or model response from triggering a
    misleading visual.
    """

    text = f" {(question or '').strip().lower()} "

    if not text.strip():
        return None

    phrase_map = [
        (
            "regression",
            [
                "linear regression",
                "regression line",
                "simple regression",
                "slope and intercept",
            ],
        ),
        (
            "p_value",
            [
                "p-value",
                "p value",
                "hypothesis testing",
                "significance level",
                "level of significance",
            ],
        ),
        (
            "normal_distribution",
            [
                "normal distribution",
                "bell curve",
                "z-score",
                "z score",
            ],
        ),
        (
            "standard_deviation",
            [
                "standard deviation",
                "variance",
                "data spread",
                "spread of data",
                "dispersion",
            ],
        ),
        (
            "probability",
            [
                "conditional probability",
                "probability",
                "independent events",
                "dependent events",
                "mutually exclusive",
            ],
        ),
        (
            "central_tendency",
            [
                "mean",
                "median",
                "mode",
                "arithmetic average",
                "average value",
            ],
        ),
    ]

    for visual_type, phrases in phrase_map:
        if any(
            f" {phrase} " in text
            or text.strip().startswith(f"{phrase} ")
            or text.strip().endswith(f" {phrase}")
            for phrase in phrases
        ):
            return visual_type

    return None


SUPPORTED_VISUAL_TYPES = {
    "regression",
    "p_value",
    "normal_distribution",
    "standard_deviation",
    "probability",
    "central_tendency",
}
