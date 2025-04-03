"""
Voice interface for WhatsApp commands.
Records audio, converts to text, and automatically processes WhatsApp commands.
"""

import os
import sys
from typing import Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Add WhatsApp server to path
whatsapp_server = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'whatsapp-mcp-server')
if whatsapp_server not in sys.path:
    sys.path.insert(0, whatsapp_server)

from whatsapp import search_contacts, get_last_interaction

from .audio_capture import AudioRecorder, process_with_whisper, cleanup_audio_file
from .tts_handler import TTSHandler, VoiceConfig

@dataclass
class Config:
    openai_api_key: str
    elevenlabs_api_key: str
    narrator_voice_id: str
    message_voice_id: str
    temp_dir: Optional[str] = None

class VoiceCommandInterface:
    def __init__(self, config: Config):
        """Initialize the voice interface with configuration."""
        self.config = config
        self.audio_recorder = AudioRecorder(temp_dir=config.temp_dir)
        self.tts_handler = TTSHandler(
            api_key=config.elevenlabs_api_key,
            narrator_voice=VoiceConfig(voice_id=config.narrator_voice_id),
            message_voice=VoiceConfig(voice_id=config.message_voice_id)
        )

    def process_whatsapp_command(self, command: str) -> None:
        """
        Process WhatsApp command and speak the response.
        
        Args:
            command: Transcribed voice command
        """
        command = command.lower().strip()
        name = None
        
        try:
            # Extract name using various patterns
            if "from" in command:
                name = command.split("from")[-1].strip()
            elif "to" in command:
                name = command.split("to")[-1].strip()
            elif "what did" in command and "say" in command:
                # Pattern: "what did [name] say"
                parts = command.split("what did")[-1].split("say")[0].strip()
                if parts:
                    name = parts
            elif "message" in command:
                # Look for a name near "message"
                words = command.split()
                msg_idx = words.index("message")
                # Look at words before and after "message"
                for i in range(max(0, msg_idx-3), min(len(words), msg_idx+4)):
                    if words[i] not in {"what", "is", "the", "last", "message", "from", "to", "get", "show", "me", "latest", "recent"}:
                        name = words[i]
                        break
            
            if name:
                # Clean up the extracted name
                name = name.strip("?!.,")
                print(f"Looking for messages from: {name}")
                
                # Search for contact
                contacts = search_contacts(name)
                if not contacts:
                    self.tts_handler.speak_narrator_text(f"Could not find contact named {name}")
                    return
                    
                # Get last interaction
                message = get_last_interaction(contacts[0].jid)  # Use attribute access
                if not message:
                    self.tts_handler.speak_narrator_text(f"No messages found with {name}")
                    return
                
                # Format response
                timestamp = message.timestamp.strftime("%I:%M %p on %B %d")
                content = message.content
                is_from_me = message.is_from_me
                
                if is_from_me:
                    narrator_text = f"Your last message to {name} was sent at {timestamp} and said:"
                else:
                    narrator_text = f"The last message from {name} was sent at {timestamp} and said:"
                
                # Speak response
                self.tts_handler.speak_narrator_text(narrator_text)
                self.tts_handler.speak_message_text(content)
                return
            
            # If command not recognized
            self.tts_handler.speak_narrator_text(
                "I'm sorry, I don't understand that command. Try saying something like:\n"
                "- What was the last message from [name]\n"
                "- What did [name] say\n"
                "- Show me the latest message from [name]"
            )
            
        except Exception as e:
            print(f"Error processing command: {e}")
            self.tts_handler.speak_narrator_text(f"An error occurred while processing your command: {str(e)}")
        
    def run(self):
        """Run the voice interface in a loop."""
        print("Starting Voice Command Interface...")
        print("Press Ctrl+C to stop recording when you're done speaking")
        
        try:
            while True:
                # Start recording
                print("\nListening... (Press Ctrl+C to stop recording)")
                self.audio_recorder.start_recording()
                
                try:
                    while True:
                        self.audio_recorder.record_chunk()
                except KeyboardInterrupt:
                    # Stop recording on Ctrl+C
                    audio_file = self.audio_recorder.stop_recording()
                    
                    try:
                        # Process with Whisper
                        command, success = process_with_whisper(
                            audio_file,
                            self.config.openai_api_key
                        )
                        
                        if not success:
                            self.tts_handler.speak_narrator_text("Failed to process speech. Please try again.")
                            continue
                            
                        # Echo the command back
                        print(f"\nCommand: {command}")
                        self.tts_handler.speak_narrator_text("I heard:")
                        self.tts_handler.speak_message_text(command)
                        
                        # Process the command
                        self.process_whatsapp_command(command)
                        
                        # Cleanup
                        cleanup_audio_file(audio_file)
                        
                        # Ask if user wants to record another command
                        self.tts_handler.speak_narrator_text("Would you like to try another command?")
                        response = input("Try another command? (y/n): ")
                        if response.lower() != 'y':
                            raise KeyboardInterrupt
                        
                    except Exception as e:
                        print(f"Error processing command: {e}")
                        self.tts_handler.speak_narrator_text(f"An error occurred: {str(e)}")
                        
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.tts_handler.speak_narrator_text("Shutting down. Goodbye!")
            
def main():
    """Entry point for the voice interface."""
    # Load configuration from environment variables
    config = Config(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
        narrator_voice_id=os.getenv("NARRATOR_VOICE_ID"),
        message_voice_id=os.getenv("MESSAGE_VOICE_ID"),
        temp_dir=os.getenv("TEMP_DIR")
    )
    
    if not config.openai_api_key:
        print("Error: OPENAI_API_KEY not found in .env file")
        sys.exit(1)
        
    if not config.elevenlabs_api_key:
        print("Error: ELEVENLABS_API_KEY not found in .env file")
        sys.exit(1)
        
    if not config.narrator_voice_id or not config.message_voice_id:
        print("Error: Voice IDs not found in .env file")
        sys.exit(1)
    
    # Initialize and run interface
    interface = VoiceCommandInterface(config)
    interface.run()

if __name__ == "__main__":
    main() 