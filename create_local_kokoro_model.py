#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Kokoro TTS model implementation to interface with the Always-On AI Assistant.

This script provides a simple implementation of the Kokoro TTS model running locally.
It creates an inference function that can be called from the assistant.

Usage:
    python create_local_kokoro_model.py --text "Text to synthesize" --output output.wav
"""

import os
import sys
import argparse
import logging
import torch
import torchaudio
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import numpy as np
import soundfile as sf
import sounddevice as sd
from pathlib import Path
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("kokoro_local")

class LocalKokoroTTS:
    """Local implementation of Kokoro TTS model"""

    def __init__(self, model_dir=None, device=None):
        """Initialize the local Kokoro TTS model.

        Args:
            model_dir: Path to model directory (default: models/kokoro)
            device: Device to use for inference (cpu, cuda, mps)
        """
        # Determine model directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if model_dir is None:
            model_dir = os.path.join(script_dir, "models", "kokoro")
        self.model_dir = model_dir

        # Check if model exists
        if not os.path.exists(os.path.join(model_dir, "config.json")):
            raise ValueError(f"Model files not found at {model_dir}. Please run download_kokoro_model.py first.")

        # Choose the best available device
        if device is None:
            if torch.backends.mps.is_available():
                device = "mps"  # Apple Silicon GPU
                logger.info("Using MPS (Apple Silicon GPU)")
            elif torch.cuda.is_available():
                device = "cuda"  # NVIDIA GPU
                logger.info("Using CUDA (NVIDIA GPU)")
            else:
                device = "cpu"  # CPU fallback
                logger.info("Using CPU (no GPU available)")
        self.device = device

        # Load the model and processor
        logger.info(f"Loading Kokoro model from {model_dir}...")
        self.processor = AutoProcessor.from_pretrained(model_dir)
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_dir,
            device_map=device
        )

        # Set model to evaluation mode
        self.model.eval()
        model_size = sum(p.numel() for p in self.model.parameters()) / 1_000_000
        logger.info(f"Model loaded successfully: {model_size:.2f}M parameters")

    def generate_speech(self, text, output_file=None, play_audio=True):
        """Generate speech from text.

        Args:
            text: Text to synthesize
            output_file: Path to save audio file (optional)
            play_audio: Whether to play audio after generation

        Returns:
            Path to output file if saved, None otherwise
        """
        logger.info(f"Generating speech for: '{text[:50]}...' ({len(text)} chars)")

        start_time = time.time()
        try:
            # Process the input text
            inputs = self.processor(text=text, return_tensors="pt").to(self.device)

            # Generate speech
            with torch.no_grad():
                speech = self.model.generate(**inputs, vocoder=None)

            # Convert to audio
            audio_array = speech.cpu().numpy().squeeze()
            sample_rate = 24000  # Known sample rate for Kokoro model

            # Create temporary file if no output specified
            if output_file is None:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    output_file = temp_file.name

            # Save audio to file
            sf.write(output_file, audio_array, sample_rate)
            logger.info(f"Audio saved to {output_file}")

            # Play audio if requested
            if play_audio:
                self.play_audio(output_file)

            duration = time.time() - start_time
            logger.info(f"Speech generated in {duration:.2f} seconds")

            return output_file

        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None

    def play_audio(self, audio_file):
        """Play audio file using the appropriate method."""
        logger.info(f"Playing audio file: {audio_file}")

        try:
            # Try soundfile/sounddevice first
            data, samplerate = sf.read(audio_file)
            sd.play(data, samplerate)
            sd.wait()  # Wait for playback to finish
            logger.info("✓ Audio playback complete with sounddevice")
        except Exception as e1:
            logger.error(f"sounddevice playback failed: {e1}")

            # Fall back to system player
            try:
                logger.info("Attempting playback with system player...")
                if os.name == 'posix':  # macOS/Linux
                    if sys.platform == 'darwin':  # macOS
                        os.system(f"afplay {audio_file}")
                    else:  # Linux
                        os.system(f"aplay {audio_file}")
                else:  # Windows
                    os.system(f"start {audio_file}")
            except Exception as e2:
                logger.error(f"System player failed: {e2}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate speech with local Kokoro TTS model")
    parser.add_argument("--text", type=str, default="Hello, I am a local version of the Kokoro TTS system. This is a high-quality voice model running on your local machine.",
                        help="Text to convert to speech")
    parser.add_argument("--model-dir", type=str, default=None,
                        help="Directory containing the model files")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to save the output audio file")
    parser.add_argument("--device", type=str, default=None, choices=["cpu", "cuda", "mps"],
                        help="Device to use for inference")
    args = parser.parse_args()

    try:
        # Initialize the TTS model
        tts = LocalKokoroTTS(model_dir=args.model_dir, device=args.device)

        # Generate speech
        output_file = tts.generate_speech(args.text, output_file=args.output)

        # Display path to the output file
        if output_file:
            logger.info(f"✓ Speech generation complete. Output saved to: {output_file}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()