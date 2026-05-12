"""
Main Streamlit Application - PRODUCTION READY
Handles all common Streamlit Cloud errors
"""

import streamlit as st
import sys
import logging
from pathlib import Path

# ============= LOGGING SETUP =============
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= PAGE CONFIG FIRST =============
st.set_page_config(
    page_title="AI Cartoon Commerce Studio Lite",
    page_icon="🎬",
    layout="wide",
)

# ============= ADD PATH =============
sys.path.insert(0, str(Path(__file__).parent))

# ============= SAFE IMPORTS WITH ERROR HANDLING =============
try:
    from config import UPLOADS_DIR
    logger.info("Config imported OK")
except ImportError as e:
    st.error(f"❌ Config Error: {str(e)}")
    st.stop()
except Exception as e:
    st.error(f"❌ Unexpected config error: {str(e)}")
    st.stop()

try:
    from pipeline import get_pipeline
    logger.info("Pipeline imported OK")
except ImportError as e:
    st.error(f"❌ Pipeline Import Error: {str(e)}")
    st.stop()
except Exception as e:
    st.error(f"❌ Pipeline Error: {str(e)}")
    st.stop()

import shutil

# ============= CUSTOM CSS =============
st.markdown("""
<style>
body { background-color: #0e1117; color: #c9d1d9; }
.stButton > button { width: 100%; background-color: #238636; color: white; font-weight: bold; }
.title { font-size: 2.5em; font-weight: bold; color: #58a6ff; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ============= CACHE SAFE INITIALIZATION =============
@st.cache_resource(show_spinner=False)
def init_pipeline():
    """Initialize pipeline safely."""
    try:
        pipeline = get_pipeline()
        return pipeline, None
    except Exception as e:
        return None, str(e)

# ============= MAIN APP =============
def main():
    # Title
    st.markdown('<div class="title">🎬 AI Cartoon Commerce Studio Lite</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b949e;'>Generate Instagram Reels Instantly</p>", unsafe_allow_html=True)
    st.divider()
    
    # Initialize pipeline
    pipeline, pipeline_error = init_pipeline()
    
    if pipeline_error:
        st.error(f"⚠️ Pipeline initialization failed")
        st.info(f"Error details: {pipeline_error}")
        st.info("Try refreshing the page")
        return
    
    # Initialize session state
    if "output_video" not in st.session_state:
        st.session_state.output_video = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    # ===== INPUT SECTION =====
    st.subheader("📦 Product Information")
    col1, col2 = st.columns(2)
    
    with col1:
        product_name = st.text_input("Product Name", placeholder="e.g., Smart Water Bottle", max_chars=100)
    
    with col2:
        uploaded_files = st.file_uploader("Upload Images (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    st.divider()
    
    # ===== GENERATION BUTTON =====
    st.subheader("⚙️ Generate")
    col1, col2, col3 = st.columns(3)
    
    with col2:
        generate_btn = st.button("🚀 Generate Reel", use_container_width=True, disabled=st.session_state.processing)
    
    st.divider()
    
    # ===== GENERATION LOGIC =====
    if generate_btn:
        # Validate
        if not product_name or not product_name.strip():
            st.error("❌ Please enter product name")
            return
        
        if not uploaded_files:
            st.error("❌ Please upload at least 1 image")
            return
        
        if len(uploaded_files) > 5:
            st.error("❌ Max 5 images allowed")
            return
        
        st.success("✅ Validation passed")
        st.session_state.processing = True
        
        # Save files
        try:
            with st.spinner("💾 Saving files..."):
                saved_paths = []
                UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
                
                for idx, file in enumerate(uploaded_files):
                    ext = file.name.split(".")[-1].lower()
                    if ext not in ["jpg", "jpeg", "png"]:
                        st.error(f"❌ Invalid format: {ext}")
                        st.session_state.processing = False
                        return
                    
                    path = UPLOADS_DIR / f"product_{idx}.{ext}"
                    with open(path, "wb") as f:
                        f.write(file.getbuffer())
                    saved_paths.append(str(path))
                
                st.success(f"✅ Saved {len(saved_paths)} images")
        
        except Exception as e:
            st.error(f"❌ File save error: {str(e)}")
            st.session_state.processing = False
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status = st.empty()
        
        # Generate
        try:
            with st.spinner("🎬 Generating reel..."):
                def progress_cb(msg, prog):
                    try:
                        progress_bar.progress(min(prog / 100, 0.99))
                        status.info(f"⏳ {msg}")
                    except:
                        pass
                
                output = pipeline.execute(
                    product_name=product_name,
                    image_paths=saved_paths,
                    progress_callback=progress_cb,
                )
                
                st.session_state.output_video = output
                progress_bar.progress(1.0)
                status.success("✅ Done!")
                
                # Cleanup
                for p in saved_paths:
                    try:
                        Path(p).unlink()
                    except:
                        pass
        
        except Exception as e:
            st.error(f"❌ Generation failed: {str(e)}")
            logger.error(f"Error: {str(e)}", exc_info=True)
        
        finally:
            st.session_state.processing = False
    
    st.divider()
    
    # ===== OUTPUT =====
    st.subheader("📹 Result")
    
    if st.session_state.output_video and Path(st.session_state.output_video).exists():
        st.success("✅ Reel generated!")
        
        try:
            st.video(st.session_state.output_video)
            
            with open(st.session_state.output_video, "rb") as f:
                st.download_button(
                    label="📥 Download",
                    data=f.read(),
                    file_name="reel.mp4",
                    mime="video/mp4",
                )
        except Exception as e:
            st.error(f"❌ Video error: {str(e)}")
    else:
        st.info("🎬 Upload images and generate to see your reel here")
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.subheader("ℹ️ About")
        st.markdown("""
        **AI Cartoon Commerce Studio**
        
        Auto-generate product showcase videos
        
        - 🤖 AI dialogue
        - 🎙️ Voice narration  
        - 🎬 Animations
        - 📱 Mobile (9:16)
        
        v1.0
        """)

# ============= RUN =============
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ App Error: {str(e)}")
        logger.error(f"Critical: {str(e)}", exc_info=True)
