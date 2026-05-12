"""
Pipeline Module
Orchestrates the entire workflow from input to final video export.
Implements the n8n-style modular automation pipeline.
Windows Compatible - MoviePy 1.0.3
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional
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
        try:
            self.script_gen = get_script_generator()
            self.animator = get_animator()
            self.subtitle_gen = get_subtitle_generator()
            self.composer = get_composer()
            self.output_dir = OUTPUT_DIR
            self.temp_clips = []
            logger.info("Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing pipeline: {str(e)}")
            raise

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

    def execute(
        self,
        product_name: str,
        image_paths: List[str],
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> str:
        """
        Execute the complete pipeline from images.

        Args:
            product_name (str): Name of the product
            image_paths (List[str]): List of image file paths
            progress_callback (Callable): Optional callback for progress updates

        Returns:
            str: Path to final video file
        """
        return self.run(
            product_description=" ".join(image_paths),
            product_name=product_name,
            progress_callback=progress_callback,
        )

    def run(
        self,
        product_description: str,
        product_name: str = "Product",
        voice_gender: str = "female",
        add_background_music: bool = True,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> str:
        """
        Run the complete pipeline.

        Args:
            product_description (str): Description of the product to advertise
            product_name (str): Name of the product
            voice_gender (str): Voice gender for narrator ('male', 'female')
            add_background_music (bool): Whether to add background music
            progress_callback (Callable): Optional callback for progress updates

        Returns:
            str: Path to final video file

        Raises:
            Exception: If any pipeline stage fails
        """
        try:
            logger.info(f"Starting pipeline for product: {product_name}")
            self._report_progress(progress_callback, "Initializing pipeline", 5)

            # Stage 1: Generate Script
            logger.info("Stage 1: Generating script...")
            self._report_progress(progress_callback, "Generating script", 10)
            script = self.script_gen.generate_script(
                product_name=product_name,
                product_description=product_description,
            )
            logger.info(f"Script generated with {script.get('line_count', 0)} lines")
            self._report_progress(progress_callback, "Script generated", 20)

            # Stage 2: Generate Audio
            logger.info("Stage 2: Generating audio narration...")
            self._report_progress(progress_callback, "Generating voice narration", 30)
            try:
                audio_file = self.script_gen.generate_audio(
                    script=script, voice_gender=voice_gender
                )
                logger.info(f"Audio generated: {audio_file}")
            except Exception as e:
                logger.error(f"Audio generation failed: {str(e)}")
                raise
            self._report_progress(progress_callback, "Voice narration complete", 40)

            # Stage 3: Create Animation
            logger.info("Stage 3: Creating animation frames...")
            self._report_progress(progress_callback, "Creating animations", 50)
            script_lines = script.get("script_lines", [])
            animated_clip = self.animator.create_animation(
                script=script_lines, audio_file=audio_file
            )
            self.temp_clips.append(animated_clip)
            logger.info("Animation created")
            self._report_progress(progress_callback, "Animation complete", 60)

            # Stage 4: Add Subtitles
            logger.info("Stage 4: Adding subtitles...")
            self._report_progress(progress_callback, "Adding subtitles", 70)
            subtitle_clips = self.subtitle_gen.create_subtitle_clips(
                script_lines=script_lines,
                audio_duration=self.script_gen.get_audio_duration(audio_file),
            )
            video_with_subtitles = self.subtitle_gen.overlay_subtitles(
                animated_clip, subtitle_clips
            )
            self.temp_clips.append(video_with_subtitles)
            logger.info(f"Added {len(subtitle_clips)} subtitles")
            self._report_progress(progress_callback, "Subtitles added", 75)

            # Stage 5: Compose Final Video
            logger.info("Stage 5: Composing final video with audio...")
            self._report_progress(progress_callback, "Composing audio", 80)
            background_music = (
                AUDIO_CONFIG.get("background_music_path") if add_background_music else None
            )
            final_video = self.composer.compose_with_audio(
                video_with_subtitles, audio_file, background_music
            )
            self.temp_clips.append(final_video)
            logger.info("Audio composition complete")
            self._report_progress(progress_callback, "Audio composed", 85)

            # Stage 6: Export
            logger.info("Stage 6: Exporting final video...")
            self._report_progress(progress_callback, "Exporting video", 90)
            output_file = self.composer.export_video(
                final_video,
                output_filename=f"{product_name.replace(' ', '_')}_commercial.mp4",
            )
            logger.info(f"Pipeline completed successfully: {output_file}")
            self._report_progress(progress_callback, "Export complete", 100)

            return output_file

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise

        finally:
            # Cleanup all temporary clips
            logger.info("Cleaning up temporary clips...")
            self._cleanup_clips(self.temp_clips)
            self.temp_clips = []

    def _report_progress(
        self, 
        callback: Optional[Callable[[str, int], None]], 
        message: str, 
        progress: int
    ) -> None:
        """
        Report progress via callback if provided.
        
        Args:
            callback: Progress callback function
            message: Progress message
            progress: Progress percentage (0-100)
        """
        if callback:
            try:
                callback(message, progress)
            except Exception as e:
                logger.warning(f"Error in progress callback: {e}")


def get_pipeline() -> GenerationPipeline:
    """
    Factory function to get GenerationPipeline instance.
    """
    return GenerationPipeline()
