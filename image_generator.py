"""
Image Generator Module
Handles image processing, resizing, and scene creation from product images.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging
from typing import List, Tuple
from config import SCENES_DIR, VIDEO_CONFIG, ANIMATION_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    Processes and prepares product images for animation.
    """

    def __init__(self):
        self.output_width = VIDEO_CONFIG["width"]
        self.output_height = VIDEO_CONFIG["height"]
        self.scenes_dir = SCENES_DIR
        self.scenes_dir.mkdir(parents=True, exist_ok=True)

    def load_and_validate_image(self, image_path: str) -> Image.Image:
        """
        Load and validate image file.

        Args:
            image_path (str): Path to image file

        Returns:
            Image.Image: Loaded PIL Image
        """
        try:
            image = Image.open(image_path)
            if image.mode == "RGBA":
                image = image.convert("RGB")
            logger.info(f"Image loaded successfully: {image_path}")
            return image
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            raise

    def resize_and_center(self, image: Image.Image) -> Image.Image:
        """
        Resize image to fit 9:16 aspect ratio with proper centering.

        Args:
            image (Image.Image): Input image

        Returns:
            Image.Image: Resized image in 9:16 format
        """
        try:
            # Calculate scaling to fit within 1080x1920
            img_aspect = image.width / image.height
            target_aspect = self.output_width / self.output_height

            if img_aspect > target_aspect:
                # Image is wider, fit to height
                new_height = self.output_height
                new_width = int(new_height * img_aspect)
            else:
                # Image is taller, fit to width
                new_width = self.output_width
                new_height = int(new_width / img_aspect)

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create canvas and center image
            canvas = Image.new("RGB", (self.output_width, self.output_height), (0, 0, 0))
            offset_x = (self.output_width - new_width) // 2
            offset_y = (self.output_height - new_height) // 2
            canvas.paste(image, (offset_x, offset_y))

            logger.info(f"Image resized and centered: {self.output_width}x{self.output_height}")
            return canvas

        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            raise

    def prepare_scene_images(self, image_paths: List[str]) -> List[str]:
        """
        Prepare all product images for animation.

        Args:
            image_paths (List[str]): List of image file paths

        Returns:
            List[str]: List of processed image paths
        """
        try:
            prepared_images = []

            for idx, image_path in enumerate(image_paths):
                # Load and process
                img = self.load_and_validate_image(image_path)
                img = self.resize_and_center(img)

                # Save processed image
                output_path = self.scenes_dir / f"scene_{idx}.png"
                img.save(str(output_path))
                prepared_images.append(str(output_path))

                logger.info(f"Scene {idx} prepared: {output_path}")

            return prepared_images

        except Exception as e:
            logger.error(f"Error preparing scene images: {str(e)}")
            raise


def get_image_generator() -> ImageGenerator:
    """
    Factory function to get ImageGenerator instance.
    """
    return ImageGenerator()
