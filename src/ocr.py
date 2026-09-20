"""OCR + language detection on a photographed sloka using a Groq vision model."""
import base64
import json

from langchain_core.messages import HumanMessage

from src.groq_client import get_vision_llm
from src.logging_config import get_logger

logger = get_logger(__name__)

_PROMPT = (
    "You are an OCR assistant for the Bhagavad Gita. The attached image is a photo of a "
    "book page containing one or more slokas (verses) written in either Hindi (Devanagari) "
    "or Bangla (Bengali) script.\n\n"
    "1. Detect which script/language the text is written in (hindi or bangla).\n"
    "2. Transcribe the sloka text exactly as it appears, preserving line breaks.\n\n"
    "Respond with ONLY a JSON object, no markdown fences, in this exact shape:\n"
    '{"detected_language": "hindi" | "bangla", "extracted_text": "<verbatim transcription>"}'
)


def extract_text_from_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """Run OCR + language detection on the given image bytes.

    Returns a dict: {"detected_language": str, "extracted_text": str}
    Raises ValueError if the model response can't be parsed as the expected JSON shape.
    """
    logger.debug("Starting OCR: image size=%d bytes, mime_type=%s", len(image_bytes), mime_type)

    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_image}"

    message = HumanMessage(
        content=[
            {"type": "text", "text": _PROMPT},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]
    )

    llm = get_vision_llm()
    logger.debug("Sending OCR request to vision model")
    response = llm.invoke([message])
    raw_content = response.content
    logger.debug("Raw OCR model response: %s", raw_content)

    try:
        result = json.loads(raw_content)
        detected_language = result["detected_language"]
        extracted_text = result["extracted_text"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.error("Failed to parse OCR response as expected JSON: %s", raw_content)
        raise ValueError(f"OCR model did not return valid JSON: {exc}") from exc

    logger.info(
        "OCR complete: detected_language=%s, extracted_text_len=%d",
        detected_language,
        len(extracted_text),
    )
    return {"detected_language": detected_language, "extracted_text": extracted_text}
