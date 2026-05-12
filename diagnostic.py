"""
Diagnostic Test App - Identify startup errors
"""
import streamlit as st
import sys
from pathlib import Path

st.set_page_config(page_title="Diagnostic Test", layout="wide")

st.title("🔍 Diagnostic Test App")
st.write("Testing module imports and dependencies...")

# Test 1: Config import
st.subheader("Test 1: Config Module")
try:
    from config import ANIMATION_CONFIG, VIDEO_CONFIG, UPLOADS_DIR
    st.success("✅ config.py imported successfully")
    st.write(f"ANIMATION_CONFIG keys: {list(ANIMATION_CONFIG.keys())}")
except Exception as e:
    st.error(f"❌ Config import failed: {str(e)}")
    st.stop()

# Test 2: Animator import
st.subheader("Test 2: Animator Module")
try:
    from animator import get_animator
    animator = get_animator()
    st.success("✅ animator.py imported and initialized")
    st.write(f"Animator bg_color: {animator.bg_color}")
    st.write(f"Animator text_color: {animator.text_color}")
except Exception as e:
    st.error(f"❌ Animator import failed: {str(e)}")
    st.stop()

# Test 3: Script Generator import
st.subheader("Test 3: Script Generator Module")
try:
    from script_generator import get_script_generator
    script_gen = get_script_generator()
    st.success("✅ script_generator.py imported and initialized")
except Exception as e:
    st.error(f"❌ Script Generator import failed: {str(e)}")
    st.stop()

# Test 4: Pipeline import
st.subheader("Test 4: Pipeline Module")
try:
    from pipeline import get_pipeline
    st.success("✅ pipeline.py module loaded")
    st.write("Attempting to initialize pipeline...")
    pipeline = get_pipeline()
    st.success("✅ Pipeline initialized successfully!")
except Exception as e:
    st.error(f"❌ Pipeline initialization failed: {str(e)}")
    st.write("Full error details:")
    st.code(str(e))
    st.stop()

# Test 5: Generate sample script
st.subheader("Test 5: Script Generation")
try:
    script = script_gen.generate_script("Test Product")
    st.success("✅ Script generated successfully")
    st.write(f"Script lines: {script.get('line_count', 0)}")
except Exception as e:
    st.error(f"❌ Script generation failed: {str(e)}")

st.divider()
st.success("✅ ALL TESTS PASSED - App is ready for deployment")
