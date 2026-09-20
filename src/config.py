"""Central configuration: loads secrets/env vars and wires up LangSmith tracing.

Works both locally (via a .env file) and on Streamlit Community Cloud (via st.secrets).
"""
import os

from dotenv import load_dotenv

load_dotenv()  # no-op if .env doesn't exist (e.g. on Streamlit Cloud)

_REQUIRED_KEYS = ["GROQ_API_KEY", "TAVILY_API_KEY"]
_OPTIONAL_LANGSMITH_KEYS = ["LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT"]


def _load_from_streamlit_secrets() -> None:
    """Copy values from st.secrets into os.environ, if Streamlit secrets are available."""
    try:
        import streamlit as st

        for key in _REQUIRED_KEYS + _OPTIONAL_LANGSMITH_KEYS:
            if key in st.secrets and not os.environ.get(key):
                os.environ[key] = str(st.secrets[key])
    except Exception:
        # No secrets.toml / not running inside Streamlit yet - fall back to env vars only.
        pass


def configure() -> None:
    """Populate os.environ from Streamlit secrets and enable LangSmith tracing if configured."""
    _load_from_streamlit_secrets()

    missing = [key for key in _REQUIRED_KEYS if not os.environ.get(key)]
    if missing:
        raise RuntimeError(
            f"Missing required API key(s): {', '.join(missing)}. "
            "Set them in .env (local) or Streamlit secrets (deployed)."
        )

    # Enable LangSmith tracing only when an API key is actually provided.
    if os.environ.get("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ.setdefault("LANGCHAIN_PROJECT", "gita-app")


GROQ_VISION_MODEL = "qwen/qwen3.8-27b"
GROQ_TEXT_MODEL = "openai/gpt-oss-120b"
