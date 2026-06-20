import streamlit as st
from rag_engine import generate_answer
from visuals import detect_visual_type, show_visual_explanation

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
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message["role"] == "assistant" and message.get("source"):
            st.caption(f"Source: {message['source']}")

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
            result = generate_answer(student_question)
            answer = result["answer"]
            source = result["source"]

            st.write(answer)

            visual_type = detect_visual_type(student_question, answer)

            if visual_type:
                with st.expander("Show visual explanation"):
                    show_visual_explanation(visual_type)

            st.caption(f"Source: {source}")

    st.session_state.messages.append(
    {
        "role": "assistant",
        "content": answer,
        "source": source,
        "visual_type": visual_type
    }
)

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