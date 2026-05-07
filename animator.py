"""
Animator Module
Creates animated scenes with cinematic zoom effects and transitions.
Uses MoviePy 1.0.3 syntax (NOT v2).
Windows Compatible - Pillow 9.5.0+ compatible
"""

import logging
from pathlib import Path
from typing import List
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).parent))

from moviepy.editor import ImageClip, concatenate_videoclips, VideoFileClip
from config import VIDEO_CONFIG, ANIMATION_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Animator:
    """
    Creates animated video clips with cinematic effects.
    Compatible with MoviePy 1.0.3
    """

    def __init__(self):
        self.width = VIDEO_CONFIG["width"]
        self.height = VIDEO_CONFIG["height"]
        self.fps = VIDEO_CONFIG["fps"]
        self.scene_duration = ANIMATION_CONFIG["scene_duration"]
        self.zoom_factor = ANIMATION_CONFIG["zoom_factor"]
        self.transition_duration = ANIMATION_CONFIG["transition_duration"]

    def _get_pil_resample_filter(self):
        """
        Get PIL resample filter compatible with Pillow 9.5.0+
        """
        try:
            # Try newer Pillow API (10.0.0+)
            from PIL import Image
            return Image.Resampling.LANCZOS
        except AttributeError:
            # Fallback for Pillow 9.5.0
            from PIL import Image
            return Image.LANCZOS

    def _normalize_frame_to_uint8(self, frame: np.ndarray) -> np.ndarray:
        """
        Safely normalize frame array to uint8 for PIL.Image.fromarray().
        Handles both float32 (0.0-1.0 range) and uint8 (0-255 range).
        
        Args:
            frame (np.ndarray): Input frame array
            
        Returns:
            np.ndarray: Normalized uint8 frame safe for PIL
        """
        try:
            if frame is None or frame.size == 0:
                logger.warning("Invalid frame: None or empty array")
                return None
                
            # Already uint8 - validate range
            if frame.dtype == np.uint8:
                return frame
            
            # Float type - determine range and normalize
            if np.issubdtype(frame.dtype, np.floating):
                # Check actual range to determine if 0-1 or 0-255
                frame_min = frame.min()
                frame_max = frame.max()
                
                if frame_max <= 1.0:
                    # Range is 0.0-1.0, multiply by 255
                    frame = (np.clip(frame, 0.0, 1.0) * 255).astype(np.uint8)
                else:
                    # Range is 0-255, just clip and convert
                    frame = np.clip(frame, 0, 255).astype(np.uint8)
                return frame
            
            # Integer type (int32, int64, etc.) - assume 0-255 range
            if np.issubdtype(frame.dtype, np.integer):
                return np.clip(frame, 0, 255).astype(np.uint8)
            
            # Unknown type - attempt conversion via float
            logger.warning(f"Unknown frame dtype: {frame.dtype}. Attempting float conversion.")
            frame_float = frame.astype(np.float32)
            if frame_float.max() <= 1.0:
                return (np.clip(frame_float, 0.0, 1.0) * 255).astype(np.uint8)
            else:
                return np.clip(frame_float, 0, 255).astype(np.uint8)
                
        except Exception as e:
            logger.error(f"Error normalizing frame: {e}")
            raise

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
            # Load image as clip - MoviePy 1.0.3 compatible
            clip = ImageClip(str(image_path))
            clip = clip.set_duration(self.scene_duration)
            clip = clip.resize((self.width, self.height))

            # Apply zoom effect using frame processing
            def apply_zoom_effect(get_frame, t):
                """
                Apply cinematic zoom to frame.
                MoviePy 1.0.3 compatible implementation.
                """
                try:
                    from PIL import Image
                    
                    # Get frame at current time
                    frame = get_frame(t)
                    
                    # CRITICAL FIX: Normalize frame to safe uint8 format
                    frame = self._normalize_frame_to_uint8(frame)
                    if frame is None:
                        logger.error("Frame normalization failed, returning original")
                        return get_frame(t)
                    
                    # Convert to PIL Image - now guaranteed uint8
                    pil_img = Image.fromarray(frame, mode='RGB')
                    
                    # Calculate zoom progress
                    progress = t / self.scene_duration
                    zoom = 1 + (self.zoom_factor - 1) * progress
                    
                    # Calculate new size
                    new_width = int(self.width * zoom)
                    new_height = int(self.height * zoom)
                    
                    # Get resample filter
                    resample = self._get_pil_resample_filter()
                    
                    # Resize image
                    pil_img = pil_img.resize((new_width, new_height), resample)
                    
                    # Crop to center
                    left = (pil_img.width - self.width) // 2
                    top = (pil_img.height - self.height) // 2
                    right = left + self.width
                    bottom = top + self.height
                    
                    pil_img = pil_img.crop((left, top, right, bottom))
                    
                    # Convert back to numpy array
                    return np.array(pil_img, dtype=np.uint8)
                    
                except Exception as e:
                    logger.error(f"Error in zoom effect frame processing: {e}")
                    # Return original frame on error
                    return get_frame(t)

            # Apply the zoom effect - MoviePy 1.0.3 syntax
            clip = clip.fl(apply_zoom_effect)

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
                try:
                    clip = self.create_zoom_effect(image_path)
                    clips.append(clip)
                    logger.info(f"Scene clip {idx} created successfully")
                except Exception as e:
                    logger.warning(f"Failed to create clip {idx}: {e}. Skipping.")
                    continue

            if not clips:
                raise ValueError("No clips were successfully created")

            return clips

        except Exception as e:
            logger.error(f"Error creating scene clips: {str(e)}")
            raise

    def compose_clips(self, clips: List[any]) -> any:
        """
        Concatenate all clips into a single video.
        Uses MoviePy 1.0.3 syntax.

        Args:
            clips (List[VideoClip]): List of video clips

        Returns:
            VideoClip: Concatenated video
        """
        try:
            if not clips:
                raise ValueError("No clips provided for composition")

            # Concatenate clips - MoviePy 1.0.3 compatible
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
