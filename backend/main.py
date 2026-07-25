from fastapi import FastAPI
from pydantic import BaseModel

from rag_engine import generate_answer, compare_student_attempt
from observability import (
    create_langfuse_trace_id,
    log_user_feedback,
)
from learning_mode import (
    is_problem_solving_question,
    get_hint_message,
)


class ChatRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    trace_id: str
    feedback_value: str
    comment: str | None = None


class LearningHintRequest(BaseModel):
    question: str


class LearningCompareRequest(BaseModel):
    question: str
    student_attempt: str
    full_solution: str


app = FastAPI(
    title="AI Student Doubt Resolution Bot API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Student Doubt Resolution Bot API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/chat")
def chat(request: ChatRequest):
    trace_id = create_langfuse_trace_id()

    if trace_id:
        result = generate_answer(
            request.question,
            langfuse_trace_id=trace_id,
        )
    else:
        result = generate_answer(
            request.question
        )

    return {
        "feedback_id": trace_id,
        "answer": result.get("answer"),
        "source": result.get("source"),
        "model_used": result.get("model_used"),
        "routing_type": result.get("routing_type"),
        "routing_reason": result.get("routing_reason"),
        "confidence": result.get("confidence"),
        "confidence_reason": result.get("confidence_reason"),
        "latency_ms": result.get("latency_ms"),
        "input_tokens": result.get("input_tokens"),
        "output_tokens": result.get("output_tokens"),
    }


@app.post("/api/feedback")
def feedback(request: FeedbackRequest):
    normalized_feedback = request.feedback_value.lower().strip()

    if normalized_feedback not in {
        "helpful",
        "not_helpful",
    }:
        return {
            "status": "error",
            "message": (
                "feedback_value must be "
                "'helpful' or 'not_helpful'"
            ),
        }

    log_user_feedback(
        trace_id=request.trace_id,
        feedback_value=normalized_feedback,
        comment=request.comment,
    )

    return {
        "status": "success",
        "message": "Feedback recorded",
        "trace_id": request.trace_id,
        "feedback_value": normalized_feedback,
    }


@app.post("/api/learning/hint")
def learning_hint(request: LearningHintRequest):
    problem_solving = is_problem_solving_question(
        request.question
    )

    if not problem_solving:
        return {
            "problem_solving": False,
            "hint": None,
            "message": (
                "This question does not require the "
                "try-first learning flow."
            ),
        }

    hint = get_hint_message(
        request.question
    )

    return {
        "problem_solving": True,
        "hint": hint,
        "message": (
            "Encourage the student to try the problem "
            "before requesting the full solution."
        ),
    }


@app.post("/api/learning/compare")
def learning_compare(request: LearningCompareRequest):
    feedback = compare_student_attempt(
        student_question=request.question,
        student_attempt=request.student_attempt,
        full_solution=request.full_solution,
    )

    return {
        "status": "success",
        "reflection": feedback,
    }