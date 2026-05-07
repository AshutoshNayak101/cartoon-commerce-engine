"""
Voice Generator Module
Converts narration text to speech using gTTS (Google Text-to-Speech)
"""

from pathlib import Path
from gtts import gTTS
import logging
from config import VOICE_CONFIG, VOICES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceGenerator:
    """
    Generates voice narration from text using gTTS.
    """

    def __init__(self):
        self.language = VOICE_CONFIG["language"]
        self.tld = VOICE_CONFIG["tld"]
        self.slow = VOICE_CONFIG["slow"]
        self.output_dir = VOICES_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_voice(self, text: str, filename: str = "narration.mp3") -> str:
        """
        Convert text to speech and save as MP3.

        Args:
            text (str): Text to convert to speech
            filename (str): Output filename

        Returns:
            str: Path to generated MP3 file
        """
        try:
            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")

            output_path = self.output_dir / filename

            # Generate speech
            tts = gTTS(
                text=text,
                lang=self.language,
                tld=self.tld,
                slow=self.slow,
            )

            # Save to file
            tts.save(str(output_path))

            logger.info(f"Voice generated successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating voice: {str(e)}")
            raise

    def get_audio_duration(self, filepath: str) -> float:
        """
        Calculate the duration of an audio file.
        Uses moviepy to get duration without loading entire file.

        Args:
            filepath (str): Path to audio file

        Returns:
            float: Duration in seconds
        """
        try:
            from moviepy.editor import AudioFileClip

            audio = AudioFileClip(filepath)
            duration = audio.duration
            audio.close()
            return duration

        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            return 0.0


def get_voice_generator() -> VoiceGenerator:
    """
    Factory function to get VoiceGenerator instance.
    """
    return VoiceGenerator()
