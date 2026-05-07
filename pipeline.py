"""
Pipeline Module
Orchestrates the entire workflow from input to final video export.
Implements the n8n-style modular automation pipeline.
Windows Compatible - MoviePy 1.0.3
"""

import logging
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent))

from script_generator import get_script_generator
from voice_generator import get_voice_generator
from image_generator import get_image_generator
from animator import get_animator
from subtitle_generator import get_subtitle_generator
from composer import get_composer
from background_music import get_background_music_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenerationPipeline:
    """
    Orchestrates the complete reel generation workflow.
    7-step process: Script → Voice → Images → Animation → Subtitles → Music → Export
    """

    def __init__(self):
        try:
            self.script_gen = get_script_generator()
            self.voice_gen = get_voice_generator()
            self.image_gen = get_image_generator()
            self.animator = get_animator()
            self.subtitle_gen = get_subtitle_generator()
            self.composer = get_composer()
            self.music_manager = get_background_music_manager()
            logger.info("Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            raise

    def _cleanup_clips(self, clips_to_cleanup: List[any]) -> None:
        """
        FIX: Properly cleanup all video/audio clips to prevent memory leaks.
        
        Args:
            clips_to_cleanup (List): List of MoviePy clip objects to cleanup
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
        progress_callback=None,
    ) -> str:
        """
        Execute complete pipeline from product name and images to final video.

        Args:
            product_name (str): Name of the product
            image_paths (List[str]): List of product image paths
            progress_callback (function): Callback for progress updates

        Returns:
            str: Path to final video file
        """
        # FIX: Track all clips for proper cleanup
        clips_for_cleanup = []
        
        try:
            # Validate inputs
            if not product_name or not image_paths:
                raise ValueError("Product name and image paths are required")

            # Step 1: Generate Script
            logger.info("Step 1: Generating dialogue script...")
            if progress_callback:
                progress_callback("Generating dialogue script...", 15)

            script_data = self.script_gen.generate_script(product_name)
            script_lines = script_data["script_lines"]
            narration_text = script_data["narration_text"]
            logger.info(f"Script generated with {len(script_lines)} lines")

            # Step 2: Generate Voice Narration
            logger.info("Step 2: Generating voice narration...")
            if progress_callback:
                progress_callback("Generating voice narration...", 30)

            voice_path = self.voice_gen.generate_voice(narration_text, "narration.mp3")
            audio_duration = self.voice_gen.get_audio_duration(voice_path)
            
            # FIX: Validate audio duration to prevent downstream errors
            if audio_duration <= 0:
                raise ValueError(f"Invalid audio duration: {audio_duration}s")
                
            logger.info(f"Voice generated: {voice_path} (Duration: {audio_duration:.2f}s)")

            # Step 3: Process Product Images
            logger.info("Step 3: Processing product images...")
            if progress_callback:
                progress_callback("Processing images...", 45)

            prepared_images = self.image_gen.prepare_scene_images(image_paths)
            if not prepared_images:
                raise ValueError("No images were successfully prepared")
            logger.info(f"Processed {len(prepared_images)} images")

            # Step 4: Create Animated Scenes
            logger.info("Step 4: Creating animated scenes...")
            if progress_callback:
                progress_callback("Creating animated scenes...", 60)

            scene_clips = self.animator.create_scene_clips(prepared_images)
            # FIX: Track clips for cleanup
            clips_for_cleanup.extend(scene_clips)
            
            video_clip = self.animator.compose_clips(scene_clips)
            clips_for_cleanup.append(video_clip)
            logger.info(f"Animated {len(scene_clips)} scenes into video")

            # Step 5: Generate Subtitles
            logger.info("Step 5: Generating subtitles...")
            if progress_callback:
                progress_callback("Generating subtitles...", 70)

            subtitle_clips = self.subtitle_gen.create_subtitle_clips(script_lines, audio_duration)
            video_with_subtitles = self.subtitle_gen.overlay_subtitles(video_clip, subtitle_clips)
            clips_for_cleanup.append(video_with_subtitles)
            logger.info(f"Added {len(subtitle_clips)} subtitle clips")

            # Step 6: Add Background Music
            logger.info("Step 6: Adding background music...")
            if progress_callback:
                progress_callback("Adding background music...", 80)

            music_path = self.music_manager.get_music_path("cinematic")
            final_video = self.composer.compose_with_audio(
                video_with_subtitles,
                voice_path,
                music_path,
            )
            clips_for_cleanup.append(final_video)
            logger.info("Audio mixed with narration")

            # Step 7: Export Final Video
            logger.info("Step 7: Exporting final video...")
            if progress_callback:
                progress_callback("Exporting final video...", 90)

            output_path = self.composer.export_video(
                final_video,
                output_filename="final_video.mp4",
                verbose=False,
                progress_bar=True,
            )

            logger.info(f"Pipeline completed successfully! Output: {output_path}")
            if progress_callback:
                progress_callback("Reel generation completed!", 100)

            return output_path

        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            raise
        finally:
            # FIX: Always cleanup clips to prevent memory leaks
            logger.info(f"Cleaning up {len(clips_for_cleanup)} clips from memory...")
            self._cleanup_clips(clips_for_cleanup)
            logger.info("Pipeline cleanup completed")


def get_pipeline() -> GenerationPipeline:
    """
    Factory function to get GenerationPipeline instance.
    """
    return GenerationPipeline()
