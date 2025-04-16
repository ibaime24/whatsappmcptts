"""
Voice mapping module for managing contact-to-voice associations.
Maps WhatsApp contact names to their corresponding ElevenLabs voice IDs.
"""

from typing import Dict, Optional
import os
import json
from pathlib import Path

class VoiceMapper:
    def __init__(self, default_voice_id: str, config_path: Optional[str] = None):
        """
        Initialize voice mapper with default voice and optional config path.
        
        Args:
            default_voice_id: Fallback voice ID if no mapping exists
            config_path: Optional path to JSON config file for persistent mappings
        """
        self.default_voice_id = default_voice_id
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'voice_mappings.json'
        )
        self.voice_map = self._load_voice_mappings()
        
    def _load_voice_mappings(self) -> Dict[str, str]:
        """
        Load voice mappings from both environment variables and config file.
        Environment variables take precedence over config file.
        """
        # Load from config file first
        voice_map = self._load_from_config()
        
        # Override with any environment variables
        for key, value in os.environ.items():
            if key.startswith('VOICE_MAP_'):
                contact_name = key[10:].lower()  # Convert VOICE_MAP_NAME to name
                voice_map[contact_name] = value
                
        return voice_map
    
    def _load_from_config(self) -> Dict[str, str]:
        """Load voice mappings from JSON config file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading voice mappings from config: {e}")
        return {}
    
    def _save_to_config(self) -> None:
        """Save current voice mappings to config file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.voice_map, f, indent=2)
        except Exception as e:
            print(f"Error saving voice mappings to config: {e}")
    
    def get_voice_id(self, contact_name: str) -> str:
        """
        Get voice ID for a contact, falling back to default if not found.
        
        Args:
            contact_name: Name of contact to look up
            
        Returns:
            ElevenLabs voice ID to use for this contact
        """
        return self.voice_map.get(contact_name.lower(), self.default_voice_id)
    
    def add_mapping(self, contact_name: str, voice_id: str) -> None:
        """
        Add or update a voice mapping.
        
        Args:
            contact_name: Name of contact to map
            voice_id: ElevenLabs voice ID to use
        """
        self.voice_map[contact_name.lower()] = voice_id
        self._save_to_config()
    
    def remove_mapping(self, contact_name: str) -> None:
        """
        Remove a voice mapping.
        
        Args:
            contact_name: Name of contact to remove mapping for
        """
        self.voice_map.pop(contact_name.lower(), None)
        self._save_to_config()
    
    def list_mappings(self) -> Dict[str, str]:
        """Get all current voice mappings."""
        return dict(self.voice_map) 