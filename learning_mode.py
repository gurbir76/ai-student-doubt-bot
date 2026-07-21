import re


def is_problem_solving_question(question: str) -> bool:
    """
    Identifies questions where the student should ideally
    attempt the problem before seeing the full solution.
    """

    text = question.lower().strip()

    problem_keywords = [
        "calculate",
        "solve",
        "find",
        "compute",
        "work out",
        "show steps",
        "step by step",
    ]

    has_numbers = bool(re.search(r"\d", text))

    has_problem_keyword = any(
        keyword in text
        for keyword in problem_keywords
    )

    return has_numbers or has_problem_keyword


def get_hint_message(question: str) -> str:
    """
    Returns a general learning-oriented hint for numerical
    Business Statistics questions.
    """

    text = question.lower()

    if "mean" in text:
        return (
            "Hint: Add all the observations first, then divide "
            "the total by the number of observations."
        )

    if "standard deviation" in text:
        return (
            "Hint: Start by finding the mean. Then calculate each "
            "observation's deviation from the mean before squaring "
            "those deviations."
        )

    if "variance" in text:
        return (
            "Hint: First calculate the mean, then find the squared "
            "deviations of each observation from the mean."
        )

    if "probability" in text:
        return (
            "Hint: Identify the number of favourable outcomes and "
            "the total number of possible outcomes."
        )

    if "p-value" in text or "p value" in text:
        return (
            "Hint: Compare the p-value with the chosen significance "
            "level before deciding what happens to the null hypothesis."
        )

    return (
        "Hint: Identify the statistical concept involved, write the "
        "relevant formula, and substitute the given values step by step."
    )