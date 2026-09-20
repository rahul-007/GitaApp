"""Hindi/Bangla -> English translation using a Groq text model."""
from langchain_core.messages import HumanMessage, SystemMessage

from src.groq_client import get_text_llm
from src.logging_config import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are an expert translator of classical Bhagavad Gita verses. Translate the given "
    "text into clear, natural English, preserving the verse structure/line breaks. "
    "Respond with ONLY the translated text, no extra commentary."
)

_LANGUAGE_DETECTION_PROMPT = (
    "Identify the language/script of the given Bhagavad Gita sloka text. Respond with "
    "ONLY one word: hindi, bangla, or english. If the text is already in English, "
    "respond with english."
)


def detect_language(text: str) -> str:
    """Detect whether the given typed sloka text is hindi, bangla, or english."""
    logger.debug("Detecting language of typed text (length=%d)", len(text))

    messages = [
        SystemMessage(content=_LANGUAGE_DETECTION_PROMPT),
        HumanMessage(content=text),
    ]

    llm = get_text_llm(temperature=0.0)
    response = llm.invoke(messages)
    detected_language = response.content.strip().lower()

    logger.info("Language detection complete: %s", detected_language)
    return detected_language


def translate_to_english(text: str, source_language: str) -> str:
    """Translate the given Hindi or Bangla sloka text into English."""
    logger.debug(
        "Translating text (source_language=%s, length=%d)", source_language, len(text)
    )

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Source language: {source_language}\n\nText:\n{text}"),
    ]

    llm = get_text_llm()
    response = llm.invoke(messages)
    translation = response.content.strip()

    logger.info("Translation complete (output_length=%d)", len(translation))
    logger.debug("Translation output: %s", translation)
    return translation
