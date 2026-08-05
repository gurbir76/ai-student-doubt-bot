import os
import re
import time
import streamlit as st
import chromadb

from pathlib import Path
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

from observability import observe_generation, flush_langfuse
from model_router import route_model, BASIC_MODEL, ADVANCED_MODEL
from confidence import calculate_response_confidence
from hallucination_score import (
    calculate_grounding_similarity,
    calculate_question_source_similarity,
    calculate_runtime_assurance,
)


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
        print(
            f"Using existing ChromaDB collection with "
            f"{existing_count} documents."
        )
        return client, collection

    print("Vector DB is empty. Building from knowledge_base files...")

    documents = []

    for file_path in markdown_files:
        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if content.strip():
            documents.append(
                {
                    "id": file_path.stem,
                    "text": content,
                    "source": file_path.name,
                }
            )

    if not documents:
        raise ValueError(
            "Knowledge base files exist but no readable content was found."
        )

    for doc in documents:
        embedding = embedding_model.encode(doc["text"]).tolist()

        collection.upsert(
            ids=[doc["id"]],
            documents=[doc["text"]],
            embeddings=[embedding],
            metadatas=[
                {
                    "source": doc["source"]
                }
            ],
        )

    final_count = collection.count()

    print(
        f"Vector DB build complete. "
        f"Ingested {final_count} documents."
    )

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
    """
    Normalize natural-language and compact statistical notation so
    topic detection works for inputs such as H0, H1, μ, α and z-score.
    """
    normalized = text.lower().strip()

    symbol_replacements = {
        "μ": " mu ",
        "α": " alpha ",
        "≠": " not equal ",
        "≤": " less than or equal ",
        "≥": " greater than or equal ",
        "–": "-",
        "—": "-",
    }

    for symbol, replacement in symbol_replacements.items():
        normalized = normalized.replace(symbol, replacement)

    normalized = normalized.replace("h₀", " h0 ")
    normalized = normalized.replace("h₁", " h1 ")
    normalized = normalized.replace("p–value", "p-value")
    normalized = normalized.replace("z–score", "z-score")

    normalized = re.sub(r"[^a-z0-9+\-=/ ]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def contains_any_keyword(text, keyword_list):
    return any(
        keyword in text
        for keyword in keyword_list
    )


def is_greeting(text):
    clean_text = normalize_text(text)
    return clean_text in GREETINGS


def is_thanks(text):
    clean_text = normalize_text(text)
    return clean_text in THANKS


def is_identity_question(text):
    clean_text = normalize_text(text)

    return contains_any_keyword(
        clean_text,
        IDENTITY_QUESTIONS,
    )


def is_capability_question(text):
    clean_text = normalize_text(text)

    return contains_any_keyword(
        clean_text,
        CAPABILITY_QUESTIONS,
    )


def is_out_of_scope(text):
    clean_text = normalize_text(text)

    return contains_any_keyword(
        clean_text,
        OUT_OF_SCOPE_KEYWORDS,
    )


def is_unclear_input(question: str) -> bool:
    """
    Detects very short or unclear requests that should
    not trigger RAG retrieval or an LLM call.
    """

    text = normalize_text(question)

    unclear_inputs = {
        "help",
        "question",
        "i need help",
    }

    return text in unclear_inputs


def is_obviously_out_of_scope(question: str) -> bool:
    """
    Detects obvious non-Business Statistics questions
    before RAG retrieval and LLM execution.
    """

    text = normalize_text(question)

    out_of_scope_keywords = [
        "cricket",
        "football",
        "sports score",
        "latest score",
        "weather",
        "stock price",
        "share price",
        "python program",
        "python code",
        "build a website",
        "create a website",
        "html code",
        "javascript",
        "java program",
        "movie",
        "recipe",
    ]

    return any(
        keyword in text
        for keyword in out_of_scope_keywords
    )


def is_numerical_statistics_question(question: str) -> bool:
    """
    Detect a worked numerical statistics question.

    This supports assurance scoring but does not independently prove
    that the final calculation is correct.
    """
    text = normalize_text(question)

    has_number = bool(re.search(r"\d", text))
    numerical_cues = [
        "calculate",
        "find",
        "compute",
        "test h0",
        "test whether",
        "z-score",
        "z score",
        "critical value",
        "sample mean",
        "population standard deviation",
        "significance level",
        "probability",
        "variance",
        "standard deviation",
        "mean",
        "median",
        "mode",
    ]

    return has_number and any(
        cue in text
        for cue in numerical_cues
    )


def has_structured_calculation_evidence(answer: str) -> bool:
    """
    Check whether a numerical answer shows formula-based working
    instead of only stating an unsupported final value.
    """
    text = (answer or "").lower()

    has_number = bool(re.search(r"\d", text))
    has_operator = bool(
        re.search(r"[=+\-*/√]|\bsqrt\b", text)
    )
    has_working_language = any(
        cue in text
        for cue in [
            "formula",
            "substitute",
            "calculation",
            "critical value",
            "therefore",
            "reject",
            "fail to reject",
            "final answer",
        ]
    )

    return has_number and has_operator and has_working_language


def get_preferred_sources(question: str):
    """
    Returns a list of the most relevant knowledge-base filenames
    for clearly identified Business Statistics topics.

    Supports multi-topic questions such as:
    "What is the difference between correlation and regression?"
    """
    text = normalize_text(question)

    topic_source_map = {
        "standard deviation": "03_variance_standard_deviation.md",
        "conditional probability": "05_conditional_probability.md",
        "normal distribution": "06_normal_distribution.md",
        "z-score": "06_normal_distribution.md",
        "z score": "06_normal_distribution.md",
        "hypothesis testing": "07_hypothesis_testing.md",
        "hypothesis test": "07_hypothesis_testing.md",
        "null hypothesis": "07_hypothesis_testing.md",
        "alternative hypothesis": "07_hypothesis_testing.md",
        "type i error": "07_hypothesis_testing.md",
        "type 1 error": "07_hypothesis_testing.md",
        "type ii error": "07_hypothesis_testing.md",
        "type 2 error": "07_hypothesis_testing.md",
        "critical value": "07_hypothesis_testing.md",
        "significance level": "07_hypothesis_testing.md",
        "h0": "07_hypothesis_testing.md",
        "h1": "07_hypothesis_testing.md",
        "alpha": "07_hypothesis_testing.md",
        "p-value": "08_p_value.md",
        "p value": "08_p_value.md",
        "linear regression": "10_simple_linear_regression.md",
        "correlation": "09_correlation.md",
        "regression": "10_simple_linear_regression.md",
        "variance": "03_variance_standard_deviation.md",
        "probability": "04_basic_probability.md",
        "arithmetic mean": "02_mean_median_mode.md",
        "median": "02_mean_median_mode.md",
        "mode": "02_mean_median_mode.md",
        "mean": "02_mean_median_mode.md",
    }

    matched_sources = []

    sorted_topics = sorted(
        topic_source_map.keys(),
        key=len,
        reverse=True,
    )

    for topic in sorted_topics:
        # Match complete topic terms only. This prevents false matches
        # such as "mode" inside the word "model".
        topic_pattern = rf"(?<![a-z0-9]){re.escape(topic)}(?![a-z0-9])"

        if re.search(topic_pattern, text):
            source = topic_source_map[topic]

            if source not in matched_sources:
                matched_sources.append(source)

    return matched_sources


def compare_student_attempt(
    student_question: str,
    student_attempt: str,
    full_solution: str,
):
    """
    Gives formative feedback on a student's attempt after the student
    has chosen to compare it with the full solution.

    This is intentionally not a grading function. It gives supportive
    feedback about the approach, one improvement area, and a next step.
    """

    if not student_attempt or not student_attempt.strip():
        return None

    system_prompt = """
        You are a careful and supportive Business Statistics tutor.

        Compare a student's attempt with the reference solution.
        Your purpose is formative learning feedback, not grading.

        IMPORTANT NUMERICAL VERIFICATION RULES:
        - Independently recompute every arithmetic step in the student's attempt.
        - Never say a calculation is correct unless you have verified it yourself.
        - Compare each numerical value with the reference solution.
        - Identify the FIRST incorrect step clearly.
        - If more than one error exists, mention the important errors concisely.
        - Do not assume that an intermediate result is correct just because the student's method looks reasonable.

        General rules:
        - Do not give marks, percentages, grades, or pass/fail labels.
        - Do not simply repeat the full solution.
        - Be encouraging but honest.
        - Focus on the student's reasoning and method.
        - Praise only steps that are actually correct.
        - If the attempt is partly correct, identify exactly what is correct and what needs correction.
        - If the attempt is incorrect, point to the first important misconception or calculation error.
        - Keep the feedback concise and beginner-friendly.

        Use exactly this format:

        ### Reflection on Your Attempt
        **What you did well:** <one verified correct point, or "You identified the correct general approach" if only the method was right>

        **What to revisit:** <specific verified error or errors>

        **Next step:** <one short learning action>
        """

    user_prompt = f"""
Student question:
{student_question}

Student attempt:
{student_attempt}

Reference solution:
{full_solution}
"""

    try:
        response = llm_client.chat.completions.create(
            model=ADVANCED_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=280,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Student attempt comparison failed: {type(e).__name__}: {e}")
        return (
            "### Reflection on Your Attempt\n"
            "I could not compare your attempt right now. "
            "You can still compare your steps with the full solution above."
        )


# -----------------------------
# Main answer function
# -----------------------------
@observe_generation
def generate_answer(student_question, langfuse_trace_id=None):

    start_time = time.time()

    question_clean = normalize_text(
        student_question
    )

    # -------------------------
    # 1. Empty input
    # -------------------------
    if not question_clean:
        return {
            "answer": (
                "Please ask a Business Statistics "
                "question so I can help you."
            ),
            "source": "Input clarity rule triggered",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": "Empty input",
            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 2. Greetings
    # -------------------------
    if is_greeting(student_question):
        return {
            "answer": (
                "Hello! I am your AI Student Doubt Resolution Bot "
                "for Business Statistics. You can ask me questions "
                "on topics like mean, median, mode, probability, "
                "standard deviation, hypothesis testing, p-value, "
                "correlation, and regression."
            ),
            "source": "Greeting rule triggered",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": "Greeting detected",
            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 3. Identity questions
    # -------------------------
    if is_identity_question(student_question):
        return {
            "answer": (
                "I am an AI Student Doubt Resolution Bot designed "
                "to help students understand Business Statistics "
                "concepts. I use a curated course knowledge base "
                "and provide beginner-friendly explanations with "
                "course references."
            ),
            "source": "Identity rule triggered",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": "Identity question detected",
            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 4. Capability questions
    # -------------------------
    if is_capability_question(student_question):
        return {
            "answer": (
                "I can help you with Business Statistics doubts "
                "such as:\n\n"
                "- Mean, median, and mode\n"
                "- Variance and standard deviation\n"
                "- Basic and conditional probability\n"
                "- Normal distribution\n"
                "- Hypothesis testing\n"
                "- P-value\n"
                "- Correlation\n"
                "- Simple linear regression\n\n"
                "Please ask a specific Business Statistics question, "
                "for example: 'What is p-value?' or "
                "'What is conditional probability?'"
            ),
            "source": "Capability rule triggered",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": "Capability question detected",
            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 5. Thanks
    # -------------------------
    if is_thanks(student_question):
        return {
            "answer": (
                "You're welcome! Ask me another "
                "Business Statistics question whenever "
                "you are ready."
            ),
            "source": "Courtesy rule triggered",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": "Courtesy response",
            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 6. Unclear input guardrail
    # Fixes evaluation TC15
    # -------------------------
    if is_unclear_input(student_question):
        return {
            "answer": (
                "Please ask me a specific question about "
                "Business Statistics. For example, you can ask "
                "about mean, median, probability, standard deviation, "
                "hypothesis testing, correlation, or regression."
            ),
            "source": "None",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": "Unclear or incomplete input",
            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 7. Very short unclear input
    # -------------------------
    if len(question_clean) < 4:
        return {
            "answer": (
                "Please ask a complete Business Statistics question "
                "so I can help you properly. For example: "
                "'What is p-value?' or "
                "'What is conditional probability?'"
            ),
            "source": "Input clarity rule triggered",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": "Very short input",
            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 8. Obvious out-of-scope guardrail
    # Fixes evaluation TC03 and TC06
    # -------------------------
    if is_obviously_out_of_scope(
        student_question
    ):
        return {
            "answer": (
                "This question is outside my Business Statistics "
                "learning scope. I can help with topics such as "
                "mean, median, probability, standard deviation, "
                "hypothesis testing, p-value, correlation, "
                "and regression."
            ),
            "source": "None",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": "Out-of-scope question",
            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 9. Existing out-of-scope guardrail
    # -------------------------
    if is_out_of_scope(student_question):
        return {
            "answer": (
                "This question is outside my Business Statistics "
                "learning scope. Please contact your faculty or "
                "academic support team for this."
            ),
            "source": "Escalation rule triggered",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": "Out-of-scope question",
            "latency_ms": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 10. Model routing
    # -------------------------
    routing_result = route_model(
        student_question
    )

    selected_model = routing_result.get(
        "model",
        groq_model,
    )

    routing_type = routing_result.get(
        "route",
        "default",
    )

    routing_reason = routing_result.get(
        "reason",
        "Fallback to configured Groq model",
    )

    # -------------------------
    # 11. RAG retrieval
    # -------------------------
    question_embedding = embedding_model.encode(
        student_question
    ).tolist()

    results = collection.query(
        query_embeddings=[
            question_embedding
        ],
        n_results=2,
    )

    retrieved_docs = results.get(
        "documents",
        [[]],
    )[0]

    retrieved_metadatas = results.get(
        "metadatas",
        [[]],
    )[0]

    preferred_sources = get_preferred_sources(
        student_question
    )

    if preferred_sources:
        preferred_docs = []
        preferred_metadatas = []

        # Fetch every identified topic source directly.
        # This supports multi-topic questions such as
        # correlation + regression.
        for preferred_source in preferred_sources:
            preferred_result = collection.get(
                where={
                    "source": preferred_source
                },
                include=[
                    "documents",
                    "metadatas",
                ],
            )

            documents_for_source = preferred_result.get(
                "documents",
                [],
            )

            metadatas_for_source = preferred_result.get(
                "metadatas",
                [],
            )

            for document, metadata in zip(
                documents_for_source,
                metadatas_for_source,
            ):
                if document:
                    preferred_docs.append(document)
                    preferred_metadatas.append(metadata)

        # Use direct topic matches when available.
        # Otherwise keep semantic retrieval results.
        if preferred_docs:
            retrieved_docs = preferred_docs
            retrieved_metadatas = preferred_metadatas

    if not retrieved_docs:
        return {
            "answer": (
                "I could not find this topic in my approved "
                "Business Statistics knowledge base. "
                "Please ask your faculty or academic support "
                "team for guidance."
            ),
            "source": "No relevant source found",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": (
                "No relevant knowledge-base source found"
            ),
            "latency_ms": int(
                (time.time() - start_time) * 1000
            ),
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    context = "\n\n".join(
        retrieved_docs
    )

    source_files = []

    for metadata in retrieved_metadatas:
        if metadata and "source" in metadata:
            source_files.append(
                metadata["source"]
            )

    unique_sources = list(
        dict.fromkeys(source_files)
    )

    source_text = (
        ", ".join(unique_sources)
        if unique_sources
        else "Knowledge base"
    )

    question_source_similarity = (
        calculate_question_source_similarity(
            question=student_question,
            context=context,
            embedding_model=embedding_model,
        )
    )

    # A nearest-neighbour result is not automatically a relevant result.
    #
    # Use a two-stage relevance rule:
    # - similarity >= 0.45: allow normal RAG generation;
    # - similarity 0.35-0.449 with a recognised supported topic:
    #   allow generation because direct topic routing found an approved
    #   source, even when semantic wording similarity is slightly lower;
    # - similarity < 0.35, or no recognised topic in the borderline band:
    #   block generation.
    #
    # This prevents false rejections such as "arithmetic mean" while
    # continuing to block genuinely unsupported topics.
    recognised_supported_topic = bool(
        get_preferred_sources(student_question)
    )

    should_block_for_low_relevance = (
        not recognised_supported_topic
        and question_source_similarity < 0.45
    )

    if should_block_for_low_relevance:
        latency_ms = int(
            (time.time() - start_time) * 1000
        )

        return {
            "answer": (
                "This statistical topic is not sufficiently covered "
                "in my approved Business Statistics knowledge base. "
                "I should not generate an unsupported explanation. "
                "Please ask about mean, median, mode, variance, "
                "standard deviation, probability, normal distribution, "
                "hypothesis testing, p-value, correlation, or "
                "simple linear regression."
            ),
            "source": "No relevant source found",
            "model_used": "Rule-based",
            "routing_type": "guardrail",
            "routing_reason": (
                "Unsupported topic: retrieved context was not "
                "sufficiently relevant"
            ),
            "confidence": "Not Applicable",
            "confidence_reason": (
                "The approved knowledge base did not contain "
                "sufficiently relevant evidence."
            ),
            "assurance_score": 15,
            "hallucination_risk": "High",
            "relevance_score": 0,
            "grounding_score": 0,
            "source_score": 0,
            "guardrail_score": 15,
            "question_source_similarity": round(
                question_source_similarity,
                3,
            ),
            "grounding_similarity": None,
            "assurance_reason": (
                "Question-source relevance was below the safe "
                "threshold and no recognised supported topic "
                "provided sufficient evidence, so model generation "
                "was blocked."
            ),
            "latency_ms": latency_ms,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    # -------------------------
    # 12. LLM response
    # -------------------------
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

### 1. Answer
Give a clear direct answer in 2-3 simple sentences.

### 2. Explanation
Explain the concept in beginner-friendly language using one or two short paragraphs.
Include the key idea, why it matters, and any important interpretation or limitation supported by the context.
Do not repeat the direct answer unnecessarily.

### 3. Formula or Steps
Give the formula, rule, or ordered steps if applicable.
For numerical questions, show substitution and intermediate calculations clearly.
If not applicable, write: Not applicable.

### 4. Example
If the student's question already contains a complete real-world scenario,
continue with that same scenario and briefly interpret the result.
Do not introduce an unrelated second scenario.
Only create a new practical example when the original question is conceptual
and does not already provide one.

### 5. Course Reference
Course Reference: <most relevant topic/source from retrieved context>

### 6. Follow-up Question
Ask one concise learning question that helps the student apply the concept.
"""

    user_prompt = f"""
Student question:
{student_question}

Course context:
{context}
"""

    try:
        response = (
            llm_client
            .chat
            .completions
            .create(
                model=selected_model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0,
                max_tokens=850,
            )
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        latency_ms = int(
            (time.time() - start_time) * 1000
        )

        usage = getattr(
            response,
            "usage",
            None,
        )

        input_tokens = (
            getattr(
                usage,
                "prompt_tokens",
                None,
            )
            if usage
            else None
        )

        output_tokens = (
            getattr(
                usage,
                "completion_tokens",
                None,
            )
            if usage
            else None
        )

        total_tokens = (
            getattr(
                usage,
                "total_tokens",
                None,
            )
            if usage
            else None
        )

        confidence_result = calculate_response_confidence(
            source=source_text,
            routing_type=routing_type,
            routing_reason=routing_reason,
            preferred_source_count=len(preferred_sources),
            retrieved_source_count=len(unique_sources),
        )

        grounding_similarity = calculate_grounding_similarity(
            answer=answer,
            context=context,
            embedding_model=embedding_model,
        )

        numerical_question = is_numerical_statistics_question(
            student_question
        )
        structured_calculation = (
            has_structured_calculation_evidence(answer)
        )

        assurance_result = calculate_runtime_assurance(
            source=source_text,
            question_source_similarity=question_source_similarity,
            grounding_similarity=grounding_similarity,
            guardrail_pass=True,
            recognised_topic_match=recognised_supported_topic,
            numerical_question=numerical_question,
            structured_calculation=structured_calculation,
        )

        flush_langfuse()

        return {
            "answer": answer,
            "source": source_text,
            "model_used": selected_model,
            "routing_type": routing_type,
            "routing_reason": routing_reason,
            "confidence": confidence_result["confidence"],
            "confidence_reason": confidence_result["reason"],
            "assurance_score": assurance_result["assurance_score"],
            "hallucination_risk": assurance_result["hallucination_risk"],
            "relevance_score": assurance_result["relevance_score"],
            "source_score": assurance_result["source_score"],
            "grounding_score": assurance_result["grounding_score"],
            "guardrail_score": assurance_result["guardrail_score"],
            "question_source_similarity": assurance_result[
                "question_source_similarity"
            ],
            "grounding_similarity": assurance_result["grounding_similarity"],
            "assurance_reason": assurance_result["assurance_reason"],
            "latency_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }

    except Exception as e:

        latency_ms = int(
            (time.time() - start_time) * 1000
        )

        error_answer = (
            "I faced a technical issue while generating "
            "the answer. Please try again after some time."
        )

        flush_langfuse()

        return {
            "answer": error_answer,
            "source": f"LLM error: {str(e)}",
            "model_used": selected_model,
            "routing_type": routing_type,
            "routing_reason": routing_reason,
            "latency_ms": latency_ms,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
        }