"""GitaApp - Streamlit UI.

Upload/take a photo of a Bhagavad Gita sloka (Hindi/Bangla), or type it in
directly, and get an English translation plus a plain-language explanation
with sources.
"""
import hashlib
import io

import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

from src.config import configure
from src.logging_config import get_logger
from src.pipeline import run_pipeline, run_pipeline_from_text

logger = get_logger(__name__)

st.set_page_config(page_title="GitaApp", page_icon="📖", layout="centered")

try:
    configure()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []  # session-only, cleared on refresh
if "show_input_options" not in st.session_state:
    st.session_state.show_input_options = False
if "crop_source_hash" not in st.session_state:
    st.session_state.crop_source_hash = None
if "cropped_bytes" not in st.session_state:
    st.session_state.cropped_bytes = None

st.title("📖 GitaApp")
st.caption(
    "Provide a Bhagavad Gita sloka (Hindi or Bangla) - by photo or typed text - to "
    "get an English translation and a simple explanation."
)

image_file = None
typed_text = None

if not st.session_state.show_input_options:
    if st.button("📤 Provide a sloka", type="primary"):
        st.session_state.show_input_options = True
        st.rerun()
else:
    input_mode = st.radio(
        "How would you like to provide the sloka?",
        ["📷 Use camera", "🖼️ Upload from device", "⌨️ Enter text"],
        horizontal=True,
    )
    if input_mode == "📷 Use camera":
        image_file = st.camera_input("Capture the sloka")
    elif input_mode == "🖼️ Upload from device":
        image_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    else:
        typed_text = st.text_area(
            "Type or paste the sloka text (Hindi, Bangla, or English)"
        )

    if st.button("Cancel"):
        st.session_state.show_input_options = False
        st.rerun()


if image_file is not None:
    raw_bytes = image_file.getvalue()
    source_hash = hashlib.sha256(raw_bytes).hexdigest()

    if st.session_state.crop_source_hash != source_hash:
        # a new/changed image invalidates any previously confirmed crop
        st.session_state.crop_source_hash = source_hash
        st.session_state.cropped_bytes = None

    st.markdown("**Drag to crop just the sloka text**")
    pil_image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    cropped_image = st_cropper(
        pil_image,
        realtime_update=True,
        box_color="#4A90D9",
        aspect_ratio=None,
        return_type="image",
    )
    st.image(cropped_image, caption="Cropped preview", use_container_width=True)

    if st.button("Use this crop"):
        buf = io.BytesIO()
        cropped_image.save(buf, format="PNG")
        st.session_state.cropped_bytes = buf.getvalue()
        st.success("Crop saved. You can now analyze the sloka below.")

    if st.session_state.cropped_bytes is not None:
        if st.button("Understand this sloka", type="primary"):
            with st.spinner("Reading, translating, and explaining the sloka..."):
                try:
                    result = run_pipeline(
                        st.session_state.cropped_bytes, mime_type="image/png"
                    )
                except Exception:
                    logger.exception("Pipeline failed")
                    st.error(
                        "Something went wrong while processing this image. "
                        "Please try again with a clearer photo."
                    )
                else:
                    st.session_state.history.append(result)

if typed_text is not None and typed_text.strip():
    if st.button("Understand this sloka", type="primary", key="understand_text"):
        with st.spinner("Translating and explaining the sloka..."):
            try:
                result = run_pipeline_from_text(typed_text.strip())
            except Exception:
                logger.exception("Text pipeline failed")
                st.error(
                    "Something went wrong while processing this text. "
                    "Please try again."
                )
            else:
                st.session_state.history.append(result)



if st.session_state.history:
    st.divider()
    st.subheader("Result")
    latest = st.session_state.history[-1]

    st.markdown(f"**Detected language:** {latest['detected_language'].title()}")

    st.markdown("**Original text**")
    st.text(latest["extracted_text"])

    st.markdown("**English translation**")
    st.write(latest["translation"])

    st.markdown("**Simple explanation**")
    st.write(latest["explanation"])

    if latest["sources"]:
        st.markdown("**Sources**")
        for url in latest["sources"]:
            st.markdown(f"- [{url}]({url})")

    with st.expander("Debug: step timings"):
        st.json(latest["timings"])

if len(st.session_state.history) > 1:
    with st.expander(f"Previous lookups this session ({len(st.session_state.history) - 1})"):
        for i, past in enumerate(reversed(st.session_state.history[:-1]), start=1):
            st.markdown(f"**{i}.** {past['translation'][:200]}...")
