"""
Main Streamlit Application
AI Cartoon Commerce Studio Lite - Instagram Reel Generator
Linux / Streamlit Community Cloud Compatible

Run with: python -m streamlit run app.py
"""

import streamlit as st
from pathlib import Path
import logging
import sys

sys.path.insert(0, str(Path(__file__).parent))

from pipeline import get_pipeline
from config import UPLOADS_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(
    page_title="AI Cartoon Commerce Studio Lite",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .stButton > button {
        width: 100%;
        background-color: #238636;
        color: white;
        font-weight: bold;
        padding: 12px 24px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #2ea043;
    }
    .title-text {
        font-size: 2.5em;
        font-weight: bold;
        color: #58a6ff;
        text-align: center;
    }
    .subtitle-text {
        font-size: 1.1em;
        color: #8b949e;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helper: friendly error messages
# ---------------------------------------------------------------------------

def _friendly_error(exc: Exception) -> str:
    """
    Convert a raw exception into a user-friendly message without leaking
    internal details or stack traces to the Streamlit UI.
    """
    msg = str(exc)
    try:
        from gtts.tts import gTTSError
    except Exception:
        gTTSError = None

    if isinstance(exc, ConnectionError) or (gTTSError is not None and isinstance(exc, gTTSError)):
        return (
            "🌐 Voice narration requires an internet connection to Google Text-to-Speech. "
            "Please check your connection and try again."
        )
    if isinstance(exc, FileNotFoundError) or "Output file not created" in msg:
        return "📁 Video export failed — the output file could not be created. Check disk space and permissions."
    if "ffmpeg" in msg.lower() or "codec" in msg.lower():
        return "🎬 Video encoding failed. FFmpeg may not be available or the codec is unsupported."
    if "No images were successfully prepared" in msg:
        return "🖼️ None of the uploaded images could be processed. Please upload valid JPG or PNG files."
    if "Invalid audio duration" in msg:
        return "🎙️ Voice narration could not be generated. Please try again."
    # Generic fallback — show only the first sentence to avoid leaking internals
    first_sentence = msg.split(".")[0].strip()
    return f"❌ Generation failed: {first_sentence}."


# ---------------------------------------------------------------------------
# Startup: FFmpeg preflight check
# ---------------------------------------------------------------------------

def _check_ffmpeg() -> tuple:
    """
    Return (available: bool, path_or_error: str).
    Checks imageio_ffmpeg first (bundled), then system PATH.
    """
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        return True, path
    except Exception:
        pass
    import shutil
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return True, sys_ffmpeg
    return False, "ffmpeg not found via imageio-ffmpeg or system PATH"


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def initialize_session_state():
    """
    Initialize session state variables.
    """
    if "pipeline" not in st.session_state:
        try:
            st.session_state.pipeline = get_pipeline()
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}", exc_info=True)
            st.error(
                "⚙️ Failed to initialize the generation pipeline. "
                "Please refresh the page. If the problem persists, check the server logs."
            )
            return False
    if "output_video_path" not in st.session_state:
        st.session_state.output_video_path = None
    return True


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def validate_inputs(product_name: str, uploaded_files: list) -> tuple:
    """
    Validate user inputs before generation.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not product_name or len(product_name.strip()) == 0:
        return False, "❌ Please enter a product name"

    if not uploaded_files or len(uploaded_files) == 0:
        return False, "❌ Please upload at least one product image"

    if len(uploaded_files) > 5:
        return False, "❌ Maximum 5 images allowed"

    # Check file types
    for file in uploaded_files:
        ext = file.name.split(".")[-1].lower()
        if ext not in ["jpg", "jpeg", "png"]:
            return False, f"❌ Invalid file type: {ext}. Only JPG, JPEG, PNG allowed"

    return True, "✅ Inputs validated"


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def save_uploaded_files(uploaded_files: list) -> list:
    """
    Save uploaded files to temporary directory.

    Returns:
        List of saved file paths
    """
    try:
        saved_paths = []
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

        for idx, uploaded_file in enumerate(uploaded_files):
            ext = uploaded_file.name.split(".")[-1].lower()
            if ext not in {"jpg", "jpeg", "png"}:
                raise ValueError(f"Invalid file type: {ext}")
            file_path = UPLOADS_DIR / f"product_{idx}.{ext}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_paths.append(str(file_path))
            logger.info(f"File saved: {file_path}")

        return saved_paths

    except Exception as e:
        logger.error(f"Error saving uploaded files: {str(e)}", exc_info=True)
        raise


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def display_header():
    """Display application header."""
    st.markdown(
        '<p class="title-text">🎬 AI Cartoon Commerce Studio Lite</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">Generate Instagram-Ready Reels in Minutes</p>',
        unsafe_allow_html=True,
    )
    st.divider()


def display_input_section():
    """Display product input section."""
    st.subheader("📦 Product Information")

    col1, col2 = st.columns([1, 1])

    with col1:
        product_name = st.text_input(
            "Product Name",
            placeholder="e.g., Smart Water Bottle, Wireless Earbuds",
            help="Enter the name of the product to showcase",
        )

    with col2:
        uploaded_files = st.file_uploader(
            "Upload Product Images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help="Upload 2-5 product images for the reel",
        )

    return product_name, uploaded_files


def display_generation_controls():
    """Display generation control buttons."""
    st.subheader("⚙️ Generation Controls")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        generate_button = st.button(
            "🚀 Generate Reel",
            use_container_width=True,
            help="Click to start the reel generation process",
        )

    return generate_button


def display_output_section(video_path: str = None):
    """Display output section with video preview."""
    st.subheader("📹 Generated Reel")

    if video_path and Path(video_path).exists():
        st.success("✅ Reel generated successfully!")

        with st.expander("📺 Watch Preview", expanded=True):
            try:
                st.video(video_path)
            except Exception as e:
                logger.error(f"Error displaying video: {e}", exc_info=True)
                st.warning("Could not display video preview inline. Use the download button below.")

        # Download button
        try:
            with open(video_path, "rb") as video_file:
                st.download_button(
                    label="📥 Download Reel (MP4)",
                    data=video_file.read(),
                    file_name="cartoon_commerce_reel.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                )
        except Exception as e:
            logger.error(f"Error creating download button: {e}", exc_info=True)
            st.error("Could not create download link. Please try refreshing the page.")

        # Video info
        try:
            video_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            st.info(f"📊 Video Size: {video_size_mb:.2f} MB | Format: MP4 (1080x1920) | Codec: H.264")
        except Exception as e:
            logger.warning(f"Could not get video info: {e}")
    else:
        st.info("🎬 Generated reels will appear here. Start by uploading product images!")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Main application logic."""
    # Initialize session state
    if not initialize_session_state():
        st.stop()
        return

    # Display header
    display_header()

    # Input section
    product_name, uploaded_files = display_input_section()

    st.divider()

    # Generation controls
    generate_button = display_generation_controls()

    st.divider()

    # Generation logic
    if generate_button:
        # Validate inputs
        is_valid, validation_message = validate_inputs(product_name, uploaded_files)

        if not is_valid:
            st.error(validation_message)
        else:
            st.success(validation_message)

            # Save uploaded files
            with st.spinner("💾 Saving uploaded files..."):
                try:
                    saved_image_paths = save_uploaded_files(uploaded_files)
                    st.success(f"Saved {len(saved_image_paths)} images")
                except Exception as e:
                    logger.error(f"File save error: {e}", exc_info=True)
                    st.error("❌ Could not save the uploaded files. Check server disk space and permissions.")
                    return

            # Create progress placeholder
            progress_placeholder = st.empty()
            status_placeholder = st.empty()

            def progress_callback(message: str, progress: int):
                """Callback function for pipeline progress updates."""
                try:
                    progress_placeholder.progress(progress / 100)
                    status_placeholder.info(f"⏳ {message}")
                except Exception as callback_error:
                    logger.warning(f"Progress callback failed: {callback_error}")

            # Execute pipeline
            try:
                output_path = st.session_state.pipeline.execute(
                    product_name=product_name,
                    image_paths=saved_image_paths,
                    progress_callback=progress_callback,
                )

                st.session_state.output_video_path = output_path
                progress_placeholder.success("✅ Reel generation completed!")
                status_placeholder.empty()
                st.rerun()

            except Exception as e:
                logger.error(f"Pipeline error: {e}", exc_info=True)
                progress_placeholder.empty()
                status_placeholder.empty()
                st.error(_friendly_error(e))

    st.divider()

    # Output section
    display_output_section(st.session_state.output_video_path)

    # Sidebar information
    with st.sidebar:
        st.subheader("ℹ️ About")
        st.markdown(
            """
            **AI Cartoon Commerce Studio Lite** is an automated reel generation system.

            ### Features
            - 🤖 AI dialogue generation
            - 🎙️ Voice narration with gTTS
            - 🎬 Cinematic animations
            - 📱 Mobile-optimized (9:16)
            - 🎵 Background music
            - 📝 Auto-subtitles

            ### How it works
            1. Enter product name
            2. Upload 2-5 images
            3. Click "Generate Reel"
            4. Download your video!

            ### Tech Stack
            - **Frontend**: Streamlit
            - **Backend**: Python
            - **Video**: MoviePy 1.0.3
            - **Voice**: gTTS
            - **Images**: Pillow
            """
        )

        st.divider()

        # FFmpeg preflight status
        ffmpeg_ok, ffmpeg_info = _check_ffmpeg()
        if ffmpeg_ok:
            st.success("✅ FFmpeg available")
        else:
            st.error(f"❌ FFmpeg not found — video export will fail. ({ffmpeg_info})")

        st.divider()
        st.caption("🚀 AI Cartoon Commerce Studio Lite v1.0")
        st.caption("Made with ❤️ for creators")


if __name__ == "__main__":
    main()
