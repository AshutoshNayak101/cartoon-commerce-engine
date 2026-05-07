"""
Background Music Module
Manages background music for video composition.
"""

import logging
from pathlib import Path
from config import MUSIC_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackgroundMusicManager:
    """
    Manages background music for video.
    Provides cinematic background music tracks.
    """

    def __init__(self):
        self.music_dir = MUSIC_DIR
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.default_music = self._get_default_music_path()

    def _get_default_music_path(self) -> str:
        """
        Get path to default background music.
        Returns None if no music available (will be handled gracefully in composer).

        Returns:
            str: Path to music file or None
        """
        try:
            # Check if any music files exist
            music_files = list(self.music_dir.glob("*.mp3")) + list(self.music_dir.glob("*.wav"))
            if music_files:
                return str(music_files[0])
            return None

        except Exception as e:
            logger.error(f"Error getting default music path: {str(e)}")
            return None

    def get_music_path(self, music_type: str = "cinematic") -> str:
        """
        Get music file path for specified type.

        Args:
            music_type (str): Type of music (cinematic, upbeat, etc.)

        Returns:
            str: Path to music file or None
        """
        try:
            music_file = self.music_dir / f"{music_type}.mp3"
            if music_file.exists():
                return str(music_file)
            return self.default_music

        except Exception as e:
            logger.error(f"Error getting music path: {str(e)}")
            return None

    def upload_music(self, source_path: str, music_type: str = "cinematic") -> str:
        """
        Upload custom background music.

        Args:
            source_path (str): Path to source music file
            music_type (str): Type label for music

        Returns:
            str: Path to uploaded music file
        """
        try:
            import shutil

            if not Path(source_path).exists():
                raise FileNotFoundError(f"Source music file not found: {source_path}")

            dest_path = self.music_dir / f"{music_type}.mp3"
            shutil.copy(source_path, str(dest_path))
            logger.info(f"Music uploaded: {dest_path}")
            return str(dest_path)

        except Exception as e:
            logger.error(f"Error uploading music: {str(e)}")
            raise


def get_background_music_manager() -> BackgroundMusicManager:
    """
    Factory function to get BackgroundMusicManager instance.
    """
    return BackgroundMusicManager()
