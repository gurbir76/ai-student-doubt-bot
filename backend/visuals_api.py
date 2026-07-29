def detect_visual_type(question: str, answer: str = "") -> str | None:
    """
    Return a visual type only when the student's question clearly maps
    to one of the supported Business Statistics visuals.

    The answer parameter is accepted for future use, but detection is
    intentionally driven by the student's question so greetings,
    identity questions and unrelated responses do not trigger visuals.
    """

    text = (question or "").strip().lower()

    if not text:
        return None

    if any(
        phrase in text
        for phrase in [
            "linear regression",
            "regression line",
            "regression",
            "slope",
            "intercept",
        ]
    ):
        return "regression"

    if any(
        phrase in text
        for phrase in [
            "p-value",
            "p value",
            "hypothesis testing",
            "significance level",
            "level of significance",
        ]
    ):
        return "p_value"

    if any(
        phrase in text
        for phrase in [
            "normal distribution",
            "bell curve",
            "z-score",
            "z score",
        ]
    ):
        return "normal_distribution"

    if any(
        phrase in text
        for phrase in [
            "standard deviation",
            "variance",
            "data spread",
            "spread of data",
            "dispersion",
        ]
    ):
        return "standard_deviation"

    if any(
        phrase in text
        for phrase in [
            "conditional probability",
            "probability",
            "independent events",
            "dependent events",
            "mutually exclusive",
        ]
    ):
        return "probability"

    if any(
        phrase in text
        for phrase in [
            "mean",
            "median",
            "mode",
            "arithmetic average",
            "average value",
        ]
    ):
        return "central_tendency"

    return None


SUPPORTED_VISUAL_TYPES = {
    "regression",
    "p_value",
    "normal_distribution",
    "standard_deviation",
    "probability",
    "central_tendency",
}
