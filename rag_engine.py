import os
import time
import streamlit as st
import chromadb
import uuid
from pathlib import Path
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from observability import observe_generation, flush_langfuse, get_active_trace_id
from observability import observe_generation, flush_langfuse

# -----------------------------
# Load API key
# -----------------------------
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    try:
        groq_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        groq_api_key = None

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY is missing. Add it to .env locally or Streamlit secrets online."
    )

llm_client = Groq(api_key=groq_api_key)


# -----------------------------
# Load Groq model
# -----------------------------
groq_model = os.getenv("GROQ_MODEL")

if not groq_model:
    try:
        groq_model = st.secrets["GROQ_MODEL"]
    except Exception:
        groq_model = "llama-3.3-70b-versatile"

# -----------------------------
# ChromaDB / Embedding setup
# -----------------------------
DB_FOLDER = "vector_db"
KB_FOLDER = "knowledge_base"
COLLECTION_NAME = "business_statistics_kb"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def build_vector_db_if_needed():
    db_path = Path(DB_FOLDER)
    kb_path = Path(KB_FOLDER)

    db_path.mkdir(exist_ok=True)

    if not kb_path.exists():
        raise ValueError("knowledge_base folder not found.")

    markdown_files = list(kb_path.glob("*.md"))

    if not markdown_files:
        raise ValueError("No Markdown files found inside knowledge_base folder.")

    client = chromadb.PersistentClient(path=DB_FOLDER)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    existing_count = collection.count()

    if existing_count > 0:
        print(f"Using existing ChromaDB collection with {existing_count} documents.")
        return client, collection

    print("Vector DB is empty. Building from knowledge_base files...")

    documents = []

    for file_path in markdown_files:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        if content.strip():
            documents.append(
                {
                    "id": file_path.stem,
                    "text": content,
                    "source": file_path.name,
                }
            )

    if not documents:
        raise ValueError("Knowledge base files exist but no readable content was found.")

    for doc in documents:
        embedding = embedding_model.encode(doc["text"]).tolist()

        collection.upsert(
            ids=[doc["id"]],
            documents=[doc["text"]],
            embeddings=[embedding],
            metadatas=[{"source": doc["source"]}],
        )

    final_count = collection.count()
    print(f"Vector DB build complete. Ingested {final_count} documents.")

    return client, collection


client, collection = build_vector_db_if_needed()

# -----------------------------
# Guardrail keyword lists
# -----------------------------
OUT_OF_SCOPE_KEYWORDS = [
    "attendance",
    "fees",
    "fee",
    "marks",
    "grade",
    "increase my marks",
    "exam answer",
    "assignment cheating",
    "cheat",
    "write my exam",
    "personal problem",
    "harassment",
    "counselling",
    "counseling",
    "hostel",
    "admission",
    "scholarship",
    "placement",
    "library fine",
    "neural network",
    "neural networks",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai model",
    "classification model",
    "random forest",
    "decision tree",
    "support vector machine",
]


GREETINGS = [
    "hi",
    "hii",
    "hello",
    "hey",
    "helo",
    "good morning",
    "good afternoon",
    "good evening",
    "namaste",
]


THANKS = [
    "thanks",
    "thank you",
    "thankyou",
    "thx",
    "ok thanks",
    "okay thanks",
]


IDENTITY_QUESTIONS = [
    "who are you",
    "what are you",
    "are you a chatbot",
    "are you an ai",
    "what is this bot",
    "what is this chatbot",
    "tell me about yourself",
]


CAPABILITY_QUESTIONS = [
    "what can you do",
    "how can you help",
    "what do you do",
    "what questions can i ask",
    "which topics do you cover",
    "what topics do you cover",
    "what can i ask you",
    "help me",
]


# -----------------------------
# Helper functions
# -----------------------------
def normalize_text(text):
    return text.lower().strip().replace("?", "").replace(".", "")


def contains_any_keyword(text, keyword_list):
    return any(keyword in text for keyword in keyword_list)


def is_greeting(text):
    clean_text = normalize_text(text)
    return clean_text in GREETINGS


def is_thanks(text):
    clean_text = normalize_text(text)
    return clean_text in THANKS


def is_identity_question(text):
    clean_text = normalize_text(text)
    return contains_any_keyword(clean_text, IDENTITY_QUESTIONS)


def is_capability_question(text):
    clean_text = normalize_text(text)
    return contains_any_keyword(clean_text, CAPABILITY_QUESTIONS)


def is_out_of_scope(text):
    clean_text = normalize_text(text)
    return contains_any_keyword(clean_text, OUT_OF_SCOPE_KEYWORDS)


