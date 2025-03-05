#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Speech-to-Text Demo for the Always-On AI Assistant.

This script performs a live test of the speech recognition functionality.
It listens for speech, converts it to text, and optionally sends it to an LLM
for processing, then speaks the response.

The script includes verbose debugging output to help diagnose any issues.

Usage:
    python live_stt_demo.py [--engine ENGINE] [--continuous]

Example:
    python live_stt_demo.py
    python live_stt_demo.py --engine vosk
    python live_stt_demo.py --continuous
"""

import sys
import os
import argparse
import time
from typing import Dict, Any, Optional, Callable

# Import the test helper module
try:
    from tests.test_helper import (
        setup_paths,
        print_debug_info,
        import_tts_modules,
        import_query_helper,
        format_prompt,
        create_tts_layer,
        get_env_defaults
    )
except ImportError as e:
    print(f"Error importing test_helper: {e}")
    print("Make sure the test_helper.py file exists in the tests directory.")
    sys.exit(1)

# Import the speech input layer
try:
    from layers.speech_input_layer import SpeechInputLayer, VOSK_AVAILABLE, SPEECHRECOGNITION_AVAILABLE
except ImportError as e:
    print(f"Error importing speech_input_layer: {e}")
    print("Make sure the speech_input_layer.py file exists in the layers directory.")
    sys.exit(1)


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    # Get default values from environment variables
    defaults = get_env_defaults()

    parser = argparse.ArgumentParser(description="Live test of the speech recognition functionality")
    parser.add_argument(
        "--engine",
        choices=["speechrecognition", "vosk"],
        default="speechrecognition" if SPEECHRECOGNITION_AVAILABLE else "vosk",
        help="The speech recognition engine to use"
    )
    parser.add_argument(
        "--language",
        default="en-US",
        help="The language code to use for speech recognition"
    )
    parser.add_argument(
        "--vosk-model-path",
        default=None,
        help="Path to the Vosk model directory (required for Vosk)"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Listen continuously for speech"
    )
    parser.add_argument(
        "--with-llm",
        action="store_true",
        help="Process recognized text with an LLM and speak the response"
    )
    parser.add_argument(
        "--tts-engine",
        choices=["pyttsx3", "gtts"],
        default=defaults["tts_engine"],
        help=f"The TTS engine to use (default: {defaults['tts_engine']})"
    )
    parser.add_argument(
        "--tts-voice",
        default=defaults["tts_voice_id"],
        help="The voice ID to use for TTS (for pyttsx3 only)"
    )
    parser.add_argument(
        "--tts-rate",
        type=int,
        default=defaults["tts_rate"],
        help=f"The speech rate (words per minute, for pyttsx3 only, default: {defaults['tts_rate']})"
    )
    parser.add_argument(
        "--tts-volume",
        type=float,
        default=defaults["tts_volume"],
        help=f"The speech volume (0.0 to 1.0, for pyttsx3 only, default: {defaults['tts_volume']})"
    )
    parser.add_argument(
        "--model",
        default=defaults["llm_model_name"],
        help=f"The LLM model to use (default: {defaults['llm_model_name']})"
    )
    parser.add_argument(
        "--model-type",
        default=defaults["llm_model_type"],
        choices=["ollama", "openai", "anthropic", "lmstudio"],
        help=f"The type of LLM to use (default: {defaults['llm_model_type']})"
    )
    parser.add_argument(
        "--base-url",
        default=defaults["llm_base_url"],
        help=f"The base URL for the LLM API (default: {defaults['llm_base_url']})"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()


def main():
    """
    Main function to run the live STT demo.
    """
    # Set up paths and load environment variables
    paths = setup_paths()

    # Parse command-line arguments
    args = parse_arguments()

    # Print debug information
    print_debug_info(paths)

    # Import the query_helper module if needed
    query_model = None
    if args.with_llm:
        query_model = import_query_helper()

    # Create a TextToSpeechOutputLayer instance if needed
    tts_layer = None
    if args.with_llm:
        tts_layer = create_tts_layer(args)

    print("\n" + "=" * 80)
    print("LIVE SPEECH-TO-TEXT DEMO")
    print("=" * 80)
    print(f"STT Engine: {args.engine}")
    if args.with_llm:
        print(f"TTS Engine: {args.tts_engine}")
        print(f"LLM Model: {args.model_type}/{args.model}")
        print(f"Base URL: {args.base_url}")
    print("=" * 80 + "\n")

    # Welcome message
    welcome_message = "Welcome to the Always-On AI Assistant speech recognition demo."
    print(welcome_message)
    if tts_layer:
        tts_layer.output(welcome_message)

    # Define the callback function for processing recognized text
    def process_text(text):
        if not text:
            return

        print("\nRecognized Text:")
        print("-" * 40)
        print(text)
        print("-" * 40)

        if args.with_llm and query_model and tts_layer:
            # Format the prompt
            prompt = format_prompt(text)

            if args.verbose:
                print("DEBUG: Formatted prompt:")
                print("-" * 40)
                print(prompt)
                print("-" * 40 + "\n")

            # Query the LLM
            print("Querying the LLM...")
            start_time = time.time()

            try:
                response = query_model(
                    model_type=args.model_type,
                    model_name=args.model,
                    prompt=prompt,
                    base_url=args.base_url,
                    verbose=args.verbose
                )

                query_time = time.time() - start_time
                print(f"Query completed in {query_time:.2f} seconds.")

                # Print and speak the response
                print("\nAI Response:")
                print("-" * 40)
                print(response)
                print("-" * 40)

                tts_layer.output(response)

            except Exception as e:
                error_message = f"Error querying the LLM: {e}"
                print(error_message)
                if tts_layer:
                    tts_layer.output(error_message)

    try:
        # Create a speech input layer
        speech_layer = SpeechInputLayer(
            engine=args.engine,
            language=args.language,
            vosk_model_path=args.vosk_model_path,
            print_text=True
        )

        if args.continuous:
            # Listen continuously
            print("\nListening continuously for speech... (Press Ctrl+C to stop)")
            speech_layer.listen_continuously(callback=process_text)
        else:
            # Listen for a single utterance
            print("\nListening for speech...")
            text = speech_layer.listen()
            process_text(text)

    except ImportError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        if 'speech_layer' in locals():
            speech_layer.close()

        print("\nLive STT demo completed.")


if __name__ == "__main__":
    main()