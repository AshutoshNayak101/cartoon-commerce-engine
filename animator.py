"""
Animator Module
Creates animated scenes with cinematic zoom effects and transitions.
Uses MoviePy 1.0.3 syntax (NOT v2).
"""

import logging
from pathlib import Path
from typing import List
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips
from config import VIDEO_CONFIG, ANIMATION_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Animator:
    """
    Creates animated video clips with cinematic effects.
    """

    def __init__(self):
        self.width = VIDEO_CONFIG["width"]
        self.height = VIDEO_CONFIG["height"]
        self.fps = VIDEO_CONFIG["fps"]
        self.scene_duration = ANIMATION_CONFIG["scene_duration"]
        self.zoom_factor = ANIMATION_CONFIG["zoom_factor"]
        self.transition_duration = ANIMATION_CONFIG["transition_duration"]

    def create_zoom_effect(self, image_path: str) -> any:
        """
        Create a cinematic zoom effect on an image.
        Uses MoviePy 1.0.3 syntax.

        Args:
            image_path (str): Path to image file

        Returns:
            VideoClip: Animated clip with zoom effect
        """
        try:
            # Load image as clip
            clip = ImageClip(image_path).set_duration(self.scene_duration)
            clip = clip.resize((self.width, self.height))

            # Apply zoom effect using custom transformation
            def resize_func(get_frame, t):
                """
                Apply zoom resize to frame.
                """
                progress = t / self.scene_duration
                zoom = 1 + (self.zoom_factor - 1) * progress

                frame = get_frame(t)
                from PIL import Image

                # Convert frame to PIL, scale, and back
                pil_img = Image.fromarray(frame.astype("uint8"))
                new_size = (
                    int(self.width * zoom),
                    int(self.height * zoom),
                )
                pil_img = pil_img.resize(new_size, Image.Resampling.LANCZOS)

                # Crop to center
                left = (pil_img.width - self.width) // 2
                top = (pil_img.height - self.height) // 2
                pil_img = pil_img.crop((left, top, left + self.width, top + self.height))

                return np.array(pil_img)

            clip = clip.fl(resize_func)

            logger.info(f"Zoom effect created for: {image_path}")
            return clip

        except Exception as e:
            logger.error(f"Error creating zoom effect: {str(e)}")
            raise

    def create_scene_clips(self, image_paths: List[str]) -> List[any]:
        """
        Create animated clips for all images.

        Args:
            image_paths (List[str]): List of image file paths

        Returns:
            List[VideoClip]: List of animated clips
        """
        try:
            clips = []

            for idx, image_path in enumerate(image_paths):
                clip = self.create_zoom_effect(image_path)
                clips.append(clip)
                logger.info(f"Scene clip {idx} created")

            return clips

        except Exception as e:
            logger.error(f"Error creating scene clips: {str(e)}")
            raise

    def compose_clips(self, clips: List[any]) -> any:
        """
        Concatenate all clips into a single video.

        Args:
            clips (List[VideoClip]): List of video clips

        Returns:
            VideoClip: Concatenated video
        """
        try:
            if not clips:
                raise ValueError("No clips provided")

            # Concatenate clips
            final_clip = concatenate_videoclips(clips)

            logger.info(f"Composed {len(clips)} clips into final video")
            return final_clip

        except Exception as e:
            logger.error(f"Error composing clips: {str(e)}")
            raise


def get_animator() -> Animator:
    """
    Factory function to get Animator instance.
    """
    return Animator()
