"""
Pipeline Module
Orchestrates the entire workflow from input to final video export.
Implements the n8n-style modular automation pipeline.
Windows Compatible - MoviePy 1.0.3
"""

import logging
from pathlib import Path
from typing import Dict, List, Any
import sys

sys.path.insert(0, str(Path(__file__).parent))

from script_generator import get_script_generator
from animator import get_animator
from subtitle_generator import get_subtitle_generator
from composer import get_composer
from config import VIDEO_CONFIG, ANIMATION_CONFIG, OUTPUT_DIR, AUDIO_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenerationPipeline:
    """
    Main pipeline orchestrator.
    Coordinates script generation → animation → subtitle → audio → export.
    """

    def __init__(self):
        self.script_gen = get_script_generator()
        self.animator = get_animator()
        self.subtitle_gen = get_subtitle_generator()
        self.composer = get_composer()
        self.output_dir = OUTPUT_DIR
        self.temp_clips = []

    def _cleanup_clips(self, clips_to_cleanup: List[Any]) -> None:
        """
        Safely cleanup MoviePy clips to prevent memory leaks.
        
        Args:
            clips_to_cleanup (List[Any]): List of video/audio clips to close
        """
        for clip in clips_to_cleanup:
            try:
                if clip is not None and hasattr(clip, 'close'):
                    clip.close()
            except Exception as e:
                logger.warning(f"Error closing clip: {e}")

    def run(
        self,
        product_description: str,
        product_name: str = "Product",
        voice_gender: str = "female",
        add_background_music: bool = True,
    ) -> str:
        """
        Run the complete pipeline.

        Args:
            product_description (str): Description of the product to advertise
            product_name (str): Name of the product
            voice_gender (str): Voice gender for narrator ('male', 'female')
            add_background_music (bool): Whether to add background music

        Returns:
            str: Path to final video file

        Raises:
            Exception: If any pipeline stage fails
        """
        try:
            logger.info(f"Starting pipeline for product: {product_name}")

            # Stage 1: Generate Script
            logger.info("Stage 1: Generating script...")
            script = self.script_gen.generate_script(
                product_name=product_name,
                product_description=product_description,
            )
            logger.info(f"Script generated with {len(script)} lines")

            # Stage 2: Generate Audio
            logger.info("Stage 2: Generating audio narration...")
            audio_file = self.script_gen.generate_audio(
                script=script, voice_gender=voice_gender
            )
            logger.info(f"Audio generated: {audio_file}")

            # Stage 3: Create Animation
            logger.info("Stage 3: Creating animation frames...")
            animated_clip = self.animator.create_animation(
                script=script, audio_file=audio_file
            )
            self.temp_clips.append(animated_clip)
            logger.info("Animation created")

            # Stage 4: Add Subtitles
            logger.info("Stage 4: Adding subtitles...")
            subtitle_clips = self.subtitle_gen.create_subtitle_clips(
                script_lines=script,
                audio_duration=self.script_gen.get_audio_duration(audio_file),
            )
            video_with_subtitles = self.subtitle_gen.overlay_subtitles(
                animated_clip, subtitle_clips
            )
            self.temp_clips.append(video_with_subtitles)
            logger.info(f"Added {len(subtitle_clips)} subtitles")

            # Stage 5: Compose Final Video
            logger.info("Stage 5: Composing final video with audio...")
            background_music = (
                AUDIO_CONFIG.get("background_music_path") if add_background_music else None
            )
            final_video = self.composer.compose_with_audio(
                video_with_subtitles, audio_file, background_music
            )
            self.temp_clips.append(final_video)
            logger.info("Audio composition complete")

            # Stage 6: Export
            logger.info("Stage 6: Exporting final video...")
            output_file = self.composer.export_video(
                final_video,
                output_filename=f"{product_name.replace(' ', '_')}_commercial.mp4",
            )
            logger.info(f"Pipeline completed successfully: {output_file}")

            return output_file

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

        finally:
            # Cleanup all temporary clips
            logger.info("Cleaning up temporary clips...")
            self._cleanup_clips(self.temp_clips)
            self.temp_clips = []


def get_pipeline() -> GenerationPipeline:
    """
    Factory function to get GenerationPipeline instance.
    """
    return GenerationPipeline()
