# GitaApp

A Streamlit web app that helps readers understand Bhagavad Gita slokas
written in Hindi or Bangla — by photo, or by typed text — through
AI-powered OCR, web-grounded translation, and plain-English explanation.

## What is this app about?

Many people have access to a physical copy of the Bhagavad Gita in Hindi
or Bangla but aren't fluent enough in either script to read it comfortably,
and even when they can read the words, the philosophical meaning of a
sloka (verse) is often hard to grasp without commentary. GitaApp bridges
that gap: point your phone camera (or upload a photo) at a page, crop
down to the verse you care about, and get back the original text, an
English translation, and a simple explanation grounded in real commentary
from the web — complete with source links.

## What problem are we solving?

- **Language barrier** — the reader isn't comfortable reading Hindi or
  Bangla script, so the sloka needs to be transcribed and translated to
  English.
- **Comprehension barrier** — even in English, sloka language is dense
  and philosophical; a plain-language explanation is needed.
- **Trust/accuracy** — a pure LLM translation/explanation can hallucinate
  or misinterpret a verse, so the explanation is grounded in real web
  search results (via Tavily) with cited sources instead of relying on
  the model's memory alone.

## Features / use cases

- **Multiple input modes**: capture a photo with your camera, upload an
  existing image, or type/paste the sloka text directly.
- **Crop before you analyze**: after selecting an image, drag a crop box
  around just the verse so OCR isn't distracted by surrounding page
  content (headers, footnotes, adjacent verses, etc.).
- **Automatic OCR + language detection**: a Groq vision model transcribes
  the photographed text and detects whether it's Hindi or Bangla.
- **Web-grounded translation + explanation**: rather than translating
  blind, the app searches the web for the verse's published meaning and
  asks the LLM to produce an accurate English translation and a simple,
  jargon-free explanation grounded in those results.
- **Cited sources**: every explanation lists the (de-duplicated) source
  URLs it was grounded on, so you can read further.
- **Session history**: previous lookups in the same browser session are
  kept in a collapsible list (cleared on refresh — no accounts, no
  persistent storage).
- **Step-by-step debug timings**: each result includes a breakdown of how
  long OCR/search/explanation took, useful for troubleshooting.

## Tech stack

| Layer | Technology |
|---|---|
| UI / app framework | [Streamlit](https://streamlit.io/) |
| Image cropping | [streamlit-cropper](https://github.com/turner-anderson/streamlit-cropper) + Pillow |
| LLM provider | [Groq](https://groq.com/) (open-weight models, e.g. Qwen for vision/OCR, GPT-OSS for text) |
| LLM orchestration | [LangChain](https://www.langchain.com/) (`langchain-groq`) |
| Web search grounding | [Tavily](https://tavily.com/) (`langchain-tavily`) |
| Observability | Python `logging` (see `src/logging_config.py`) + optional [LangSmith](https://smith.langchain.com/) tracing |
| Config/secrets | `python-dotenv` locally, `st.secrets` on Streamlit Community Cloud |

## High-level architecture

```
Camera / upload / typed text (Streamlit UI, app.py)
        │ (image only)
        ▼
Crop tool (streamlit-cropper) - isolate just the sloka
        │
        ▼
OCR + language detection - Groq vision model (src/ocr.py)
        │
        ▼
Tavily web search - query built from the original sloka text,
explicitly asking for its plain English meaning (src/explain.py)
        │
        ▼
Groq text model summarizes the search results into:
  - an English translation
  - a plain-English explanation
(src/explain.py)
        │
        ▼
Result display: original text, translation, explanation,
de-duplicated source links, step timings (app.py)
```

Typed-text input skips the OCR/crop steps and goes straight from language
detection to the search-grounded translation/explanation step.

All LLM calls go through LangChain (`langchain-groq`) and are traced in
LangSmith when `LANGCHAIN_API_KEY` is set. Detailed step-by-step logs are
printed via `src/logging_config.py`.

See [project_context.md](project_context.md) for the full requirements/decisions log,
and [problem.md](problem.md) for the original problem statement.

## Setup

Create a `.env` file in the project root (or copy `.env.example`) with the
following content:

```bash
GROQ_API_KEY=your-groq-api-key
TAVILY_API_KEY=your-tavily-api-key

# Optional: enables LangSmith tracing for all LLM calls
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=gita-app
```

- `GROQ_API_KEY` (required) — from [console.groq.com](https://console.groq.com/keys), used for OCR/vision and text LLM calls.
- `TAVILY_API_KEY` (required) — from [app.tavily.com](https://app.tavily.com/), used for web search grounding.
- `LANGCHAIN_API_KEY` / `LANGCHAIN_PROJECT` (optional) — from [smith.langchain.com](https://smith.langchain.com/), only needed if you want LangSmith call tracing; omit them and the app runs fine without tracing.

Then install dependencies and run the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

For deployment on Streamlit Community Cloud, set the same keys under
**App settings → Secrets** (see `.streamlit/secrets.toml.example`).
