"""
Utility script for managing voice mappings.
"""

import argparse
from voice_mapper import VoiceMapper
import os

def main():
    parser = argparse.ArgumentParser(description='Manage voice mappings')
    parser.add_argument('action', choices=['add', 'remove', 'list'],
                       help='Action to perform')
    parser.add_argument('--contact', help='Contact name')
    parser.add_argument('--voice-id', help='ElevenLabs voice ID')
    
    args = parser.parse_args()
    
    # Initialize voice mapper with default voice
    mapper = VoiceMapper(default_voice_id=os.getenv('MESSAGE_VOICE_ID', ''))
    
    if args.action == 'list':
        mappings = mapper.list_mappings()
        print("\nCurrent Voice Mappings:")
        print("----------------------")
        for contact, voice_id in mappings.items():
            print(f"{contact}: {voice_id}")
            
    elif args.action == 'add':
        if not args.contact or not args.voice_id:
            print("Error: Both --contact and --voice-id are required for add action")
            return
        mapper.add_mapping(args.contact, args.voice_id)
        print(f"Added voice mapping for {args.contact}")
        
    elif args.action == 'remove':
        if not args.contact:
            print("Error: --contact is required for remove action")
            return
        mapper.remove_mapping(args.contact)
        print(f"Removed voice mapping for {args.contact}")

if __name__ == '__main__':
    main() 