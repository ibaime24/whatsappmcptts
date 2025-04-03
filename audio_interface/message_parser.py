"""
Message parser module for formatting WhatsApp responses into narrator and message components.
"""

from typing import Tuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ParsedResponse:
    narrator_text: str
    message_text: str

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp into human-readable string."""
    return timestamp.strftime("%B %d at %I:%M %p")

def parse_last_message_response(message: Dict[str, Any]) -> ParsedResponse:
    """
    Parse a last message response into narrator and message components.
    
    Args:
        message: Message dictionary from WhatsApp API
        
    Returns:
        ParsedResponse with separated narrator and message text
    """
    timestamp = datetime.fromisoformat(message['timestamp'])
    is_from_me = message['is_from_me']
    content = message['content']
    chat_name = message.get('chat_name', 'Unknown')
    
    if is_from_me:
        narrator_text = f"Your last message to {chat_name} was sent on {format_timestamp(timestamp)} and said:"
    else:
        narrator_text = f"The last message from {chat_name} was sent on {format_timestamp(timestamp)} and said:"
    
    return ParsedResponse(
        narrator_text=narrator_text,
        message_text=content
    )

def parse_message_context(context: Dict[str, Any]) -> ParsedResponse:
    """
    Parse message context into narrator and message components.
    
    Args:
        context: Message context dictionary from WhatsApp API
        
    Returns:
        ParsedResponse with separated narrator and message text
    """
    # TODO: Implement context parsing
    raise NotImplementedError("Message context parsing not yet implemented") 