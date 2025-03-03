#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Kokoro TTS integration.

This script tests the Kokoro TTS implementation by:
1. Initializing the TextToSpeechOutputLayer with the Kokoro engine
2. Generating speech from sample text
3. Providing detailed logs about the API connection and audio playback

Usage:
    python test_kokoro_tts.py [--text "Your test text here"]
"""

import os
import sys
import argparse
import logging
from tests.test_helper import setup_paths

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("kokoro_test")

def main():
    # Set up paths
    paths = setup_paths()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test Kokoro TTS implementation")
    parser.add_argument("--text", type=str, default="Hello, I am speaking using the Kokoro TTS system. This is a high-quality voice model.",
                        help="Text to convert to speech")
    parser.add_argument("--hf-token", type=str, default=None,
                        help="HuggingFace token to use for API access (will be saved to env var)")
    args = parser.parse_args()

    # Set HF_TOKEN environment variable if provided
    if args.hf_token:
        os.environ["HF_TOKEN"] = args.hf_token
        logger.info(f"Set HF_TOKEN environment variable from command line")

    # Print debug info about environment
    print("=" * 80)
    print("ENVIRONMENT VARIABLES:")
    print(f"HF_TOKEN present: {'Yes' if any(key.upper() == 'HF_TOKEN' for key in os.environ) else 'No'}")

    # Import TTS modules
    try:
        from layers.output_layer import (
            TextToSpeechOutputLayer,
            PYTTSX3_AVAILABLE,
            GTTS_AVAILABLE,
            KOKORO_AVAILABLE
        )
        print(f"TTS modules imported successfully")
        print(f"  - pyttsx3 available: {PYTTSX3_AVAILABLE}")
        print(f"  - gTTS available: {GTTS_AVAILABLE}")
        print(f"  - Kokoro TTS available: {KOKORO_AVAILABLE}")

        if not KOKORO_AVAILABLE:
            print("Error: Kokoro TTS dependencies are not available. Please install them:")
            print("uv pip install torch torchaudio transformers numpy soundfile sounddevice requests")
            sys.exit(1)

    except ImportError as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)

    # Initialize the TTS layer
    print("\nInitializing Kokoro TTS layer...")
    try:
        tts_layer = TextToSpeechOutputLayer(
            engine="kokoro",
            print_text=True,
            prefix="Kokoro TTS: "
        )
        print("✓ TTS layer initialized successfully")
    except Exception as e:
        print(f"Error initializing TTS layer: {e}")
        sys.exit(1)

    # Test text-to-speech
    print("\nTesting text-to-speech...")
    print(f"Test text: \"{args.text}\"")

    # Generate speech
    try:
        tts_layer.output(args.text)
        print("\n✓ Text-to-speech test completed")
    except Exception as e:
        print(f"\nError during text-to-speech: {e}")
        sys.exit(1)

    print("\nCheck the logs directory for detailed API response logs")

if __name__ == "__main__":
    main()