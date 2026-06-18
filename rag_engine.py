import os
import streamlit as st
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

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
            documents.append({
                "id": file_path.stem,
                "text": content,
                "source": file_path.name
            })

    if not documents:
        raise ValueError("Knowledge base files exist but no readable content was found.")

    for doc in documents:
        embedding = embedding_model.encode(doc["text"]).tolist()

        collection.upsert(
            ids=[doc["id"]],
            documents=[doc["text"]],
            embeddings=[embedding],
            metadatas=[{"source": doc["source"]}]
        )

    final_count = collection.count()
    print(f"Vector DB build complete. Ingested {final_count} documents.")

    return client, collection


client, collection = build_vector_db_if_needed()

llm_client = Groq(api_key=groq_api_key)

OUT_OF_SCOPE_KEYWORDS = [
    "attendance",
    "fees",
    "marks",
    "grade",
    "increase my marks",
    "exam answer",
    "assignment cheating",
    "write my exam",
    "personal problem",
    "harassment",
    "counselling",
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

def is_out_of_scope(question):
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in OUT_OF_SCOPE_KEYWORDS)

def retrieve_context(question, top_k=3):
    query_embedding = embedding_model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    return documents, metadatas

def generate_answer(question):
    if is_out_of_scope(question):
        return {
            "answer": "This question is outside my Business Statistics learning scope. Please contact your faculty or academic support team for this.",
            "source": "Escalation rule triggered"
        }

    documents, metadatas = retrieve_context(question)

    if not documents:
        return {
            "answer": "I could not find this topic in the approved Business Statistics knowledge base. Please ask your instructor for help.",
            "source": "No matching knowledge base content"
        }

    context = "\n\n".join(documents)
    sources = ", ".join([metadata["source"] for metadata in metadatas])

    system_prompt = """
You are an AI teaching assistant for Business Statistics students.
You must answer only using the provided course context.
Your audience is first-year MBA or undergraduate management students.
Use simple beginner-friendly language.
Do not hallucinate.
If the context does not support the answer, say that the doubt should be escalated to the instructor.
Never create fake citations, fake chapter numbers, fake textbook names, or fake page numbers.

Use this exact answer format with clear headings:

### 1. Short Answer
Write 1-2 simple sentences.

### 2. Simple Explanation
Explain in beginner-friendly language.

### 3. Formula or Steps
Give formula or decision rule if applicable.

### 4. Example
Give a small simple example.

### 5. Course Reference
Write only one line in this format:
Course Reference: <most relevant topic/source from retrieved context>
Do not create extra headings under Course Reference.

### 6. Follow-up Question
Ask one useful learning question.
"""

    user_prompt = f"""
Student Question:
{question}

Course Context:
{context}
"""

    response = llm_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    return {
        "answer": response.choices[0].message.content,
        "source": sources
    }