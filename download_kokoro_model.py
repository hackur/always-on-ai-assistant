#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download the Kokoro TTS model for local offline use.

This script downloads the Kokoro-82M TTS model from HuggingFace
and sets it up for local inference, eliminating the need for API calls.

Usage:
    python download_kokoro_model.py [--output-dir models/kokoro]
"""

import os
import sys
import argparse
import logging
import torch
from huggingface_hub import hf_hub_download, snapshot_download
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("kokoro_downloader")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Download Kokoro TTS model for offline use")
    parser.add_argument("--model-id", type=str, default="hexgrad/Kokoro-82M",
                        help="HuggingFace model ID to download")
    parser.add_argument("--output-dir", type=str, default="models/kokoro",
                        help="Directory to save the model files")
    parser.add_argument("--force", action="store_true",
                        help="Force re-download even if files exist")
    args = parser.parse_args()

    # Get the absolute path for the output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, args.output_dir)

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading Kokoro TTS model: {args.model_id}")
    logger.info(f"Output directory: {output_dir}")

    try:
        # Check if we need to download
        if os.path.exists(os.path.join(output_dir, "config.json")) and not args.force:
            logger.info("Model files already exist. Use --force to re-download.")
            logger.info("Testing local model...")
            test_loaded_model(output_dir)
            return

        # Download the model
        logger.info(f"Downloading model files from HuggingFace...")
        snapshot_download(
            repo_id=args.model_id,
            local_dir=output_dir,
            local_dir_use_symlinks=False,
            revision="main"
        )

        # Test the downloaded model
        logger.info("Download complete. Testing model...")
        test_loaded_model(output_dir)

        # Create a flag file to indicate successful download
        with open(os.path.join(output_dir, ".download_complete"), "w") as f:
            f.write("Model downloaded successfully")

        logger.info(f"✓ Model successfully downloaded and tested!")
        logger.info(f"Model location: {output_dir}")

    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        sys.exit(1)

def test_loaded_model(model_dir):
    """Test that the model can be loaded correctly"""

    try:
        # Load the model
        logger.info("Loading model for testing...")
        processor = AutoProcessor.from_pretrained(model_dir)
        model = AutoModelForSpeechSeq2Seq.from_pretrained(model_dir)

        # Log model information
        device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Model device: {device}")

        logger.info(f"Model size: {sum(p.numel() for p in model.parameters()) / 1_000_000:.2f}M parameters")
        logger.info("✓ Model loaded successfully!")

    except Exception as e:
        logger.error(f"Error testing model: {e}")
        raise

if __name__ == "__main__":
    main()