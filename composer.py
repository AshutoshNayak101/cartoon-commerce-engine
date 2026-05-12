"""
Composer Module - SIMPLIFIED for MoviePy 1.0.3 compatibility
Handles final video composition with audio, music, and export.
"""

import logging
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from moviepy.editor import (
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
    ImageClip,
)
from config import VIDEO_CONFIG, AUDIO_CONFIG, OUTPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Composer:
    """Composes final video with audio mixing and export."""

    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fps = VIDEO_CONFIG.get("fps", 30)
        self.codec = VIDEO_CONFIG.get("codec", "libx264")
        self.audio_codec = VIDEO_CONFIG.get("audio_codec", "aac")

    def compose_with_audio(self, video_clip: Any, voice_audio_path: str, background_music_path: str = None) -> Any:
        """Compose video with voice narration and optional background music."""
        try:
            voice_audio = AudioFileClip(voice_audio_path)
            
            # Extend video if needed
            if video_clip.duration < voice_audio.duration:
                logger.warning(f"Extending video from {video_clip.duration}s to {voice_audio.duration}s")
                try:
                    final_frame = video_clip.get_frame(video_clip.duration - 0.1)
                    extend_clip = ImageClip(final_frame).set_duration(voice_audio.duration - video_clip.duration)
                    video_clip = concatenate_videoclips([video_clip, extend_clip])
                except Exception as e:
                    logger.warning(f"Could not extend: {e}. Using set_duration.")
                    video_clip = video_clip.set_duration(voice_audio.duration)

            # Handle background music
            final_audio = voice_audio
            if background_music_path and Path(background_music_path).exists():
                try:
                    bg_audio = AudioFileClip(background_music_path)
                    loop_count = int(voice_audio.duration / bg_audio.duration) + 1
                    bg_audio = bg_audio.loop(n=loop_count).set_duration(voice_audio.duration)
                    
                    # Mix volumes
                    bg_audio = bg_audio.volumex(AUDIO_CONFIG.get("background_music_volume", 0.3))
                    voice_audio = voice_audio.volumex(AUDIO_CONFIG.get("voice_volume", 1.0))
                    
                    final_audio = CompositeAudioClip([voice_audio, bg_audio])
                except Exception as e:
                    logger.warning(f"Background music error: {e}. Using voice only.")

            final_video = video_clip.set_audio(final_audio)
            logger.info("Video and audio composed successfully")
            return final_video

        except Exception as e:
            logger.error(f"Error composing: {str(e)}")
            raise
        finally:
            try:
                if 'voice_audio' in locals():
                    voice_audio.close()
                if 'bg_audio' in locals():
                    bg_audio.close()
            except:
                pass

    def export_video(self, video_clip: Any, output_filename: str = "final_video.mp4") -> str:
        """Export video WITHOUT any extra parameters."""
        output_path = None
        try:
            output_path = self.output_dir / output_filename
            logger.info(f"Exporting to: {output_path}")

            # MINIMAL PARAMETERS ONLY - MoviePy 1.0.3 compatible
            video_clip.write_videofile(str(output_path))

            if not output_path.exists():
                raise FileNotFoundError(f"Export failed: {output_path}")
            
            file_size = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Export successful: {file_size:.2f} MB")
            return str(output_path)

        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            if output_path and output_path.exists():
                try:
                    output_path.unlink()
                except:
                    pass
            raise
        finally:
            try:
                if video_clip:
                    video_clip.close()
            except:
                pass


def get_composer() -> Composer:
    """Factory function to get Composer instance."""
    return Composer()
