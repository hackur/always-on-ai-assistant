#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for downloading and installing Vosk speech recognition models.

This script downloads the specified Vosk model, extracts it, and places it
in the correct location for use with the Always-On AI Assistant.

Usage:
    python setup_vosk_model.py [--model MODEL] [--output-dir DIR]

Example:
    python setup_vosk_model.py
    python setup_vosk_model.py --model small
    python setup_vosk_model.py --model large --output-dir ~/vosk-models
"""

import os
import sys
import argparse
import zipfile
import shutil
from urllib.request import urlretrieve
from tqdm import tqdm


# Available models with their URLs and sizes
MODELS = {
    "small": {
        "name": "vosk-model-small-en-us-0.15",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "size": 40,  # Size in MB (approximate)
        "description": "Small model for English (US), good balance of size and accuracy"
    },
    "medium": {
        "name": "vosk-model-en-us-0.22",
        "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        "size": 1800,  # Size in MB (approximate)
        "description": "Large model for English (US), higher accuracy but requires more resources"
    },
    "large": {
        "name": "vosk-model-en-us-0.42-gigaspeech",
        "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip",
        "size": 2300,  # Size in MB (approximate)
        "description": "Very large model for English (US), highest accuracy"
    }
}


class DownloadProgressBar(tqdm):
    """Progress bar for downloads."""

    def update_to(self, b=1, bsize=1, tsize=None):
        """Update the progress bar.

        Args:
            b: Number of blocks transferred so far
            bsize: Size of each block in bytes
            tsize: Total size in bytes
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url, output_path):
    """Download a file with a progress bar.

    Args:
        url: URL to download
        output_path: Path to save the file
    """
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        urlretrieve(url, filename=output_path, reporthook=t.update_to)


def extract_zip(zip_path, extract_dir):
    """Extract a ZIP file with a progress bar.

    Args:
        zip_path: Path to the ZIP file
        extract_dir: Directory to extract to
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Get the total size of all files
        total_size = sum(file.file_size for file in zip_ref.infolist())

        # Create a progress bar
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="Extracting") as pbar:
            for file in zip_ref.infolist():
                zip_ref.extract(file, extract_dir)
                pbar.update(file.file_size)


def setup_model(model_key, output_dir):
    """Download and set up a Vosk model.

    Args:
        model_key: Key of the model to download ("small", "medium", or "large")
        output_dir: Directory to save the model
    """
    if model_key not in MODELS:
        print(f"Error: Unknown model '{model_key}'. Available models: {', '.join(MODELS.keys())}")
        return False

    model = MODELS[model_key]
    model_name = model["name"]
    model_url = model["url"]
    model_size = model["size"]

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Paths for the downloaded ZIP and extracted model
    zip_path = os.path.join(output_dir, f"{model_name}.zip")
    model_dir = os.path.join(output_dir, model_name)

    # Check if the model is already downloaded and extracted
    if os.path.exists(model_dir):
        print(f"Model '{model_name}' is already installed at '{model_dir}'.")
        return True

    # Download the model
    print(f"Downloading {model_name} ({model_size} MB)...")
    print(f"URL: {model_url}")
    print(f"This may take a while depending on your internet connection.")

    try:
        download_file(model_url, zip_path)
    except Exception as e:
        print(f"Error downloading the model: {e}")
        return False

    # Extract the model
    print(f"Extracting {model_name}...")
    try:
        extract_zip(zip_path, output_dir)
    except Exception as e:
        print(f"Error extracting the model: {e}")
        return False

    # Clean up the ZIP file
    print("Cleaning up...")
    os.remove(zip_path)

    print(f"Model '{model_name}' has been successfully installed at '{model_dir}'.")
    return True


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Setup script for Vosk speech recognition models")
    parser.add_argument(
        "--model",
        choices=["small", "medium", "large"],
        default="small",
        help="The model to download (default: small)"
    )
    parser.add_argument(
        "--output-dir",
        default="models",
        help="Directory to save the model (default: models)"
    )
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()

    # Print information about the available models
    print("=" * 80)
    print("VOSK MODEL SETUP")
    print("=" * 80)
    print("Available models:")
    for key, model in MODELS.items():
        print(f"  - {key}: {model['name']} ({model['size']} MB)")
        print(f"    {model['description']}")
    print("=" * 80)

    # Confirm the download
    model_key = args.model
    model = MODELS[model_key]
    output_dir = os.path.abspath(args.output_dir)

    print(f"Selected model: {model_key} ({model['name']})")
    print(f"Output directory: {output_dir}")
    print(f"This will download approximately {model['size']} MB of data.")

    confirm = input("Do you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    # Download and set up the model
    success = setup_model(model_key, output_dir)

    if success:
        # Print instructions for using the model
        model_path = os.path.join(output_dir, model["name"])
        print("\nTo use this model with the voice assistant, run:")
        print(f"  python voice_assistant_demo.py --stt-engine vosk --vosk-model-path {model_path}")
        print("\nOr with the speech-to-text demo:")
        print(f"  python live_stt_demo.py --engine vosk --vosk-model-path {model_path}")
    else:
        print("\nFailed to set up the model. Please try again.")


if __name__ == "__main__":
    main()