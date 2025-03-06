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

def test_direct_tts():
    """Test TTS using direct API access through specific model endpoints"""
    print("\n====== TESTING DIRECT MODEL ACCESS =======")

    # Find HuggingFace token
    hf_token = None
    for key in os.environ:
        if "HF" in key.upper() or "HUGGINGFACE" in key.upper():
            hf_token = os.environ[key]
            print(f"Using token from {key}")
            break

    if not hf_token:
        print("No HuggingFace token found in environment variables")
        return False

    import requests
    import tempfile
    import soundfile as sf
    import sounddevice as sd
    import time

    # Direct access to OpenAI TTS endpoint as alternative
    # Using the TTS-1 model which is known to work reliably
    try:
        print("Attempting direct TTS generation...")

        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name

        test_text = "Hello, I am speaking using an alternative TTS system. This should work reliably."

        # Try Microsoft's SpeechT5 model specifically for TTS
        api_url = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"

        headers = {"Authorization": f"Bearer {hf_token}"}

        # First get the speaker embeddings
        speaker_url = "https://api-inference.huggingface.co/models/microsoft/speecht5_hifigan"
        speaker_response = requests.post(
            speaker_url,
            headers=headers,
            json={
                "inputs": {
                    "text": "This is a sample sentence to get speaker embeddings."
                }
            }
        )

        print(f"Speaker embeddings response status: {speaker_response.status_code}")

        if speaker_response.status_code != 200:
            # Try another model as backup
            print("Trying backup TTS model: suno/bark-small")

            api_url = "https://api-inference.huggingface.co/models/suno/bark-small"

            # Make request
            response = requests.post(
                api_url,
                headers=headers,
                json={
                    "inputs": test_text
                }
            )
        else:
            # Make request with speaker embeddings
            response = requests.post(
                api_url,
                headers=headers,
                json={
                    "inputs": {
                        "text": test_text,
                        "speaker_embeddings": speaker_response.json()
                    }
                }
            )

        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            # Save the audio data to the file
            with open(temp_path, "wb") as f:
                f.write(response.content)

            # Play the audio
            data, samplerate = sf.read(temp_path)
            sd.play(data, samplerate)
            sd.wait()

            print("✓ Direct TTS test successful!")
            os.unlink(temp_path)
            return True
        else:
            print(f"Error: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")
            return False

    except Exception as e:
        print(f"Error in direct TTS test: {e}")
        return False

def main():
    # Set up paths
    paths = setup_paths()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test Kokoro TTS implementation")
    parser.add_argument("--text", type=str, default="Hello, I am speaking using the Kokoro TTS system. This is a high-quality voice model.",
                        help="Text to convert to speech")
    parser.add_argument("--hf-token", type=str, default=None,
                        help="HuggingFace token to use for API access (will be saved to env var)")
    parser.add_argument("--direct", action="store_true",
                        help="Test direct API access instead of using the TextToSpeechOutputLayer")
    args = parser.parse_args()

    # Set HF_TOKEN environment variable if provided
    if args.hf_token:
        os.environ["HF_TOKEN"] = args.hf_token
        logger.info(f"Set HF_TOKEN environment variable from command line")

    # If direct testing is requested, skip the layer test
    if args.direct:
        test_direct_tts()
        return

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