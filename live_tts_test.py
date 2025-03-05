#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Text-to-Speech Test for the Always-On AI Assistant.

This script performs a live test of the text-to-speech functionality with a real LLM.
It asks the user for a question, sends it to an LLM, and speaks the response.

The script includes verbose debugging output to help diagnose any issues.

Usage:
    python live_tts_test.py [--engine ENGINE] [--voice VOICE_ID] [--model MODEL]

Example:
    python live_tts_test.py
    python live_tts_test.py --engine gtts
    python live_tts_test.py --model llama3:8b
"""

import sys
import os
import argparse
import time
import json
from typing import Dict, Any, Optional

# Add the parent directory to sys.path to import layers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Add the servers directory to sys.path to import query_helper
SERVERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'servers'))
sys.path.append(SERVERS_DIR)

# Print debug information about paths
print("=" * 80)
print("DEBUG: Script paths")
print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
print(f"Servers directory: {SERVERS_DIR}")
print(f"Python path: {sys.path}")
print("=" * 80)

# Import required modules with error handling
try:
    print("Importing output layer module...")
    from layers.output_layer import (
        TextToSpeechOutputLayer,
        PYTTSX3_AVAILABLE,
        GTTS_AVAILABLE
    )
    print(f"✓ Output layer module imported successfully")
    print(f"  - pyttsx3 available: {PYTTSX3_AVAILABLE}")
    print(f"  - gTTS available: {GTTS_AVAILABLE}")
except ImportError as e:
    print(f"✗ Error importing output layer: {e}")
    print("Make sure you have installed the required dependencies.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    print("Importing query_helper module...")
    from query_helper import query_model
    print(f"✓ query_helper module imported successfully")
except ImportError as e:
    print(f"✗ Error importing query_helper: {e}")
    print("Falling back to mock implementation.")

    # Mock implementation of query_model
    def query_model(model_type, model_name, prompt, base_url=None, **kwargs):
        """Mock implementation of query_model for when the actual module is not available."""
        print(f"MOCK: Would query {model_type} model {model_name} at {base_url}")
        print(f"MOCK: Prompt: {prompt}")
        return "This is a mock response. The actual implementation would query the LLM."


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Live test of the text-to-speech functionality with a real LLM")
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
    parser.add_argument(
        "--model",
        default="mistralai/Mistral-7B-Instruct-v0.1",
        help="The LLM model to use (default: mistralai/Mistral-7B-Instruct-v0.1)"
    )
    parser.add_argument(
        "--model-type",
        default="ollama",
        choices=["ollama", "openai", "anthropic", "lmstudio"],
        help="The type of LLM to use (default: ollama)"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:11434",
        help="The base URL for the LLM API (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()


def format_prompt(question: str) -> str:
    """
    Format the prompt for the LLM.

    Args:
        question (str): The user's question.

    Returns:
        str: The formatted prompt.
    """
    return f"""You are a helpful, friendly AI assistant. Answer the user's question concisely and accurately.

