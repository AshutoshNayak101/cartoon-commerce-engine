"""
Subtitle Generator Module
Creates and synchronizes subtitles with video and audio.
MoviePy 1.0.3 Compatible
"""

import logging
from typing import Any, Dict, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from moviepy.editor import TextClip, CompositeVideoClip
from config import VIDEO_CONFIG, ANIMATION_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """
    Generates and synchronizes subtitles for video.
    MoviePy 1.0.3 compatible implementation.
    """

    def __init__(self):
        self.width = VIDEO_CONFIG["width"]
        self.height = VIDEO_CONFIG["height"]
        self.font_size = ANIMATION_CONFIG["subtitle_font_size"]
        self.subtitle_color = ANIMATION_CONFIG["subtitle_color"]
        self.min_subtitle_duration = 0.5  # Minimum duration to ensure visibility

    def _create_text_clip_safe(self, text: str, duration: float, start_time: float) -> Any:
        """
        Safely create a TextClip with MoviePy 1.0.3.
        Handles font availability gracefully.
        
        FIX: Ensures duration is always safe (minimum 0.5s for visibility)
        """
        try:
            # FIX: Ensure minimum duration for visibility
            if duration <= 0:
                logger.warning(f"Invalid subtitle duration: {duration}. Using minimum: {self.min_subtitle_duration}s")
                duration = self.min_subtitle_duration
            
            # Try with specific font
            txt_clip = TextClip(
                text,
                fontsize=self.font_size,
                color='white',
                font='Arial',
                method='caption',
                size=(self.width - 100, None),
                interline=5,
            )
        except Exception as e:
            logger.warning(f"Failed with Arial font: {e}. Trying default font.")
            try:
                # Fallback to default font
                txt_clip = TextClip(
                    text,
                    fontsize=self.font_size,
                    color='white',
                    method='caption',
                    size=(self.width - 100, None),
                    interline=5,
                )
            except Exception as e2:
                logger.warning(f"Failed with default font: {e2}. Using minimal text clip.")
                # Last resort - simple text
                txt_clip = TextClip(
                    text[:50],  # Truncate if too long
                    fontsize=40,
                    color='white',
                )

        # Set duration and timing - MoviePy 1.0.3 compatible
        txt_clip = txt_clip.set_duration(duration)
        txt_clip = txt_clip.set_start(start_time)
        txt_clip = txt_clip.set_position('center')

        return txt_clip

    def create_subtitle_clips(
        self, script_lines: List[Dict], audio_duration: float
    ) -> List[Any]:
        """
        Create subtitle clips synchronized with narration.

        Args:
            script_lines (List[Dict]): Script with character dialogues
            audio_duration (float): Duration of audio in seconds

        Returns:
            List[TextClip]: List of subtitle clips
        """
        try:
            if not script_lines:
                logger.warning("No script lines provided for subtitles")
                return []

            # FIX: Prevent divide-by-zero when audio_duration is invalid
            if audio_duration <= 0:
                logger.warning(f"Invalid audio duration: {audio_duration}. Cannot create subtitles.")
                return []

            subtitle_clips = []
            time_per_line = audio_duration / len(script_lines)

            for idx, line in enumerate(script_lines):
                try:
                    # Extract dialogue
                    dialogue = line.get("dialogue", "")
                    
                    # Remove emojis and character names
                    clean_text = dialogue.replace("🤖 Robot Cat: ", "").replace("👦 Boy: ", "")
                    clean_text = clean_text.strip()
                    
                    # FIX: Handle empty subtitle with fallback text
                    if not clean_text or len(clean_text) == 0:
                        logger.warning(f"Empty dialogue at line {idx}. Using placeholder.")
                        clean_text = f"[Scene {idx + 1}]"
                    
                    # Calculate timing
                    start_time = idx * time_per_line
                    duration = time_per_line

                    # Create text clip safely (handles minimum duration)
                    txt_clip = self._create_text_clip_safe(clean_text, duration, start_time)

                    subtitle_clips.append(txt_clip)
                    logger.info(f"Subtitle {idx} created: {clean_text[:40]}...")

                except Exception as e:
                    logger.warning(f"Failed to create subtitle {idx}: {e}. Continuing.")
                    continue

            if not subtitle_clips:
                logger.warning("No subtitle clips were created")

            return subtitle_clips

        except Exception as e:
            logger.error(f"Error creating subtitle clips: {str(e)}")
            raise

    def overlay_subtitles(self, video_clip: Any, subtitle_clips: List[Any]) -> Any:
        """
        Overlay subtitles on video.

        Args:
            video_clip (VideoClip): Main video clip
            subtitle_clips (List[TextClip]): Subtitle clips

        Returns:
            VideoClip: Video with overlaid subtitles
        """
        try:
            if not subtitle_clips:
                logger.warning("No subtitle clips to overlay. Returning video as-is.")
                return video_clip

            # Composite video with subtitles - MoviePy 1.0.3 compatible
            final_clip = CompositeVideoClip([video_clip] + subtitle_clips)

            logger.info(f"Overlaid {len(subtitle_clips)} subtitle clips on video")
            return final_clip

        except Exception as e:
            logger.error(f"Error overlaying subtitles: {str(e)}")
            # Return video without subtitles on error
            logger.warning("Returning video without subtitles due to overlay error")
            return video_clip


def get_subtitle_generator() -> SubtitleGenerator:
    """
    Factory function to get SubtitleGenerator instance.
    """
    return SubtitleGenerator()
