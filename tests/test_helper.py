#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Helper Module for the Always-On AI Assistant.

This module provides helper functions for testing the assistant,
particularly for text-to-speech functionality and LLM integration.
"""

import sys
import os
import time
import re
from typing import Dict, Any, Optional, Tuple, Callable
from dotenv import load_dotenv


def setup_paths() -> Dict[str, str]:
    """
    Set up the necessary paths for importing modules.

    This function adds the parent directory and servers directory to sys.path
    to allow importing the layers package and query_helper module.

    Returns:
        Dict[str, str]: A dictionary containing the paths.
    """
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the parent directory (always-on-ai-assistant)
    parent_dir = os.path.dirname(current_dir)

    # Get the servers directory
    servers_dir = os.path.abspath(os.path.join(parent_dir, '..', 'servers'))

    # Add the parent directory to sys.path to import layers and modules
    sys.path.append(parent_dir)

    # Add the servers directory to sys.path to import query_common
    sys.path.append(servers_dir)

    # Load environment variables from .env.test
    env_file = os.path.join(current_dir, '.env.test')
    if os.path.exists(env_file):
        print(f"Loading environment variables from {env_file}")
        load_dotenv(env_file)
    else:
        print(f"Warning: Environment file {env_file} not found")

    return {
        "current_dir": current_dir,
        "parent_dir": parent_dir,
        "servers_dir": servers_dir
    }


def print_debug_info(paths: Dict[str, str]) -> None:
    """
    Print debug information about paths and Python path.

    Args:
        paths (Dict[str, str]): A dictionary containing the paths.
    """
    print("=" * 80)
    print("DEBUG: Script paths")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {paths['current_dir']}")
    print(f"Parent directory: {paths['parent_dir']}")
    print(f"Servers directory: {paths['servers_dir']}")
    print(f"Python path: {sys.path}")
    print("=" * 80)


def import_tts_modules() -> Tuple[Any, bool, bool]:
    """
    Import the text-to-speech modules with error handling.

    Returns:
        Tuple[Any, bool, bool]: A tuple containing:
            - The TextToSpeechOutputLayer class
            - Whether pyttsx3 is available
            - Whether gTTS is available

    Raises:
        ImportError: If the output layer module cannot be imported.
    """
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
        return TextToSpeechOutputLayer, PYTTSX3_AVAILABLE, GTTS_AVAILABLE
    except ImportError as e:
        print(f"✗ Error importing output layer: {e}")
        print("Make sure you have installed the required dependencies.")
        print("Run: pip install -r requirements.txt")
        raise


def import_query_helper() -> Callable:
    """
    Import the query_helper module with error handling.

    Returns:
        Callable: The query_model function.
    """
    try:
        print("Importing query_helper module...")
        from modules.query_helper import query_model
        print(f"✓ query_helper module imported successfully")
        return query_model
    except ImportError as e:
        print(f"✗ Error importing query_helper: {e}")
        print("Falling back to mock implementation.")

        # Mock implementation of query_model
        def mock_query_model(model_type, model_name, prompt, base_url=None, **kwargs):
            """Mock implementation of query_model for when the actual module is not available."""
            print(f"MOCK: Would query {model_type} model {model_name} at {base_url}")
            print(f"MOCK: Prompt: {prompt}")
            return "This is a mock response. The actual implementation would query the LLM."

        return mock_query_model


def safe_xml_string(text: str) -> str:
    """
    Convert special XML-like tags to their proper form.

    This function replaces '[|' with '<' and '|]' with '>' to avoid
    triggering tool use parsers when writing prompts that include XML-like tags.

    Args:
        text (str): The text containing safe XML-like tags.

    Returns:
        str: The text with proper XML tags.
    """
    return text.replace("[|", "<").replace("|]", ">")


def get_prompt_template() -> str:
    """
    Get the prompt template from environment variables or use a default.

    Returns:
        str: The prompt template.
    """
    # Get the prompt template from environment variables or use a default
    return os.environ.get(
        "ASSISTANT_PROMPT_TEMPLATE",
        "You are a helpful, friendly AI assistant. Answer the user's question concisely and accurately.\n\nUser: {question}"
    )


def format_prompt(question: str) -> str:
    """
    Format the prompt for the LLM.

    Args:
        question (str): The user's question.

    Returns:
        str: The formatted prompt.
    """
    # Get the prompt template
    prompt_template = get_prompt_template()

    # Format the prompt
    formatted_prompt = prompt_template.format(question=question)

    # Apply safe XML string conversion
    return safe_xml_string(formatted_prompt)


def create_tts_layer(args: Any) -> Any:
    """
    Create a TextToSpeechOutputLayer instance.

    Args:
        args (Any): The command-line arguments.

    Returns:
        Any: The TextToSpeechOutputLayer instance.
    """
    TextToSpeechOutputLayer, PYTTSX3_AVAILABLE, GTTS_AVAILABLE = import_tts_modules()

    # Get the engine name from the appropriate argument
    # Check for both tts_engine (voice_assistant_demo.py) and engine (live_tts_demo.py)
    engine = getattr(args, 'tts_engine', getattr(args, 'engine', 'pyttsx3'))

    # Check if the selected engine is available
    if engine == "pyttsx3" and not PYTTSX3_AVAILABLE:
        print("Error: pyttsx3 is not installed. Install it with 'pip install pyttsx3'. To use gTTS instead, run with '--tts-engine gtts'")
        sys.exit(1)
    elif engine == "gtts" and not GTTS_AVAILABLE:
        print("Error: gTTS and pygame are not installed. Install them with 'pip install gtts pygame'. To use pyttsx3 instead, run with '--tts-engine pyttsx3'")
        sys.exit(1)

    # Create a TextToSpeechOutputLayer instance
    try:
        tts_layer = TextToSpeechOutputLayer(
            engine=engine,
            voice_id=args.tts_voice if hasattr(args, 'tts_voice') else args.voice,
            rate=args.tts_rate if hasattr(args, 'tts_rate') else args.rate,
            volume=args.tts_volume if hasattr(args, 'tts_volume') else args.volume,
            language=args.language,
            print_text=True
        )
        return tts_layer
    except Exception as e:
        print(f"Error creating TextToSpeechOutputLayer: {e}")
        sys.exit(1)


def get_env_defaults() -> Dict[str, Any]:
    """
    Get default values from environment variables.

    Returns:
        Dict[str, Any]: A dictionary containing default values.
    """
    return {
        "tts_engine": os.environ.get("TTS_ENGINE", "pyttsx3"),
        "tts_voice_id": os.environ.get("TTS_VOICE_ID", None),
        "tts_rate": int(os.environ.get("TTS_RATE", "150")),
        "tts_volume": float(os.environ.get("TTS_VOLUME", "1.0")),
        "tts_language": os.environ.get("TTS_LANGUAGE", "en"),
        "llm_model_type": os.environ.get("LLM_MODEL_TYPE", "ollama"),
        "llm_model_name": os.environ.get("LLM_MODEL_NAME", "mistral:instruct"),
        "llm_base_url": os.environ.get("LLM_BASE_URL", "http://localhost:11434"),
    }
