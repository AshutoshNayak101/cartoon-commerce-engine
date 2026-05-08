"""
Main Streamlit Application
AI Cartoon Commerce Studio Lite - Instagram Reel Generator
Cloud-Optimized for Streamlit Community Cloud

Run with: python -m streamlit run app.py
"""

import streamlit as st
from pathlib import Path
import logging
import sys
import shutil
import os

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


@st.cache_resource
def validate_environment():
    """
    Validate cloud environment and dependencies.
    Cached to run only once per app session.
    """
    issues = []
    
    # Check FFmpeg availability
    if not shutil.which("ffmpeg"):
        issues.append("❌ FFmpeg not found - video export will fail. Please contact support.")
    else:
        logger.info("✓ FFmpeg available")
    
    # Check required directories can be created
    try:
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("✓ Upload directory accessible")
    except Exception as e:
        issues.append(f"❌ Cannot create upload directory: {e}")
    
    return issues


def initialize_session_state():
    """
    Initialize session state variables.
    """
    if "pipeline" not in st.session_state:
        try:
            st.session_state.pipeline = get_pipeline()
            logger.info("Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            st.error(f"❌ Failed to initialize pipeline: {e}")
            return False
    if "output_video_path" not in st.session_state:
        st.session_state.output_video_path = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    return True


def validate_inputs(product_name: str, uploaded_files: list) -> tuple:
    """
    Validate user inputs before generation.

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate product name
    if not product_name or len(product_name.strip()) == 0:
        return False, "❌ Please enter a product name"
    
    if len(product_name.strip()) > 100:
        return False, "❌ Product name too long (max 100 characters)"
    
    # Validate uploaded files
    if not uploaded_files or len(uploaded_files) == 0:
        return False, "❌ Please upload at least one product image"

    if len(uploaded_files) > 5:
        return False, "❌ Maximum 5 images allowed"

    # Check file types and sizes
    total_size = 0
    for file in uploaded_files:
        ext = file.name.split(".")[-1].lower()
        if ext not in ["jpg", "jpeg", "png"]:
            return False, f"❌ Invalid file type: {ext}. Only JPG, JPEG, PNG allowed"
        
        file_size_mb = len(file.getvalue()) / (1024 * 1024)
        if file_size_mb > 50:
            return False, f"❌ File {file.name} is too large ({file_size_mb:.1f}MB > 50MB limit)"
        
        total_size += file_size_mb
    
    if total_size > 100:
        return False, "❌ Total upload size exceeds 100MB limit"

    return True, "✅ Inputs validated"


def save_uploaded_files(uploaded_files: list) -> list:
    """
    Save uploaded files to temporary directory.
    Uses UUID to prevent path traversal attacks.

    Returns:
        List of saved file paths
    """
    try:
        saved_paths = []
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

        for idx, uploaded_file in enumerate(uploaded_files):
            # Sanitize filename: extract extension only
            ext = uploaded_file.name.split(".")[-1].lower()
            if ext not in ["jpg", "jpeg", "png"]:
                raise ValueError(f"Invalid file extension: {ext}")
            
            # Use safe filename based on index
            file_path = UPLOADS_DIR / f"product_{idx}.{ext}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_paths.append(str(file_path))
            logger.info(f"File saved: {file_path}")

        return saved_paths

    except Exception as e:
        logger.error(f"Error saving uploaded files: {str(e)}")
        raise


def cleanup_temp_files():
    """
    Clean up temporary files from previous generations.
    """
    try:
        # Clean old uploads
        if UPLOADS_DIR.exists():
            for file in UPLOADS_DIR.glob("product_*"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete {file}: {e}")
        logger.info("Cleanup completed")
    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")


def display_header():
    """
    Display application header.
    """
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
    """
    Display product input section.
    """
    st.subheader("📦 Product Information")

    col1, col2 = st.columns([1, 1])

    with col1:
        product_name = st.text_input(
            "Product Name",
            placeholder="e.g., Smart Water Bottle, Wireless Earbuds",
            help="Enter the name of the product to showcase",
            max_chars=100,
        )

    with col2:
        uploaded_files = st.file_uploader(
            "Upload Product Images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help="Upload 2-5 product images for the reel (max 50MB each)",
        )

    return product_name, uploaded_files


def display_generation_controls():
    """
    Display generation control buttons.
    """
    st.subheader("⚙️ Generation Controls")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        # Disable button while processing
        generate_button = st.button(
            "🚀 Generate Reel",
            use_container_width=True,
            help="Click to start the reel generation process",
            disabled=st.session_state.processing,
        )

    return generate_button


def display_output_section(video_path: str = None):
    """
    Display output section with video preview.
    """
    st.subheader("📹 Generated Reel")

    if video_path and Path(video_path).exists():
        # Display video
        st.success("✅ Reel generated successfully!")

        with st.expander("📺 Watch Preview", expanded=True):
            try:
                st.video(video_path)
            except Exception as e:
                logger.error(f"Error displaying video: {e}")
                st.error(f"Error displaying video preview: {e}")

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
            logger.error(f"Error creating download button: {e}")
            st.error(f"Error creating download: {e}")

        # Video info
        try:
            video_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            st.info(f"📊 Video Size: {video_size_mb:.2f} MB | Format: MP4 (1080x1920) | Codec: H.264")
        except Exception as e:
            logger.warning(f"Could not get video info: {e}")
    else:
        st.info("🎬 Generated reels will appear here. Start by uploading product images!")


def main():
    """
    Main application logic.
    """
    # Check environment first
    env_issues = validate_environment()
    if env_issues:
        st.error("⚠️ Environment Issues Found:")
        for issue in env_issues:
            st.error(issue)
        st.warning("Please contact support or try again later.")
        return

    # Initialize session state
    if not initialize_session_state():
        st.error("Failed to initialize application. Please refresh the page.")
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

            # Set processing flag
            st.session_state.processing = True

            # Save uploaded files
            with st.spinner("💾 Saving uploaded files..."):
                try:
                    saved_image_paths = save_uploaded_files(uploaded_files)
                    st.success(f"Saved {len(saved_image_paths)} images")
                except Exception as e:
                    st.error(f"Error saving files: {e}")
                    logger.error(f"File save error: {e}")
                    st.session_state.processing = False
                    return

            # Create progress placeholder
            progress_placeholder = st.empty()
            status_placeholder = st.empty()

            def progress_callback(message: str, progress: int):
                """
                Callback function for pipeline progress updates.
                """
                progress_placeholder.progress(progress / 100)
                status_placeholder.info(f"⏳ {message}")

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
                
                # Clean up uploaded files after successful generation
                cleanup_temp_files()
                
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error during generation: {str(e)}")
                logger.error(f"Pipeline error: {str(e)}", exc_info=True)
                status_placeholder.empty()
            
            finally:
                # Reset processing flag
                st.session_state.processing = False

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
            - **Images**: Pillow 10.0.1
            
            ### Limits (Free Tier)
            - Max 5 images per reel
            - Max 50MB per image
            - Max 100MB total upload
            - Processing time: ~5-10 minutes
            - Free tier resource limits apply
            """
        )

        st.divider()
        st.caption("🚀 AI Cartoon Commerce Studio Lite v1.0")
        st.caption("Made with ❤️ for creators")
        
        # Show deployment info
        st.divider()
        with st.expander("📋 Deployment Info"):
            st.caption("Environment: Streamlit Community Cloud")
            st.caption(f"Python: {sys.version.split()[0]}")
            st.caption(f"FFmpeg: {'✓ Available' if shutil.which('ffmpeg') else '✗ Not available'}")


if __name__ == "__main__":
    main()
