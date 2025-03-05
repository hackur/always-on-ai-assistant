#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Text-to-Speech Demo for the Always-On AI Assistant.

This script performs a live test of the text-to-speech functionality with a real LLM.
It asks the user for a question, sends it to an LLM, and speaks the response.

The script includes verbose debugging output to help diagnose any issues.

Usage:
    python live_tts_demo.py [--engine ENGINE] [--model MODEL]

Example:
    python live_tts_demo.py
    python live_tts_demo.py --engine gtts
    python live_tts_demo.py --model llama3:8b
"""

import sys
import os
import argparse
import time
import json
from typing import Dict, Any, Optional

# Import the test helper module
try:
    from tests.test_helper import (
        setup_paths,
        print_debug_info,
        import_tts_modules,
        import_query_helper,
        format_prompt,
        create_tts_layer,
        safe_xml_string,
        get_env_defaults
    )
except ImportError as e:
    print(f"Error importing test_helper: {e}")
    print("Make sure the test_helper.py file exists in the tests directory.")
    sys.exit(1)


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    # Get default values from environment variables
    defaults = get_env_defaults()

    parser = argparse.ArgumentParser(description="Live test of the text-to-speech functionality with a real LLM")
    parser.add_argument(
        "--engine",
        choices=["pyttsx3", "gtts"],
        default=defaults["tts_engine"],
        help=f"The TTS engine to use (default: {defaults['tts_engine']})"
    )
    parser.add_argument(
        "--voice",
        default=defaults["tts_voice_id"],
        help="The voice ID to use (for pyttsx3 only)"
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=defaults["tts_rate"],
        help=f"The speech rate (words per minute, for pyttsx3 only, default: {defaults['tts_rate']})"
    )
    parser.add_argument(
        "--volume",
        type=float,
        default=defaults["tts_volume"],
        help=f"The speech volume (0.0 to 1.0, for pyttsx3 only, default: {defaults['tts_volume']})"
    )
    parser.add_argument(
        "--language",
        default=defaults["tts_language"],
        help=f"The language code (for gTTS only, default: {defaults['tts_language']})"
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
    Main function to run the live TTS demo.
    """
    # Set up paths and load environment variables
    paths = setup_paths()

    # Parse command-line arguments
    args = parse_arguments()

    # Print debug information
    print_debug_info(paths)

    # Import the query_helper module
    query_model = import_query_helper()

    # Create a TextToSpeechOutputLayer instance
    tts_layer = create_tts_layer(args)

    print("\n" + "=" * 80)
    print("LIVE TEXT-TO-SPEECH DEMO")
    print("=" * 80)
    print(f"TTS Engine: {args.engine}")
    print(f"LLM Model: {args.model_type}/{args.model}")
    print(f"Base URL: {args.base_url}")
    print("=" * 80 + "\n")

    # Welcome message
    welcome_message = "Welcome to the Always-On AI Assistant live demo. I can answer your questions and speak the responses."
    print(welcome_message)
    tts_layer.output(welcome_message)

    # Main interaction loop
    try:
        while True:
            # Get user input
            print("\n" + "-" * 80)
            question = input("Ask a question (or type 'exit' to quit): ")
            print("-" * 80 + "\n")

            # Check if the user wants to exit
            if question.lower() in ["exit", "quit", "bye"]:
                goodbye_message = "Thank you for using the Always-On AI Assistant. Goodbye!"
                print(goodbye_message)
                tts_layer.output(goodbye_message)
                break

            # Format the prompt
            prompt = format_prompt(question)

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
                tts_layer.output(error_message)

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")

    print("\nLive TTS demo completed.")


if __name__ == "__main__":
    main()
