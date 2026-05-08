"""
Composer Module
Handles final video composition with audio, music, and export.
Uses MoviePy 1.0.3 syntax.
Windows Compatible Implementation
"""

import logging
from pathlib import Path
from typing import Any
import sys

# Add current directory to path for relative imports
sys.path.insert(0, str(Path(__file__).parent))

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_audioclips,
    CompositeAudioClip,
)
from config import VIDEO_CONFIG, AUDIO_CONFIG, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Composer:
    """
    Composes final video with audio mixing and export.
    """

    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fps = VIDEO_CONFIG["fps"]
        self.codec = VIDEO_CONFIG["codec"]
        self.audio_codec = VIDEO_CONFIG["audio_codec"]

    def compose_with_audio(
        self,
        video_clip: Any,
        voice_audio_path: str,
        background_music_path: str = None,
    ) -> Any:
        """
        Compose video with voice narration and optional background music.

        Args:
            video_clip (VideoClip): Main video clip
            voice_audio_path (str): Path to voice narration audio
            background_music_path (str): Path to background music (optional)

        Returns:
            VideoClip: Video with composed audio
        """
        try:
            # Load voice audio
            voice_audio = AudioFileClip(voice_audio_path)
            
            # FIX: Safely extend video duration without black frames
            if video_clip.duration < voice_audio.duration:
                logger.warning(
                    f"Video duration ({video_clip.duration}s) is less than audio ({voice_audio.duration}s). "
                    f"Extending video by looping final frame."
                )
                # Loop the final frame instead of stretching
                from moviepy.video.io.VideoFileClip import VideoFileClip
                try:
                    # Create extended clip by repeating/looping
                    final_frame = video_clip.get_frame(video_clip.duration - 0.1)
                    from moviepy.editor import ImageClip
                    extend_clip = ImageClip(final_frame).set_duration(
                        voice_audio.duration - video_clip.duration
                    )
                    from moviepy.editor import concatenate_videoclips
                    video_clip = concatenate_videoclips([video_clip, extend_clip])
                except Exception as e:
                    logger.warning(f"Could not loop final frame: {e}. Using set_duration instead.")
                    # Fallback: just set duration
                    video_clip = video_clip.set_duration(voice_audio.duration)

            # Create audio composition
            if background_music_path and Path(background_music_path).exists():
                try:
                    background_audio = AudioFileClip(background_music_path)
                    background_audio = background_audio.loop(n=int(voice_audio.duration / background_audio.duration) + 1)
                    background_audio = background_audio.set_duration(voice_audio.duration)

                    # Scale background music volume
                    background_audio = background_audio.volumex(AUDIO_CONFIG["background_music_volume"])
                    voice_audio = voice_audio.volumex(AUDIO_CONFIG["voice_volume"])

                    # Composite audio
                    final_audio = CompositeAudioClip([voice_audio, background_audio])
                except Exception as music_error:
                    logger.warning(f"Background music loading failed: {music_error}. Using voice only.")
                    final_audio = voice_audio
            else:
                logger.info("No background music file provided. Using voice only.")
                final_audio = voice_audio

            # Set audio to video
            final_video = video_clip.set_audio(final_audio)

            logger.info("Video and audio composed successfully")
            return final_video

        except Exception as e:
            logger.error(f"Error composing video with audio: {str(e)}")
            raise
        finally:
            # FIX: Always cleanup audio resources to prevent memory leaks
            try:
                if 'voice_audio' in locals() and voice_audio is not None:
                    voice_audio.close()
                if 'background_audio' in locals() and background_audio is not None:
                    background_audio.close()
            except Exception as cleanup_error:
                logger.warning(f"Error closing audio clips: {cleanup_error}")

    def export_video(
        self,
        video_clip: Any,
        output_filename: str = "final_video.mp4",
        verbose: bool = False,
        progress_bar: bool = True,
    ) -> str:
        """
        Export final video to MP4 file.

        Args:
            video_clip (VideoClip): Final video clip
            output_filename (str): Output filename
            verbose (bool): Show verbose output
            progress_bar (bool): Show progress bar

        Returns:
            str: Path to exported video

        Raises:
            FileNotFoundError: If export fails to create file
        """
        output_path = None
        try:
            output_path = self.output_dir / output_filename

            logger.info(f"Exporting video to: {output_path}")

            # Export video with Windows-compatible parameters
            video_clip.write_videofile(
                str(output_path),
                fps=self.fps,
                codec=self.codec,
                audio_codec=self.audio_codec,
                verbose=verbose,
                progress_bar=progress_bar,
            )

            # FIX: Validate that file was actually created
            if not output_path.exists():
                raise FileNotFoundError(
                    f"Video export failed: Output file not created at {output_path}"
                )
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            if file_size_mb < 1:
                raise ValueError(
                    f"Video export created invalid file: Size is only {file_size_mb:.2f} MB"
                )

            logger.info(f"Video exported successfully: {output_path} ({file_size_mb:.2f} MB)")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error exporting video: {str(e)}")
            # Clean up partial/invalid file
            if output_path and output_path.exists():
                try:
                    output_path.unlink()
                    logger.info(f"Cleaned up invalid export file: {output_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not clean up failed export: {cleanup_error}")
            raise
        finally:
            # FIX: Always cleanup video clip resource
            try:
                if video_clip is not None:
                    video_clip.close()
            except Exception as cleanup_error:
                logger.warning(f"Error closing video clip: {cleanup_error}")


def get_composer() -> Composer:
    """
    Factory function to get Composer instance.
    """
    return Composer()
