import streamlit as st

from rag_engine import generate_answer
from visuals import detect_visual_type, show_visual_explanation

from observability import (
    log_user_feedback,
    create_langfuse_trace_id,
)

from governance import (
    get_review_priority,
    ROOT_CAUSE_CATEGORIES,
)

from learning_mode import (
    is_problem_solving_question,
    get_hint_message,
)


st.set_page_config(
    page_title="AI Student Doubt Resolution Bot",
    page_icon="🧑‍🏫",
    layout="centered",
)


# -----------------------------
# Custom CSS
# -----------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 34px;
        font-weight: 750;
        line-height: 1.15;
        color: #F5F5F5;
        margin-bottom: 4px;
        text-align: center;
    }

    .main-subtitle {
        font-size: 15px;
        color: #B8B8B8;
        margin-bottom: 24px;
        text-align: center;
    }

    .title-icon {
        font-size: 30px;
        margin-right: 8px;
        vertical-align: middle;
    }

    .info-box {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 14px 16px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 18px;
        font-size: 14px;
        color: #D0D0D0;
    }

    .footer-text {
        text-align: center;
        font-size: 12px;
        color: #8A8A8A;
        margin-top: 30px;
    }

    .source-caption {
        font-size: 12px;
        color: #999999;
        margin-top: 8px;
    }

    .stChatMessage {
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="main-title">
        <span class="title-icon">🧑‍🏫</span>
        AI Student Doubt Resolution Bot
    </div>

    <div class="main-subtitle">
        Business Statistics support for first-year MBA /
        undergraduate management students
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Session state
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_learning_question" not in st.session_state:
    st.session_state.pending_learning_question = None

if "pending_learning_hint" not in st.session_state:
    st.session_state.pending_learning_hint = None

if "show_full_solution" not in st.session_state:
    st.session_state.show_full_solution = False

if "try_first_message" not in st.session_state:
    st.session_state.try_first_message = False


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.header("About this Bot")

    st.write(
        """
        This bot answers Business Statistics doubts using
        a curated course knowledge base.

        It is designed for beginner to intermediate learners.
        """
    )

    st.header("Covered Topics")

    st.write(
        """
        - Introduction to Statistics
        - Mean, Median, Mode
        - Variance and Standard Deviation
        - Basic Probability
        - Conditional Probability
        - Normal Distribution
        - Hypothesis Testing
        - P-Value
        - Correlation
        - Simple Linear Regression
        """
    )

    st.header("Try asking")

    st.write(
        """
        - What is p-value?
        - What is conditional probability?
        - What is standard deviation?
        - Difference between correlation and regression?
        - What is the formula for mean?
        """
    )

    st.warning(
        "For marks, attendance, fees, exam cheating, "
        "or personal issues, contact faculty/admin."
    )

    if st.button("Clear chat"):

        st.session_state.messages = []

        st.session_state.pending_learning_question = None
        st.session_state.pending_learning_hint = None
        st.session_state.show_full_solution = False
        st.session_state.try_first_message = False

        st.rerun()


# -----------------------------
# Intro box when chat is empty
# -----------------------------
if (
    not st.session_state.messages
    and not st.session_state.pending_learning_question
):
    st.markdown(
        """
        <div class="info-box">
            Ask a Business Statistics doubt below.
            The bot will search the approved knowledge base,
            generate a beginner-friendly explanation,
            and show the source used.
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Display chat history
# -----------------------------
for idx, message in enumerate(
    st.session_state.messages
):

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )

        if message["role"] == "assistant":

            visual_type = message.get(
                "visual_type"
            )

            if visual_type:

                with st.expander(
                    "Show visual explanation"
                ):
                    show_visual_explanation(
                        visual_type
                    )

            source = message.get(
                "source",
                "N/A",
            )

            model_used = message.get(
                "model_used",
                "N/A",
            )

            routing_type = message.get(
                "routing_type",
                "N/A",
            )

            routing_reason = message.get(
                "routing_reason",
                "N/A",
            )

            latency_ms = message.get(
                "latency_ms",
                "N/A",
            )

            input_tokens = message.get(
                "input_tokens",
                "N/A",
            )

            output_tokens = message.get(
                "output_tokens",
                "N/A",
            )

            feedback_id = message.get(
                "feedback_id"
            )

            # Do not show technical metadata
            # for learning-only hint messages.
            if not message.get(
                "learning_hint",
                False,
            ):

                st.caption(
                    f"Source: {source} | "
                    f"Model: {model_used} | "
                    f"Route: {routing_type} | "
                    f"Reason: {routing_reason} | "
                    f"Latency: {latency_ms} ms | "
                    f"Input tokens: {input_tokens} | "
                    f"Output tokens: {output_tokens}"
                )

            # -----------------------------
            # Feedback buttons
            # -----------------------------
            if (
                feedback_id
                and not message.get(
                    "feedback_given",
                    False,
                )
            ):

                col1, col2, col3 = st.columns(
                    [1, 1, 5]
                )

                with col1:

                    if st.button(
                        "👍 Helpful",
                        key=(
                            f"helpful_"
                            f"{idx}_"
                            f"{feedback_id}"
                        ),
                    ):

                        log_user_feedback(
                            trace_id=feedback_id,
                            feedback_value="helpful",
                            comment=(
                                "User marked answer "
                                "as helpful"
                            ),
                        )

                        st.session_state.messages[
                            idx
                        ][
                            "feedback_given"
                        ] = True

                        st.session_state.messages[
                            idx
                        ][
                            "feedback_value"
                        ] = "Helpful"

                        st.rerun()

                with col2:

                    if st.button(
                        "👎 Not helpful",
                        key=(
                            f"not_helpful_"
                            f"{idx}_"
                            f"{feedback_id}"
                        ),
                    ):

                        log_user_feedback(
                            trace_id=feedback_id,
                            feedback_value="not_helpful",
                            comment=(
                                "User marked answer "
                                "as not helpful"
                            ),
                        )

                        review_priority = (
                            get_review_priority(
                                "not_helpful"
                            )
                        )

                        st.session_state.messages[
                            idx
                        ][
                            "feedback_given"
                        ] = True

                        st.session_state.messages[
                            idx
                        ][
                            "feedback_value"
                        ] = "Not helpful"

                        st.session_state.messages[
                            idx
                        ][
                            "review_priority"
                        ] = review_priority

                        st.session_state.messages[
                            idx
                        ][
                            "review_status"
                        ] = "Pending Review"

                        st.session_state.messages[
                            idx
                        ][
                            "root_cause"
                        ] = "Pending Classification"

                        st.rerun()

            # -----------------------------
            # Governance review
            # -----------------------------
            elif message.get(
                "feedback_given",
                False,
            ):

                feedback_value = message.get(
                    "feedback_value",
                    "recorded",
                )

                st.caption(
                    f"Feedback recorded: "
                    f"{feedback_value}"
                )

                if (
                    feedback_value
                    == "Not helpful"
                ):

                    review_priority = message.get(
                        "review_priority",
                        "High",
                    )

                    review_status = message.get(
                        "review_status",
                        "Pending Review",
                    )

                    root_cause = message.get(
                        "root_cause",
                        "Pending Classification",
                    )

                    st.caption(
                        f"Review priority: "
                        f"{review_priority} | "
                        f"Review status: "
                        f"{review_status} | "
                        f"Root cause: "
                        f"{root_cause}"
                    )

                    with st.expander(
                        "Review governance details"
                    ):

                        root_cause_options = (
                            [
                                "Pending Classification"
                            ]
                            + ROOT_CAUSE_CATEGORIES
                        )

                        selected_root_cause = (
                            st.selectbox(
                                "Reviewer root-cause "
                                "classification",
                                root_cause_options,
                                index=(
                                    root_cause_options
                                    .index(
                                        root_cause
                                    )
                                    if root_cause
                                    in root_cause_options
                                    else 0
                                ),
                                key=(
                                    f"root_cause_"
                                    f"{idx}_"
                                    f"{feedback_id}"
                                ),
                            )
                        )

                        if st.button(
                            "Save Classification",
                            key=(
                                f"save_root_cause_"
                                f"{idx}_"
                                f"{feedback_id}"
                            ),
                        ):

                            st.session_state.messages[
                                idx
                            ][
                                "root_cause"
                            ] = selected_root_cause

                            if (
                                selected_root_cause
                                != "Pending Classification"
                            ):
                                st.session_state.messages[
                                    idx
                                ][
                                    "review_status"
                                ] = "Under Review"

                            st.rerun()

                        if (
                            root_cause
                            != "Pending Classification"
                            and review_status
                            != "Resolved"
                        ):

                            if st.button(
                                "Resolve Review",
                                key=(
                                    f"resolve_review_"
                                    f"{idx}_"
                                    f"{feedback_id}"
                                ),
                            ):

                                st.session_state.messages[
                                    idx
                                ][
                                    "review_status"
                                ] = "Resolved"

                                st.rerun()


# =====================================================
# LEARNING MODE — PENDING QUESTION
# =====================================================

if st.session_state.pending_learning_question:

    pending_question = (
        st.session_state
        .pending_learning_question
    )

    pending_hint = (
        st.session_state
        .pending_learning_hint
    )

    with st.chat_message("assistant"):

        # ---------------------------------
        # Hint first
        # ---------------------------------
        if not st.session_state.show_full_solution:

            st.info(
                f"💡 Learning Hint\n\n"
                f"{pending_hint}"
            )

            st.write(
                "Try working through the problem "
                "before viewing the complete solution."
            )

            col1, col2 = st.columns(
                [1, 1]
            )

            with col1:

                if st.button(
                    "Show Full Solution",
                    key="show_full_solution_button",
                ):

                    st.session_state.show_full_solution = True
                    st.session_state.try_first_message = False

                    st.rerun()

            with col2:

                if st.button(
                    "I'll Try First",
                    key="try_first_button",
                ):

                    st.session_state.try_first_message = True

                    st.rerun()

            if st.session_state.try_first_message:

                st.success(
                    "Great choice. Try solving it yourself first. "
                    "When you are ready, click "
                    "'Show Full Solution'."
                )

        # ---------------------------------
        # Full solution requested
        # ---------------------------------
        else:

            with st.spinner(
                "Searching approved course material..."
            ):

                trace_id = (
                    create_langfuse_trace_id()
                )

                if trace_id:

                    result = generate_answer(
                        pending_question,
                        langfuse_trace_id=trace_id,
                    )

                else:

                    result = generate_answer(
                        pending_question
                    )

                result[
                    "feedback_id"
                ] = trace_id

                answer = result["answer"]

                source = result["source"]

                model_used = result.get(
                    "model_used",
                    "N/A",
                )

                routing_type = result.get(
                    "routing_type",
                    "N/A",
                )

                routing_reason = result.get(
                    "routing_reason",
                    "N/A",
                )

                latency_ms = result.get(
                    "latency_ms",
                    "N/A",
                )

                input_tokens = result.get(
                    "input_tokens",
                    "N/A",
                )

                output_tokens = result.get(
                    "output_tokens",
                    "N/A",
                )

                visual_type = (
                    detect_visual_type(
                        pending_question
                    )
                )

                st.write(
                    answer
                )

                if visual_type:

                    with st.expander(
                        "Show visual explanation"
                    ):

                        show_visual_explanation(
                            visual_type
                        )

                st.caption(
                    f"Source: {source} | "
                    f"Model: {model_used} | "
                    f"Route: {routing_type} | "
                    f"Reason: {routing_reason} | "
                    f"Latency: {latency_ms} ms | "
                    f"Input tokens: {input_tokens} | "
                    f"Output tokens: {output_tokens}"
                )

                # Save full answer
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "source": source,
                        "visual_type": visual_type,
                        "model_used": model_used,
                        "routing_type": routing_type,
                        "routing_reason": routing_reason,
                        "latency_ms": latency_ms,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "feedback_id": (
                            result.get(
                                "feedback_id"
                            )
                        ),
                        "feedback_given": False,
                    }
                )

                # Clear pending learning state
                st.session_state.pending_learning_question = None
                st.session_state.pending_learning_hint = None
                st.session_state.show_full_solution = False
                st.session_state.try_first_message = False

                st.rerun()


# -----------------------------
# Chat input
# -----------------------------
student_question = st.chat_input(
    "Ask your Business Statistics doubt..."
)


if student_question:

    # Save student question
    st.session_state.messages.append(
        {
            "role": "user",
            "content": student_question,
        }
    )

    problem_question = (
        is_problem_solving_question(
            student_question
        )
    )

    # =================================================
    # Problem-solving question → Hint-first learning mode
    # =================================================
    if problem_question:

        st.session_state.pending_learning_question = (
            student_question
        )

        st.session_state.pending_learning_hint = (
            get_hint_message(
                student_question
            )
        )

        st.session_state.show_full_solution = False
        st.session_state.try_first_message = False

        st.rerun()

    # =================================================
    # Conceptual question → Normal answer flow
    # =================================================
    else:

        with st.chat_message("user"):

            st.write(
                student_question
            )

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching approved course material..."
            ):

                trace_id = (
                    create_langfuse_trace_id()
                )

                if trace_id:

                    result = generate_answer(
                        student_question,
                        langfuse_trace_id=trace_id,
                    )

                else:

                    result = generate_answer(
                        student_question
                    )

                # Attach exact trace ID
                result[
                    "feedback_id"
                ] = trace_id

                answer = result["answer"]

                source = result["source"]

                model_used = result.get(
                    "model_used",
                    "N/A",
                )

                routing_type = result.get(
                    "routing_type",
                    "N/A",
                )

                routing_reason = result.get(
                    "routing_reason",
                    "N/A",
                )

                latency_ms = result.get(
                    "latency_ms",
                    "N/A",
                )

                input_tokens = result.get(
                    "input_tokens",
                    "N/A",
                )

                output_tokens = result.get(
                    "output_tokens",
                    "N/A",
                )

                st.write(
                    answer
                )

                visual_type = (
                    detect_visual_type(
                        student_question
                    )
                )

                if visual_type:

                    with st.expander(
                        "Show visual explanation"
                    ):

                        show_visual_explanation(
                            visual_type
                        )

                st.caption(
                    f"Source: {source} | "
                    f"Model: {model_used} | "
                    f"Route: {routing_type} | "
                    f"Reason: {routing_reason} | "
                    f"Latency: {latency_ms} ms | "
                    f"Input tokens: {input_tokens} | "
                    f"Output tokens: {output_tokens}"
                )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "source": source,
                "visual_type": visual_type,
                "model_used": model_used,
                "routing_type": routing_type,
                "routing_reason": routing_reason,
                "latency_ms": latency_ms,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "feedback_id": (
                    result.get(
                        "feedback_id"
                    )
                ),
                "feedback_given": False,
            }
        )

        st.rerun()


# -----------------------------
# Footer
# -----------------------------
st.markdown(
    """
    <div class="footer-text">
        AI Student Doubt Resolution Bot ·
        Built with Streamlit, ChromaDB, Groq and a
        curated Business Statistics knowledge base
    </div>
    """,
    unsafe_allow_html=True,
)