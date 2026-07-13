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


# Langfuse v4 uses these environment variable names
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