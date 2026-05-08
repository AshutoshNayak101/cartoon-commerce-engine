"""
Animator Module
Converts script into animated video frames using PIL, NumPy, and MoviePy.
MoviePy 1.0.3 Compatible
"""

import logging
from pathlib import Path
from typing import List, Any
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from moviepy.editor import ImageSequenceClip
from config import VIDEO_CONFIG, ANIMATION_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Animator:
    """
    Creates animations from script using PIL and NumPy.
    MoviePy 1.0.3 compatible.
    """

    def __init__(self):
        self.width = VIDEO_CONFIG["width"]
        self.height = VIDEO_CONFIG["height"]
        self.fps = VIDEO_CONFIG["fps"]
        self.bg_color = ANIMATION_CONFIG["background_color"]
        self.text_color = ANIMATION_CONFIG["text_color"]

    def _get_pil_resample_filter(self) -> Any:
        """
        Get appropriate PIL resampling filter based on version.
        Handles both old (Image.LANCZOS) and new (Image.Resampling.LANCZOS) APIs.
        """
        try:
            # Try modern API first (Pillow 10+)
            return Image.Resampling.LANCZOS
        except AttributeError:
            # Fallback to older API
            return Image.LANCZOS

    def _normalize_frame_to_uint8(self, frame: np.ndarray) -> np.ndarray:
        """
        Normalize frame array to uint8 format for PIL.
        
        Args:
            frame (np.ndarray): Frame array (may be float or int)
            
        Returns:
            np.ndarray: Normalized uint8 array
        """
        if frame.dtype == np.uint8:
            return frame
        elif frame.dtype in [np.float32, np.float64]:
            # Assume float is 0-1 range
            return (np.clip(frame, 0, 1) * 255).astype(np.uint8)
        else:
            # Other integer types
            return np.clip(frame, 0, 255).astype(np.uint8)

    def create_animation(self, script: List[Any], audio_file: str) -> Any:
        """
        Create animated video clip from script.

        Args:
            script (List[Any]): Script lines with dialogue
            audio_file (str): Path to audio file (for duration)

        Returns:
            VideoClip: Animated video clip
        """
        try:
            if not script:
                raise ValueError("Script cannot be empty")

            logger.info(f"Creating animation for {len(script)} script lines...")

            # Generate frames
            frames = self._generate_frames(script)

            if not frames:
                raise ValueError("No frames were generated")

            logger.info(f"Generated {len(frames)} frames")

            # Create video clip from frames
            video_clip = ImageSequenceClip(frames, fps=self.fps)

            logger.info(f"Animation clip created: {video_clip.duration:.2f}s")
            return video_clip

        except Exception as e:
            logger.error(f"Error creating animation: {str(e)}")
            raise

    def _generate_frames(self, script: List[Any]) -> List[np.ndarray]:
        """
        Generate individual animation frames.

        Args:
            script (List[Any]): Script lines

        Returns:
            List[np.ndarray]: List of frame arrays
        """
        frames = []
        frames_per_line = max(self.fps * 2, 10)  # At least 2 seconds per line

        for line_idx, line in enumerate(script):
            try:
                dialogue = line.get("dialogue", "")
                
                # Create simple frame with text
                for frame_num in range(int(frames_per_line)):
                    img = Image.new("RGB", (self.width, self.height), self.bg_color)
                    draw = ImageDraw.Draw(img)

                    # Draw text
                    clean_text = dialogue.replace("🤖 Robot Cat: ", "").replace(
                        "👦 Boy: ", ""
                    )
                    draw.text(
                        (50, self.height // 2),
                        clean_text[:50],
                        fill=self.text_color,
                    )

                    # Convert to numpy array
                    frame_array = np.array(img)
                    frames.append(frame_array)

                logger.info(f"Generated {len(frames)} total frames so far...")

            except Exception as e:
                logger.warning(f"Error generating frame for line {line_idx}: {e}")
                continue

        return frames


def get_animator() -> Animator:
    """
    Factory function to get Animator instance.
    """
    return Animator()
