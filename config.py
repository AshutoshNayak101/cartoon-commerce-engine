"""
Configuration Module
Defines all constants and settings for the AI Cartoon Commerce Studio Lite
"""

import os
from pathlib import Path

# Project Structure
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "assets"
UPLOADS_DIR = ASSETS_DIR / "uploads"
SCENES_DIR = ASSETS_DIR / "scenes"
OUTPUT_DIR = ASSETS_DIR / "output"
VOICES_DIR = ASSETS_DIR / "voices"
MUSIC_DIR = ASSETS_DIR / "music"

# Create directories if they don't exist
for directory in [UPLOADS_DIR, SCENES_DIR, OUTPUT_DIR, VOICES_DIR, MUSIC_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Video Configuration
VIDEO_CONFIG = {
    "aspect_ratio": "9:16",
    "width": 1080,
    "height": 1920,
    "fps": 24,
    "codec": "libx264",
    "audio_codec": "aac",
}

# Animation Settings
ANIMATION_CONFIG = {
    "scene_duration": 2.5,
    "zoom_factor": 1.2,
    "transition_duration": 0.5,
    "subtitle_font_size": 60,
    "subtitle_color": (255, 255, 255),
}

# Dialogue Configuration
DIALOGUE_CONFIG = {
    "characters": ["Robot Cat", "Boy"],
    "tone": "funny, engaging, cartoon commercial",
    "max_lines": 6,
}

# Voice Configuration
VOICE_CONFIG = {
    "language": "en",
    "tld": "com",
    "slow": False,
}

# Audio Configuration
AUDIO_CONFIG = {
    "sample_rate": 44100,
    "channels": 2,
    "background_music_volume": 0.3,
    "voice_volume": 0.9,
}

# UI Configuration
UI_CONFIG = {
    "theme": "dark",
    "title": "AI Cartoon Commerce Studio Lite",
    "icon": "🎬",
}

# File Configuration
FILE_CONFIG = {
    "max_file_size_mb": 50,
    "supported_formats": ["jpg", "jpeg", "png"],
    "output_format": "mp4",
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}
