import os

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
from governance import (
    get_review_priority,
    ROOT_CAUSE_CATEGORIES,
)
from backend.governance_store import (
    initialize_database,
    create_review,
    list_reviews,
    update_root_cause,
    resolve_review,
)
from backend.visuals_api import detect_visual_type
from backend.admin_auth import (
    authenticate_admin,
    create_admin_token,
    require_admin,
    validate_admin_configuration,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    validate_admin_configuration()
    yield


app = FastAPI(
    title="AI Student Doubt Resolution Bot API",
    version="1.3.0",
    lifespan=lifespan,
)


allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    trace_id: str
    feedback_value: str
    comment: str | None = None
    question: str | None = None


class LearningHintRequest(BaseModel):
    question: str


class LearningCompareRequest(BaseModel):
    question: str
    student_attempt: str
    full_solution: str


class RootCauseUpdateRequest(BaseModel):
    root_cause: str


class AdminLoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Student Doubt Resolution Bot API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
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

    visual_type = detect_visual_type(
        question=request.question,
        answer=result.get("answer") or "",
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
        "visual_type": visual_type,
    }


@app.post("/api/feedback")
def feedback(request: FeedbackRequest):
    normalized_feedback = request.feedback_value.lower().strip()

    if normalized_feedback not in {
        "helpful",
        "not_helpful",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "feedback_value must be "
                "'helpful' or 'not_helpful'"
            ),
        )

    log_user_feedback(
        trace_id=request.trace_id,
        feedback_value=normalized_feedback,
        comment=request.comment,
    )

    governance_review_id = None

    if normalized_feedback == "not_helpful":
        review_priority = get_review_priority(
            "not_helpful"
        )

        governance_review_id = create_review(
            trace_id=request.trace_id,
            question=request.question,
            feedback_value=normalized_feedback,
            review_priority=review_priority,
        )

    return {
        "status": "success",
        "message": "Feedback recorded",
        "trace_id": request.trace_id,
        "feedback_value": normalized_feedback,
        "governance_review_id": governance_review_id,
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
def learning_compare(
    request: LearningCompareRequest,
):
    reflection = compare_student_attempt(
        student_question=request.question,
        student_attempt=request.student_attempt,
        full_solution=request.full_solution,
    )

    return {
        "status": "success",
        "reflection": reflection,
    }


@app.post("/api/admin/login")
def admin_login(request: AdminLoginRequest):
    if not authenticate_admin(
        request.username,
        request.password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin username or password.",
        )

    token, expires_at = create_admin_token(
        request.username
    )

    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
    }


@app.get("/api/admin/reviews")
def admin_list_reviews(
    _admin: dict = Depends(require_admin),
):
    return {
        "reviews": list_reviews(),
    }


@app.patch("/api/admin/reviews/{review_id}/root-cause")
def admin_update_root_cause(
    review_id: int,
    request: RootCauseUpdateRequest,
    _admin: dict = Depends(require_admin),
):
    if request.root_cause not in ROOT_CAUSE_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid root cause. "
                "Use one of the approved governance categories."
            ),
        )

    update_root_cause(
        review_id=review_id,
        root_cause=request.root_cause,
    )

    return {
        "status": "success",
        "message": "Root cause classification saved",
        "review_id": review_id,
        "root_cause": request.root_cause,
        "review_status": "Under Review",
    }


@app.patch("/api/admin/reviews/{review_id}/resolve")
def admin_resolve_review(
    review_id: int,
    _admin: dict = Depends(require_admin),
):
    resolve_review(
        review_id=review_id
    )

    return {
        "status": "success",
        "message": "Governance review resolved",
        "review_id": review_id,
        "review_status": "Resolved",
    }
