"""
Script Generator Module
Generates funny, engaging cartoon dialogue between Robot Cat and Boy
for product showcase reels.
Windows Compatible Implementation
"""

import random
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScriptGenerator:
    """
    Generates product showcase dialogue scripts.
    Uses Robot Cat and Boy characters for engaging storytelling.
    """

    def __init__(self):
        self.characters = ["Robot Cat", "Boy"]
        self.dialogue_templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, List[str]]:
        """
        Initialize dialogue templates for various product types.
        """
        return {
            "opening": [
                "🤖 {char1}: Hey! Look at this amazing {product}!",
                "🤖 {char1}: OMG! This {product} just blew my mind!",
                "🤖 {char1}: Check out this incredible {product}!",
            ],
            "reaction": [
                "👦 {char2}: Wow! What makes it so special?",
                "👦 {char2}: That looks awesome! Tell me more!",
                "👦 {char2}: I need this in my life!",
            ],
            "feature": [
                "🤖 {char1}: It's perfect for everyday use!",
                "🤖 {char1}: Quality that lasts forever!",
                "🤖 {char1}: Affordable and amazing!",
            ],
            "emotional": [
                "👦 {char2}: This is life-changing!",
                "👦 {char2}: I'm obsessed!",
                "👦 {char2}: Best purchase ever!",
            ],
            "cta": [
                "🤖 {char1}: Grab yours before stock ends!",
                "🤖 {char1}: Limited time offer - buy now!",
                "🤖 {char1}: Don't miss out!",
            ],
        }

    def generate_script(self, product_name: str, product_description: str = "") -> Dict[str, Any]:
        """
        Generate a complete product showcase script.

        Args:
            product_name (str): Name of the product to showcase
            product_description (str): Description of product (optional)

        Returns:
            Dict containing script_lines and narration_text
        """
        try:
            script_lines = []
            narration_parts = []

            # Opening
            opening = random.choice(self.dialogue_templates["opening"]).format(
                char1=self.characters[0], product=product_name
            )
            script_lines.append({"character": self.characters[0], "dialogue": opening})
            narration_parts.append(opening.replace("🤖 Robot Cat: ", "").replace("👦 Boy: ", ""))

            # Reaction
            reaction = random.choice(self.dialogue_templates["reaction"]).format(
                char2=self.characters[1]
            )
            script_lines.append({"character": self.characters[1], "dialogue": reaction})
            narration_parts.append(reaction.replace("🤖 Robot Cat: ", "").replace("👦 Boy: ", ""))

            # Feature
            feature = random.choice(self.dialogue_templates["feature"]).format(
                char1=self.characters[0]
            )
            script_lines.append({"character": self.characters[0], "dialogue": feature})
            narration_parts.append(feature.replace("🤖 Robot Cat: ", "").replace("👦 Boy: ", ""))

            # Emotional
            emotional = random.choice(self.dialogue_templates["emotional"]).format(
                char2=self.characters[1]
            )
            script_lines.append({"character": self.characters[1], "dialogue": emotional})
            narration_parts.append(emotional.replace("🤖 Robot Cat: ", "").replace("👦 Boy: ", ""))

            # CTA
            cta = random.choice(self.dialogue_templates["cta"]).format(
                char1=self.characters[0]
            )
            script_lines.append({"character": self.characters[0], "dialogue": cta})
            narration_parts.append(cta.replace("🤖 Robot Cat: ", "").replace("👦 Boy: ", ""))

            # Combine narration
            narration_text = " ".join(narration_parts)

            logger.info(f"Generated script for product: {product_name}")

            return {
                "product_name": product_name,
                "script_lines": script_lines,
                "narration_text": narration_text,
                "line_count": len(script_lines),
            }

        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise

    def generate_audio(self, script: Dict[str, Any], voice_gender: str = "female") -> str:
        """
        Generate audio from script narration.
        
        Args:
            script (Dict): Script dictionary with narration_text
            voice_gender (str): Gender for voice (female/male)
            
        Returns:
            str: Path to generated audio file
        """
        try:
            from voice_generator import get_voice_generator
            
            voice_gen = get_voice_generator()
            narration_text = script.get("narration_text", "")
            
            if not narration_text:
                raise ValueError("No narration text in script")
            
            audio_file = voice_gen.generate_voice(
                text=narration_text,
                filename="narration.mp3"
            )
            return audio_file
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise

    def get_audio_duration(self, filepath: str) -> float:
        """
        Get duration of audio file.
        
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
            return 5.0  # Default fallback


def get_script_generator() -> ScriptGenerator:
    """
    Factory function to get ScriptGenerator instance.
    """
    return ScriptGenerator()
