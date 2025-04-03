"""
Audio capture and speech-to-text processing module.
Handles recording audio and converting it to text using Whisper API.
"""

import os
import tempfile
import wave
import pyaudio
from typing import Optional, Tuple
from openai import OpenAI

class AudioRecorder:
    def __init__(self, 
                 temp_dir: str = None,
                 chunk: int = 1024,
                 format: int = pyaudio.paInt16,
                 channels: int = 1,
                 rate: int = 16000):
        """
        Initialize audio recorder with specified parameters.
        
        Args:
            temp_dir: Directory to store temporary audio files
            chunk: Audio chunk size
            format: Audio format (default: 16-bit int)
            channels: Number of audio channels (default: mono)
            rate: Sampling rate (default: 16kHz, good for Whisper)
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.p = None
        self.stream = None
        self.frames = []
        
    def start_recording(self) -> None:
        """Start recording audio."""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.frames = []
        
    def stop_recording(self) -> str:
        """
        Stop recording and save the audio to a temporary file.
        
        Returns:
            str: Path to the saved audio file
        """
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.p:
            self.p.terminate()
            
        # Save to temporary file
        temp_file = os.path.join(self.temp_dir, f"recording_{os.getpid()}.wav")
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            
        return temp_file

    def record_chunk(self) -> None:
        """Record a single chunk of audio."""
        if self.stream:
            data = self.stream.read(self.chunk)
            self.frames.append(data)

def process_with_whisper(audio_file: str, api_key: str) -> Tuple[str, bool]:
    """
    Process audio file with Whisper API.
    
    Args:
        audio_file: Path to the audio file
        api_key: OpenAI API key
        
    Returns:
        Tuple[str, bool]: (transcribed text, success status)
    """
    try:
        # Initialize OpenAI client with API key
        client = OpenAI(api_key=api_key)
        
        # Open audio file in binary read mode
        with open(audio_file, "rb") as audio:
            # Create transcription using Whisper model
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe", # gpt-4o-transcribe is the correct model - do not change
                file=audio,
                response_format="text"
            )
            
        # Return transcribed text and success status
        return transcription, True
        
    except Exception as e:
        print(f"Error processing audio with Whisper: {e}")
        return "", False

def cleanup_audio_file(file_path: str) -> None:
    """
    Clean up temporary audio file.
    
    Args:
        file_path: Path to the file to delete
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up audio file {file_path}: {e}") 