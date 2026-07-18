import streamlit as st
from rag_engine import generate_answer
from visuals import detect_visual_type, show_visual_explanation
from observability import (
    log_user_feedback,
    create_langfuse_trace_id,
)

st.set_page_config(
    page_title="AI Student Doubt Resolution Bot",
    page_icon="🧑‍🏫",
    layout="centered"
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
    unsafe_allow_html=True
)

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="main-title">
        <span class="title-icon">🧑‍🏫</span>AI Student Doubt Resolution Bot
    </div>
    <div class="main-subtitle">
        Business Statistics support for first-year MBA / undergraduate management students
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Session state
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("About this Bot")
    st.write(
        """
        This bot answers Business Statistics doubts using a curated course knowledge base.
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
        "For marks, attendance, fees, exam cheating, or personal issues, contact faculty/admin."
    )

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------
# Intro box when chat is empty
# -----------------------------
if not st.session_state.messages:
    st.markdown(
        """
        <div class="info-box">
            Ask a Business Statistics doubt below. The bot will search the approved knowledge base,
            generate a beginner-friendly explanation, and show the source used.
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# Display chat history
# -----------------------------
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message["role"] == "assistant":
            visual_type = message.get("visual_type")

            if visual_type:
                with st.expander("Show visual explanation"):
                    show_visual_explanation(visual_type)

            source = message.get("source", "N/A")
            model_used = message.get("model_used", "N/A")
            routing_type = message.get("routing_type", "N/A")
            routing_reason = message.get("routing_reason", "N/A")
            latency_ms = message.get("latency_ms", "N/A")
            input_tokens = message.get("input_tokens", "N/A")
            output_tokens = message.get("output_tokens", "N/A")
            feedback_id = message.get("feedback_id")

            st.caption(
                f"Source: {source} | Model: {model_used} | "
                f"Route: {routing_type} | Reason: {routing_reason} | "
                f"Latency: {latency_ms} ms | "
                f"Input tokens: {input_tokens} | Output tokens: {output_tokens}"
            )

            if feedback_id and not message.get("feedback_given", False):
                col1, col2, col3 = st.columns([1, 1, 5])

                with col1:
                    if st.button("👍 Helpful", key=f"helpful_{idx}_{feedback_id}"):
                        log_user_feedback(
                            trace_id=feedback_id,
                            feedback_value="helpful",
                            comment="User marked answer as helpful"
                        )
                        st.session_state.messages[idx]["feedback_given"] = True
                        st.session_state.messages[idx]["feedback_value"] = "Helpful"
                        st.rerun()

                with col2:
                    if st.button("👎 Not helpful", key=f"not_helpful_{idx}_{feedback_id}"):
                        log_user_feedback(
                            trace_id=feedback_id,
                            feedback_value="not_helpful",
                            comment="User marked answer as not helpful"
                        )
                        st.session_state.messages[idx]["feedback_given"] = True
                        st.session_state.messages[idx]["feedback_value"] = "Not helpful"
                        st.rerun()

            elif message.get("feedback_given", False):
                feedback_value = message.get("feedback_value", "recorded")
                st.caption(f"Feedback recorded: {feedback_value}")

# -----------------------------
# Chat input
# -----------------------------
student_question = st.chat_input("Ask your Business Statistics doubt...")

if student_question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": student_question
        }
    )

    with st.chat_message("user"):
        st.write(student_question)

    with st.chat_message("assistant"):
        with st.spinner("Searching approved course material..."):

            trace_id = create_langfuse_trace_id()

            if trace_id:
                result = generate_answer(
                    student_question,
                    langfuse_trace_id=trace_id
                )
            else:
                result = generate_answer(student_question)

            # Attach the exact Langfuse trace ID for later feedback
            result["feedback_id"] = trace_id

            # These must be defined BEFORE appending to session state
            answer = result["answer"]
            source = result["source"]
            model_used = result.get("model_used", "N/A")
            routing_type = result.get("routing_type", "N/A")
            routing_reason = result.get("routing_reason", "N/A")
            latency_ms = result.get("latency_ms", "N/A")
            input_tokens = result.get("input_tokens", "N/A")
            output_tokens = result.get("output_tokens", "N/A")

            st.write(answer)

            visual_type = detect_visual_type(student_question)

            if visual_type:
                with st.expander("Show visual explanation"):
                    show_visual_explanation(visual_type)

            st.caption(
                f"Source: {source} | Model: {model_used} | "
                f"Route: {routing_type} | Reason: {routing_reason} | "
                f"Latency: {latency_ms} ms | "
                f"Input tokens: {input_tokens} | Output tokens: {output_tokens}"
            )

    # This block must remain INSIDE if student_question:
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
            "feedback_id": result.get("feedback_id"),
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
        AI Student Doubt Resolution Bot · Built with Streamlit, ChromaDB, Groq and a curated Business Statistics knowledge base
    </div>
    """,
    unsafe_allow_html=True
)