import os
import streamlit as st
from dotenv import load_dotenv
from langfuse import get_client, observe

load_dotenv()


def get_secret_value(key: str, default=None):
    """
    Reads configuration from local .env first, then Streamlit secrets.
    """
    value = os.getenv(key)

    if value:
        return value

    try:
        return st.secrets[key]
    except Exception:
        return default


# Langfuse configuration
os.environ["LANGFUSE_PUBLIC_KEY"] = get_secret_value("LANGFUSE_PUBLIC_KEY", "")
os.environ["LANGFUSE_SECRET_KEY"] = get_secret_value("LANGFUSE_SECRET_KEY", "")
os.environ["LANGFUSE_HOST"] = get_secret_value(
    "LANGFUSE_BASE_URL",
    get_secret_value("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

langfuse_client = get_client()


def is_langfuse_configured():
    return bool(
        os.environ.get("LANGFUSE_PUBLIC_KEY")
        and os.environ.get("LANGFUSE_SECRET_KEY")
        and os.environ.get("LANGFUSE_HOST")
    )


def flush_langfuse():
    if is_langfuse_configured():
        try:
            langfuse_client.flush()
        except Exception as e:
            print(f"Langfuse flush failed: {e}")


def observe_generation(func):
    """
    Decorator wrapper for tracing the main chatbot answer function.
    """
    if is_langfuse_configured():
        return observe(name="student-bot-chat")(func)

    return func


def get_active_trace_id():
    """
    Returns the active Langfuse trace ID created by the @observe decorator.
    """
    try:
        return langfuse_client.get_current_trace_id()
    except Exception as e:
        print(f"Could not get active Langfuse trace ID: {e}")
        return None


def log_user_feedback(trace_id, feedback_value, comment=None):
    """
    Logs user feedback for a chatbot response.
    feedback_value should be 'helpful' or 'not_helpful'.
    """

    if not is_langfuse_configured():
        return None

    if not trace_id:
        print("Langfuse feedback logging skipped: trace_id missing")
        return None

    try:
        score_value = 1 if feedback_value == "helpful" else 0

        langfuse_client.create_score(
            trace_id=trace_id,
            name="user_feedback",
            value=score_value,
            comment=comment or feedback_value,
        )

        flush_langfuse()
        return True

    except Exception as e:
        print(f"Langfuse feedback logging failed: {e}")
        return None