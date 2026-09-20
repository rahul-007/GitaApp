"""End-to-end pipeline orchestration: image -> OCR -> grounded translation + explanation."""
import time

from src.explain import explain_sloka
from src.logging_config import get_logger
from src.ocr import extract_text_from_image
from src.translate import detect_language

logger = get_logger(__name__)


def run_pipeline(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """Run the full sloka-understanding pipeline on an uploaded image.

    Returns a dict with keys: detected_language, extracted_text, translation,
    explanation, sources, timings (seconds per step).
    """
    timings = {}
    logger.info("Pipeline started")

    start = time.perf_counter()
    ocr_result = extract_text_from_image(image_bytes, mime_type=mime_type)
    timings["ocr"] = round(time.perf_counter() - start, 2)
    logger.info("Step 1/2 OCR done in %.2fs", timings["ocr"])

    start = time.perf_counter()
    explanation_result = explain_sloka(
        ocr_result["extracted_text"], ocr_result["detected_language"]
    )
    timings["explanation"] = round(time.perf_counter() - start, 2)
    logger.info("Step 2/2 translation+explanation done in %.2fs", timings["explanation"])

    logger.info("Pipeline finished (total=%.2fs)", sum(timings.values()))

    return {
        "detected_language": ocr_result["detected_language"],
        "extracted_text": ocr_result["extracted_text"],
        "translation": explanation_result["translation"],
        "explanation": explanation_result["explanation"],
        "sources": explanation_result["sources"],
        "timings": timings,
    }


def run_pipeline_from_text(text: str) -> dict:
    """Run the sloka-understanding pipeline on typed/pasted text (no OCR step).

    Returns a dict with keys: detected_language, extracted_text, translation,
    explanation, sources, timings (seconds per step).
    """
    timings = {}
    logger.info("Text pipeline started")

    start = time.perf_counter()
    detected_language = detect_language(text)
    timings["language_detection"] = round(time.perf_counter() - start, 2)
    logger.info("Step 1/2 language detection done in %.2fs", timings["language_detection"])

    start = time.perf_counter()
    explanation_result = explain_sloka(text, detected_language)
    timings["explanation"] = round(time.perf_counter() - start, 2)
    logger.info("Step 2/2 translation+explanation done in %.2fs", timings["explanation"])

    logger.info("Text pipeline finished (total=%.2fs)", sum(timings.values()))

    return {
        "detected_language": detected_language,
        "extracted_text": text,
        "translation": explanation_result["translation"],
        "explanation": explanation_result["explanation"],
        "sources": explanation_result["sources"],
        "timings": timings,
    }
