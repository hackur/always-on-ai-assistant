#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the text-to-speech functionality.

This script demonstrates the text-to-speech functionality of the Always-On AI Assistant.
It creates a TextToSpeechOutputLayer instance and uses it to speak a test message.

Usage:
    python test_tts.py [--engine ENGINE] [--voice VOICE_ID] [--rate RATE] [--volume VOLUME]

Example:
    python test_tts.py
    python test_tts.py --engine gtts
    python test_tts.py --engine pyttsx3 --rate 150 --volume 0.8
"""

import sys
import os
import argparse
import time

# Add the parent directory to sys.path to import layers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from layers.output_layer import TextToSpeechOutputLayer, PYTTSX3_AVAILABLE, GTTS_AVAILABLE
except ImportError as e:
    print(f"Error importing output layer: {e}")
    print("Make sure you have installed the required dependencies.")
    sys.exit(1)


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Test the text-to-speech functionality")
    parser.add_argument(
        "--engine",
        choices=["pyttsx3", "gtts"],
        default="pyttsx3",
        help="The TTS engine to use (default: pyttsx3)"
    )
    parser.add_argument(
        "--voice",
        help="The voice ID to use (for pyttsx3 only)"
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=150,
        help="The speech rate (words per minute, for pyttsx3 only, default: 150)"
    )
    parser.add_argument(
        "--volume",
        type=float,
        default=1.0,
        help="The speech volume (0.0 to 1.0, for pyttsx3 only, default: 1.0)"
    )
    parser.add_argument(
        "--language",
        default="en",
        help="The language code (for gTTS only, default: en)"
    )
    return parser.parse_args()


def main():
    """
    Main function to test the text-to-speech functionality.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Check if the selected engine is available
    if args.engine == "pyttsx3" and not PYTTSX3_AVAILABLE:
        print("Error: pyttsx3 is not installed. Install it with 'pip install pyttsx3'.")
        sys.exit(1)
    elif args.engine == "gtts" and not GTTS_AVAILABLE:
        print("Error: gTTS and pygame are not installed. Install them with 'pip install gtts pygame'.")
        sys.exit(1)

    # Create a TextToSpeechOutputLayer instance
    try:
        tts_layer = TextToSpeechOutputLayer(
            engine=args.engine,
            voice_id=args.voice,
            rate=args.rate,
            volume=args.volume,
            language=args.language,
            print_text=True
        )
    except Exception as e:
        print(f"Error creating TextToSpeechOutputLayer: {e}")
        sys.exit(1)

    # Test messages
    test_messages = [
        "Hello! This is a test of the text-to-speech functionality.",
        "The Always-On AI Assistant can now speak to you.",
        "You can configure different voices, speech rates, and volumes."
    ]

    # Output the test messages
    print("\nTesting text-to-speech with the following settings:")
    print(f"  Engine: {args.engine}")
    if args.engine == "pyttsx3":
        print(f"  Voice ID: {args.voice or 'default'}")
        print(f"  Rate: {args.rate}")
        print(f"  Volume: {args.volume}")
    else:
        print(f"  Language: {args.language}")
    print("\nSpeaking test messages...\n")

    for i, message in enumerate(test_messages, 1):
        print(f"Message {i}:")
        tts_layer.output(message)

        # Add a pause between messages
        if i < len(test_messages):
            time.sleep(1)

    print("\nText-to-speech test completed.")


if __name__ == "__main__":
    main()