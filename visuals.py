import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def detect_visual_type(question: str, answer: str = ""):
    """
    Detects whether a visual should be shown based only on the student's question.
    This avoids showing graphs for greetings or bot capability responses.
    """

    text = question.lower()

    if any(word in text for word in ["slope", "regression", "linear regression", "intercept"]):
        return "regression"

    if any(word in text for word in ["p-value", "p value", "hypothesis testing", "significance level"]):
        return "p_value"

    if any(word in text for word in ["normal distribution", "bell curve", "z-score", "z score"]):
        return "normal_distribution"

    if any(word in text for word in ["standard deviation", "variance", "spread"]):
        return "standard_deviation"

    if any(word in text for word in ["conditional probability", "probability", "event"]):
        return "probability"

    if any(word in text for word in ["mean", "median", "mode", "average"]):
        return "central_tendency"

    return None


def show_visual_explanation(visual_type: str):
    """
    Shows a Streamlit visual based on the detected Business Statistics topic.
    """

    if visual_type == "regression":
        show_regression_visual()

    elif visual_type == "p_value":
        show_p_value_visual()

    elif visual_type == "normal_distribution":
        show_normal_distribution_visual()

    elif visual_type == "standard_deviation":
        show_standard_deviation_visual()

    elif visual_type == "probability":
        show_probability_visual()

    elif visual_type == "central_tendency":
        show_central_tendency_visual()


def show_regression_visual():
    st.markdown("### Visual Explanation: Simple Linear Regression")

    x = np.array([1, 2, 3, 4, 5])
    y = np.array([3, 5, 7, 9, 11])

    fig, ax = plt.subplots()
    ax.scatter(x, y, label="Data points")
    ax.plot(x, y, label="Regression line: Y = a + bX")

    ax.set_xlabel("X: Independent Variable")
    ax.set_ylabel("Y: Dependent Variable")
    ax.set_title("Regression Line and Slope")
    ax.legend()

    st.pyplot(fig)

    st.info(
        "The slope shows how much Y changes when X increases by one unit. "
        "A steeper line means a stronger increase in Y for each increase in X."
    )


def show_p_value_visual():
    st.markdown("### Visual Explanation: p-value")

    x = np.linspace(-4, 4, 500)
    y = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x**2)

    fig, ax = plt.subplots()
    ax.plot(x, y)

    critical_x = 1.65
    x_fill = x[x >= critical_x]
    y_fill = y[x >= critical_x]

    ax.fill_between(x_fill, y_fill, alpha=0.4)
    ax.axvline(critical_x, linestyle="--")

    ax.set_title("p-value as Tail Area")
    ax.set_xlabel("Test Statistic")
    ax.set_ylabel("Probability Density")

    st.pyplot(fig)

    st.info(
        "The shaded area represents the p-value. A smaller shaded area means the observed result "
        "is less likely under the null hypothesis."
    )


def show_normal_distribution_visual():
    st.markdown("### Visual Explanation: Normal Distribution")

    x = np.linspace(-4, 4, 500)
    y = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x**2)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.axvline(0, linestyle="--", label="Mean")
    ax.axvline(1, linestyle=":", label="+1 SD")
    ax.axvline(-1, linestyle=":", label="-1 SD")

    ax.set_title("Normal Distribution")
    ax.set_xlabel("Value")
    ax.set_ylabel("Probability Density")
    ax.legend()

    st.pyplot(fig)

    st.info(
        "In a normal distribution, values are concentrated around the mean. "
        "The curve is symmetric, and standard deviation shows the spread."
    )


def show_standard_deviation_visual():
    st.markdown("### Visual Explanation: Standard Deviation")

    low_spread = np.array([48, 49, 50, 51, 52])
    high_spread = np.array([30, 40, 50, 60, 70])

    fig, ax = plt.subplots()

    ax.scatter(low_spread, np.ones(len(low_spread)), label="Low standard deviation")
    ax.scatter(high_spread, np.ones(len(high_spread)) * 2, label="High standard deviation")

    ax.set_yticks([1, 2])
    ax.set_yticklabels(["Low Spread", "High Spread"])
    ax.set_xlabel("Values")
    ax.set_title("Low vs High Standard Deviation")
    ax.legend()

    st.pyplot(fig)

    st.info(
        "Standard deviation tells how spread out values are from the mean. "
        "Closely packed values have low standard deviation; widely spread values have high standard deviation."
    )


def show_probability_visual():
    st.markdown("### Visual Explanation: Conditional Probability")

    st.markdown(
        """
        Suppose we are studying students who passed Statistics.

        | Group | Number of Students |
        |---|---:|
        | Total students | 100 |
        | Students who studied regularly | 40 |
        | Students who studied regularly and passed | 30 |

        Conditional probability asks:

        **Out of the students who studied regularly, how many passed?**

        Formula:

        **P(Passed | Studied) = Students who studied and passed / Students who studied**
        """
    )

    st.info(
        "Conditional probability focuses only on the group where the condition has already happened."
    )


def show_central_tendency_visual():
    st.markdown("### Visual Explanation: Mean, Median, and Mode")

    data = np.array([2, 3, 3, 4, 8])
    mean_value = np.mean(data)
    median_value = np.median(data)
    mode_value = 3

    fig, ax = plt.subplots()

    ax.scatter(data, np.zeros(len(data)))
    ax.axvline(mean_value, linestyle="--", label=f"Mean = {mean_value:.1f}")
    ax.axvline(median_value, linestyle=":", label=f"Median = {median_value}")
    ax.axvline(mode_value, linestyle="-.", label=f"Mode = {mode_value}")

    ax.set_yticks([])
    ax.set_xlabel("Data Values")
    ax.set_title("Mean, Median, and Mode on a Number Line")
    ax.legend()

    st.pyplot(fig)

    st.info(
        "Mean is the average, median is the middle value, and mode is the most repeated value."
    )