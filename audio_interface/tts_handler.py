"""
Text-to-speech processing module using ElevenLabs API.
Handles converting text to speech with different voices for narrator and messages.
"""

import os
from typing import Optional
from dataclasses import dataclass
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from .voice_mapper import VoiceMapper

@dataclass
class VoiceConfig:
    voice_id: str
    model_id: str = "eleven_multilingual_v2"

class TTSHandler:
    def __init__(self,
                 api_key: str,
                 narrator_voice: VoiceConfig,
                 voice_mapper: VoiceMapper):
        """
        Initialize TTS handler with ElevenLabs configuration.
        
        Args:
            api_key: ElevenLabs API key
            narrator_voice: Voice configuration for narrator
            voice_mapper: Voice mapping system for contacts
        """
        self.client = ElevenLabs(api_key=api_key)
        self.narrator_voice = narrator_voice
        self.voice_mapper = voice_mapper
        
    def speak_narrator_text(self, text: str) -> None:
        """
        Convert narrator text to speech and play it using configured voice.
        
        Args:
            text: Text to convert to speech
        """
        try:
            audio_stream = self.client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=self.narrator_voice.voice_id,
                model_id=self.narrator_voice.model_id
            )
            stream(audio_stream)
        except Exception as e:
            print(f"Error generating narrator speech: {e}")
        
    def speak_message_text(self, content: str, contact_name: str) -> None:
        """
        Convert message text to speech using contact's voice if available.
        
        Args:
            content: Text to convert to speech
            contact_name: Name of contact to use for voice selection
        """
        try:
            voice_id = self.voice_mapper.get_voice_id(contact_name)
            audio_stream = self.client.text_to_speech.convert_as_stream(
                text=content,
                voice_id=voice_id,
                model_id=self.narrator_voice.model_id
            )
            stream(audio_stream)
        except Exception as e:
            print(f"Error generating message speech: {e}")

def play_response(narrator_text: str, message_text: str, tts_handler: TTSHandler) -> None:
    """
    Play a complete response using appropriate voices for narrator and message.
    
    Args:
        narrator_text: Text to be spoken by narrator voice
        message_text: Text to be spoken by message voice
        tts_handler: Configured TTSHandler instance
    """
    if narrator_text:
        tts_handler.speak_narrator_text(narrator_text)
    if message_text:
        tts_handler.speak_message_text(message_text, "default") 