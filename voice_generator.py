"""
Voice Generator Module
Converts narration text to speech using gTTS (Google Text-to-Speech)
Windows Compatible
"""

from pathlib import Path
from gtts import gTTS
import logging
import time
import sys

sys.path.insert(0, str(Path(__file__).parent))

from config import VOICE_CONFIG, VOICES_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_GTTS_MAX_RETRIES = 3
_GTTS_RETRY_DELAY = 2  # seconds between retries


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

        Retries up to _GTTS_MAX_RETRIES times on transient network errors.

        Args:
            text (str): Text to convert to speech
            filename (str): Output filename

        Returns:
            str: Path to generated MP3 file

        Raises:
            ValueError: If text is empty
            ConnectionError: If gTTS cannot reach Google's servers after all retries
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")

        output_path = self.output_dir / filename

        tts = gTTS(
            text=text,
            lang=self.language,
            tld=self.tld,
            slow=self.slow,
        )

        last_error = None
        for attempt in range(1, _GTTS_MAX_RETRIES + 1):
            try:
                tts.save(str(output_path))
                logger.info(f"Voice generated successfully: {output_path}")
                return str(output_path)
            except Exception as e:
                last_error = e
                logger.warning(
                    f"gTTS attempt {attempt}/{_GTTS_MAX_RETRIES} failed: {e}"
                )
                if attempt < _GTTS_MAX_RETRIES:
                    time.sleep(_GTTS_RETRY_DELAY)

        # All retries exhausted
        logger.error(f"Voice generation failed after {_GTTS_MAX_RETRIES} attempts: {last_error}")
        raise ConnectionError(
            f"Voice narration requires an internet connection to Google Text-to-Speech. "
            f"Please check your connection and try again. (Detail: {last_error})"
        )

    def get_audio_duration(self, filepath: str) -> float:
        """
        Calculate the duration of an audio file.
        Uses moviepy to get duration.

        Args:
            filepath (str): Path to audio file

        Returns:
            float: Duration in seconds
        """
        try:
            from moviepy.editor import AudioFileClip

            audio = AudioFileClip(str(filepath))
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
