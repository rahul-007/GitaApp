"""Factory functions for Groq chat models via LangChain."""
from langchain_groq import ChatGroq

from src.config import GROQ_TEXT_MODEL, GROQ_VISION_MODEL


def get_vision_llm(temperature: float = 0.0) -> ChatGroq:
    """Multimodal model used for OCR + language detection on sloka photos."""
    return ChatGroq(model=GROQ_VISION_MODEL, temperature=temperature)


def get_text_llm(temperature: float = 0.2) -> ChatGroq:
    """Text-only model used for translation and explanation/summarization."""
    return ChatGroq(model=GROQ_TEXT_MODEL, temperature=temperature)