# -----------------------------
# Main answer function
# -----------------------------
@observe_generation
def generate_answer(student_question):
    start_time=time.time()
    feedback_id = str(uuid.uuid4())
    question_clean = normalize_text(student_question)

    # 1. Empty input
    if not question_clean:
        return {
            "answer": "Please ask a Business Statistics question so I can help you.",
            "source": "Input clarity rule triggered",
        }

    # 2. Greetings
    if is_greeting(student_question):
        return {
            "answer": (
                "Hello! I am your AI Student Doubt Resolution Bot for Business Statistics. "
                "You can ask me questions on topics like mean, median, mode, probability, "
                "standard deviation, hypothesis testing, p-value, correlation, and regression."
            ),
            "source": "Greeting rule triggered",
        }

    # 3. Identity questions
    if is_identity_question(student_question):
        return {
            "answer": (
                "I am an AI Student Doubt Resolution Bot designed to help students understand "
                "Business Statistics concepts. I use a curated course knowledge base and provide "
                "beginner-friendly explanations with course references."
            ),
            "source": "Identity rule triggered",
        }

    # 4. Capability questions
    if is_capability_question(student_question):
        return {
            "answer": (
                "I can help you with Business Statistics doubts such as:\n\n"
                "- Mean, median, and mode\n"
                "- Variance and standard deviation\n"
                "- Basic and conditional probability\n"
                "- Normal distribution\n"
                "- Hypothesis testing\n"
                "- P-value\n"
                "- Correlation\n"
                "- Simple linear regression\n\n"
                "Please ask a specific Business Statistics question, for example: "
                "'What is p-value?' or 'What is conditional probability?'"
            ),
            "source": "Capability rule triggered",
        }

    # 5. Thanks
    if is_thanks(student_question):
        return {
            "answer": (
                "You're welcome! Ask me another Business Statistics question whenever you are ready."
            ),
            "source": "Courtesy rule triggered",
        }

    # 6. Very short unclear input
    if len(question_clean) < 4:
        return {
            "answer": (
                "Please ask a complete Business Statistics question so I can help you properly. "
                "For example: 'What is p-value?' or 'What is conditional probability?'"
            ),
            "source": "Input clarity rule triggered",
        }

    # 7. Out-of-scope guardrail
    if is_out_of_scope(student_question):
        return {
            "answer": (
                "This question is outside my Business Statistics learning scope. "
                "Please contact your faculty or academic support team for this."
            ),
            "source": "Escalation rule triggered",
        }

    # 8. RAG retrieval
    question_embedding = embedding_model.encode(student_question).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3,
    )

    retrieved_docs = results.get("documents", [[]])[0]
    retrieved_metadatas = results.get("metadatas", [[]])[0]

    if not retrieved_docs:
        return {
            "answer": (
                "I could not find this topic in my approved Business Statistics knowledge base. "
                "Please ask your faculty or academic support team for guidance."
            ),
            "source": "No relevant source found",
        }

    context = "\n\n".join(retrieved_docs)

    source_files = []
    for metadata in retrieved_metadatas:
        if metadata and "source" in metadata:
            source_files.append(metadata["source"])

    unique_sources = list(dict.fromkeys(source_files))
    source_text = ", ".join(unique_sources) if unique_sources else "Knowledge base"

    # 9. LLM response
    system_prompt = """
You are an AI Student Doubt Resolution Bot for Business Statistics.

You must follow these rules:
- Answer only using the provided course context.
- Do not answer questions outside Business Statistics.
- Do not help with cheating, exams, marks, fees, attendance, admissions, or personal issues.
- Use simple beginner-friendly language.
- If the answer is not available in the context, say that the topic is not available in the approved knowledge base.
- Do not invent facts or sources.
- Keep the answer clear, structured, and useful for first-year MBA or undergraduate management students.

For numerical Business Statistics questions:
- Solve step by step.
- Clearly show the formula used.
- Substitute the given values into the formula.
- Show intermediate calculation steps where useful.
- Clearly state the final answer.
- If required data is missing, ask the student for the missing value instead of assuming.
- Do not invent numbers, examples, or missing values.
- Keep calculations beginner-friendly and easy to follow.

Use this exact answer format:

### 1. Short Answer
Write 1-2 simple sentences.

### 2. Simple Explanation
Explain in beginner-friendly language.

### 3. Formula or Steps
Give formula, rule, or steps if applicable. If not applicable, write: Not applicable.

### 4. Example
Give a small simple example.

### 5. Course Reference
Course Reference: <most relevant topic/source from retrieved context>

### 6. Follow-up Question
Ask one useful learning question.
"""

    user_prompt = f"""
Student question:
{student_question}

Course context:
{context}
"""

    try:
        response = llm_client.chat.completions.create(
            model=groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=700,
        )

        answer = response.choices[0].message.content

        latency_ms = int((time.time() - start_time) * 1000)

        usage = getattr(response, "usage", None)

        input_tokens = getattr(usage, "prompt_tokens", None) if usage else None
        output_tokens = getattr(usage, "completion_tokens", None) if usage else None
        total_tokens = getattr(usage, "total_tokens", None) if usage else None

        
        trace_id = get_active_trace_id()

        flush_langfuse()
        

        return {
            "answer": answer,
            "source": source_text,
            "model_used": groq_model,
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "feedback_id": feedback_id,
        }

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)

        error_answer = (
            "I faced a technical issue while generating the answer. "
            "Please try again after some time."
        )

        trace_id = get_active_trace_id()
        
        flush_langfuse()

        return {
            "answer": error_answer,
            "source": f"LLM error: {str(e)}",
            "model_used": groq_model,
            "latency_ms": latency_ms,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "feedback_id": feedback_id,
        }