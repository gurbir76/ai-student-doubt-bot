import streamlit as st
from rag_engine import generate_answer

st.set_page_config(
    page_title="AI Student Doubt Resolution Bot",
    page_icon="🧑‍🏫",
    layout="centered"
)
# Custom heading styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 700;
        line-height: 1.15;
        color: #F5F5F5;
        margin-bottom: 6px;
    }

    .main-subtitle {
        font-size: 16px;
        color: #B8B8B8;
        margin-bottom: 28px;
    }

    .title-icon {
        font-size: 34px;
        margin-right: 10px;
        vertical-align: middle;
    }

    .stChatMessage {
        border-radius: 14px;
    }

    </style>

    <div class="main-title">
        <span class="title-icon">🧑‍🏫</span>AI Student Doubt Resolution Bot
    </div>
    <div class="main-subtitle">
        Business Statistics support for first-year MBA / undergraduate management students
    </div>
    """,
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("About this Bot")
    st.write("""
This bot answers Business Statistics doubts using curated course material.
It supports beginner to intermediate learners.
    """)

    st.header("Covered Topics")
    st.write("""
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
    """)

    st.warning("For marks, attendance, fees, exam cheating, or personal issues, contact faculty/admin.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

student_question = st.chat_input("Ask your Business Statistics doubt...")

if student_question:
    st.session_state.messages.append({
        "role": "user",
        "content": student_question
    })

    with st.chat_message("user"):
        st.write(student_question)

    with st.chat_message("assistant"):
        with st.spinner("Searching course material..."):
            result = generate_answer(student_question)
            st.write(result["answer"])
            st.caption(f"Source: {result['source']}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"]
    })