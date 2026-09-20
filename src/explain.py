"""Sloka translation + explanation: Tavily web search grounding + Groq summarization."""
import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch

from src.groq_client import get_text_llm
from src.logging_config import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are a warm, clear teacher explaining Bhagavad Gita verses to a beginner who has "
    "never studied Sanskrit scripture before. You are given the original sloka text and "
    "search results gathered about it. Using the search results as grounding (they typically "
    "contain accurate published translations/commentary), produce:\n"
    "1. An accurate English translation of the verse.\n"
    "2. A simple, plain-English explanation of its meaning and significance (a few short "
    "paragraphs, no jargon).\n"
    "If the search results don't clearly cover this verse, say so honestly and give your best "
    "effort using your own knowledge instead.\n"
    "Do NOT include a 'Sources' section, citations, or URLs anywhere in your output - sources "
    "are handled separately.\n\n"
    "Respond with ONLY a JSON object, no markdown fences, in this exact shape:\n"
    '{"translation": "<english translation>", "explanation": "<plain english explanation>"}'
)


def explain_sloka(extracted_text: str, detected_language: str, max_results: int = 5) -> dict:
    """Search the web for this sloka's meaning and produce a grounded translation + explanation.

    Returns a dict: {"translation": str, "explanation": str, "sources": list[str]}
    """
    logger.debug("Searching web for sloka commentary (max_results=%d)", max_results)

    search_tool = TavilySearch(max_results=max_results)
    query = (
        f"Bhagavad Gita sloka in {detected_language}: {extracted_text}\n"
        "What is the plain, simple English meaning and translation of this verse?"
    )
    search_results = search_tool.invoke({"query": query})["results"]
    logger.debug("Tavily returned %d results", len(search_results))

    # de-duplicate while preserving order, in case Tavily returns the same URL twice
    sources = list(dict.fromkeys(r["url"] for r in search_results if "url" in r))
    context_blocks = "\n\n".join(
        f"Source: {r.get('url', 'unknown')}\nContent: {r.get('content', '')}"
        for r in search_results
    )

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Original sloka ({detected_language}):\n{extracted_text}\n\n"
                f"Search results:\n{context_blocks}"
            )
        ),
    ]

    llm = get_text_llm()
    response = llm.invoke(messages)
    raw_content = response.content.strip()

    try:
        result = json.loads(raw_content)
        translation = result["translation"].strip()
        explanation = result["explanation"].strip()
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.error("Failed to parse explanation response as expected JSON: %s", raw_content)
        raise ValueError(f"Explanation model did not return valid JSON: {exc}") from exc

    logger.info(
        "Explanation generated (translation_len=%d, explanation_len=%d, sources=%d)",
        len(translation),
        len(explanation),
        len(sources),
    )
    return {"translation": translation, "explanation": explanation, "sources": sources}
