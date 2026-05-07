"""
Subtitle Generator Module
Creates and synchronizes subtitles with video and audio.
"""

import logging
from typing import List, Dict
from pathlib import Path
from moviepy.editor import TextClip, CompositeVideoClip
from config import VIDEO_CONFIG, ANIMATION_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """
    Generates and synchronizes subtitles for video.
    """

    def __init__(self):
        self.width = VIDEO_CONFIG["width"]
        self.height = VIDEO_CONFIG["height"]
        self.font_size = ANIMATION_CONFIG["subtitle_font_size"]
        self.subtitle_color = ANIMATION_CONFIG["subtitle_color"]

    def create_subtitle_clips(
        self, script_lines: List[Dict], audio_duration: float
    ) -> List[any]:
        """
        Create subtitle clips synchronized with narration.

        Args:
            script_lines (List[Dict]): Script with character dialogues
            audio_duration (float): Duration of audio in seconds

        Returns:
            List[TextClip]: List of subtitle clips
        """
        try:
            subtitle_clips = []
            time_per_line = audio_duration / len(script_lines)

            for idx, line in enumerate(script_lines):
                # Create subtitle text
                dialogue = line["dialogue"]
                # Remove emojis and character names
                clean_text = dialogue.replace("🤖 Robot Cat: ", "").replace("👦 Boy: ", "")

                # Calculate timing
                start_time = idx * time_per_line
                end_time = (idx + 1) * time_per_line

                # Create text clip
                try:
                    txt_clip = TextClip(
                        clean_text,
                        fontsize=self.font_size,
                        color="white",
                        font="Arial-Bold",
                        method="caption",
                        size=(self.width - 100, None),
                    )
                except:
                    # Fallback if custom font not available
                    txt_clip = TextClip(
                        clean_text,
                        fontsize=self.font_size,
                        color="white",
                        method="caption",
                        size=(self.width - 100, None),
                    )

                txt_clip = txt_clip.set_position("center").set_duration(end_time - start_time)
                txt_clip = txt_clip.set_start(start_time)

                subtitle_clips.append(txt_clip)
                logger.info(f"Subtitle {idx} created: {clean_text[:50]}...")

            return subtitle_clips

        except Exception as e:
            logger.error(f"Error creating subtitle clips: {str(e)}")
            raise

    def overlay_subtitles(self, video_clip: any, subtitle_clips: List[any]) -> any:
        """
        Overlay subtitles on video.

        Args:
            video_clip (VideoClip): Main video clip
            subtitle_clips (List[TextClip]): Subtitle clips

        Returns:
            VideoClip: Video with overlaid subtitles
        """
        try:
            # Composite video with subtitles
            final_clip = CompositeVideoClip([video_clip] + subtitle_clips)

            logger.info(f"Subtitles overlaid on video")
            return final_clip

        except Exception as e:
            logger.error(f"Error overlaying subtitles: {str(e)}")
            raise


def get_subtitle_generator() -> SubtitleGenerator:
    """
    Factory function to get SubtitleGenerator instance.
    """
    return SubtitleGenerator()
