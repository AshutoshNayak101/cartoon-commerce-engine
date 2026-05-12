"""
Main Streamlit Application - SIMPLIFIED FOR STREAMLIT CLOUD
AI Cartoon Commerce Studio Lite - Instagram Reel Generator
Production-Ready for Streamlit Community Cloud

Run with: streamlit run app.py
"""

import streamlit as st
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config FIRST before any other streamlit calls
st.set_page_config(
    page_title="AI Cartoon Commerce Studio Lite",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import with error handling
try:
    from config import UPLOADS_DIR, VIDEO_CONFIG, ANIMATION_CONFIG
    logger.info("✓ Config imported successfully")
except Exception as e:
    st.error(f"❌ Failed to import config: {str(e)}")
    st.stop()

try:
    from pipeline import get_pipeline
    logger.info("✓ Pipeline imported successfully")
except Exception as e:
    st.error(f"❌ Failed to import pipeline: {str(e)}")
    st.stop()

import shutil

# ============= CUSTOM CSS =============
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
    }
    .title-text {
        font-size: 2.5em;
        font-weight: bold;
        color: #58a6ff;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============= VALIDATION =============
@st.cache_resource
def validate_environment():
    """Validate environment on first load."""
    issues = []
    
    # Check FFmpeg
    if not shutil.which("ffmpeg"):
        issues.append("⚠️ FFmpeg not detected (may affect video export)")
    else:
        logger.info("✓ FFmpeg available")
    
    # Check directories
    try:
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("✓ Upload directory OK")
    except Exception as e:
        issues.append(f"❌ Cannot create upload directory: {e}")
    
    return issues

# ============= SESSION STATE INITIALIZATION =============
def init_session():
    """Initialize Streamlit session state."""
    if "pipeline" not in st.session_state:
        try:
            st.session_state.pipeline = get_pipeline()
            st.session_state.pipeline_ready = True
            logger.info("✓ Pipeline initialized")
        except Exception as e:
            logger.error(f"Pipeline init error: {str(e)}")
            st.session_state.pipeline_ready = False
            st.error(f"❌ Pipeline Error: {str(e)}")
            return False
    
    if "output_video_path" not in st.session_state:
        st.session_state.output_video_path = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    return True

# ============= MAIN UI =============
def main():
    """Main application."""
    
    # Validate environment
    env_issues = validate_environment()
    if env_issues:
        st.warning("⚠️ Environment Notes:")
        for issue in env_issues:
            st.warning(issue)
    
    # Initialize session
    if not init_session():
        st.error("Failed to initialize application. Please refresh.")
        return
    
    if not st.session_state.pipeline_ready:
        st.error("Pipeline not ready. Please refresh the page.")
        return
    
    # ===== HEADER =====
    st.markdown('<p class="title-text">🎬 AI Cartoon Commerce Studio Lite</p>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Generate Instagram-Ready Reels</p>", unsafe_allow_html=True)
    st.divider()
    
    # ===== INPUT SECTION =====
    st.subheader("📦 Product Information")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        product_name = st.text_input(
            "Product Name",
            placeholder="e.g., Smart Water Bottle",
            max_chars=100,
        )
    
    with col2:
        uploaded_files = st.file_uploader(
            "Upload Images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
        )
    
    st.divider()
    
    # ===== GENERATE BUTTON =====
    st.subheader("⚙️ Generation")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        generate_btn = st.button(
            "🚀 Generate Reel",
            use_container_width=True,
            disabled=st.session_state.processing,
        )
    
    st.divider()
    
    # ===== GENERATION LOGIC =====
    if generate_btn:
        # Validate inputs
        if not product_name or not product_name.strip():
            st.error("❌ Please enter a product name")
            return
        
        if not uploaded_files:
            st.error("❌ Please upload at least one image")
            return
        
        if len(uploaded_files) > 5:
            st.error("❌ Maximum 5 images allowed")
            return
        
        st.success("✅ Inputs validated")
        st.session_state.processing = True
        
        # Save files
        try:
            with st.spinner("💾 Saving files..."):
                saved_paths = []
                UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
                
                for idx, file in enumerate(uploaded_files):
                    ext = file.name.split(".")[-1].lower()
                    if ext not in ["jpg", "jpeg", "png"]:
                        st.error(f"❌ Invalid file type: {ext}")
                        return
                    
                    file_path = UPLOADS_DIR / f"product_{idx}.{ext}"
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    saved_paths.append(str(file_path))
                
                st.success(f"✅ Saved {len(saved_paths)} images")
        except Exception as e:
            st.error(f"❌ Error saving files: {str(e)}")
            st.session_state.processing = False
            return
        
        # Create progress placeholders
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Execute pipeline
        try:
            with st.spinner("🎬 Generating reel..."):
                def progress_callback(message: str, progress: int):
                    try:
                        progress_bar.progress(min(progress / 100, 0.99))
                        status_text.info(f"⏳ {message}")
                    except:
                        pass
                
                output_path = st.session_state.pipeline.execute(
                    product_name=product_name,
                    image_paths=saved_paths,
                    progress_callback=progress_callback,
                )
                
                st.session_state.output_video_path = output_path
                progress_bar.progress(1.0)
                status_text.success("✅ Generation complete!")
                
                # Clean up
                for p in saved_paths:
                    try:
                        Path(p).unlink()
                    except:
                        pass
        
        except Exception as e:
            st.error(f"❌ Generation failed: {str(e)}")
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        
        finally:
            st.session_state.processing = False
    
    st.divider()
    
    # ===== OUTPUT SECTION =====
    st.subheader("📹 Generated Reel")
    
    if st.session_state.output_video_path and Path(st.session_state.output_video_path).exists():
        st.success("✅ Reel ready!")
        
        try:
            st.video(st.session_state.output_video_path)
            
            with open(st.session_state.output_video_path, "rb") as f:
                st.download_button(
                    label="📥 Download Reel (MP4)",
                    data=f.read(),
                    file_name="cartoon_reel.mp4",
                    mime="video/mp4",
                )
        except Exception as e:
            st.error(f"❌ Error displaying video: {str(e)}")
    else:
        st.info("🎬 Upload images and generate a reel to see it here")
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.subheader("ℹ️ About")
        st.markdown("""
        **AI Cartoon Commerce Studio Lite**
        
        Generate product showcase videos automatically.
        
        **Features:**
        - 🤖 AI dialogue
        - 🎙️ Voice narration  
        - 🎬 Animations
        - 📱 Mobile format (9:16)
        
        **Tech:**
        - Streamlit + MoviePy
        - gTTS voice
        - Pillow images
        """)
        
        st.divider()
        st.caption("v1.0 | Made with ❤️")

# ============= RUN APP =============
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"App error: {str(e)}", exc_info=True)
        st.error(f"❌ App Error: {str(e)}")
