#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice Assistant Demo for the Always-On AI Assistant.

This script demonstrates a complete voice assistant experience by combining
speech-to-text and text-to-speech capabilities. It listens for speech,
converts it to text, sends it to an LLM for processing, and speaks the response.

Usage:
    python voice_assistant_demo.py [--stt-engine ENGINE] [--tts-engine ENGINE]

Example:
    python voice_assistant_demo.py
    python voice_assistant_demo.py --stt-engine vosk --tts-engine gtts
    python voice_assistant_demo.py --wake-word "hey assistant"
"""

import sys
import os
import argparse
import time
import signal
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

    parser = argparse.ArgumentParser(description="Voice Assistant Demo for the Always-On AI Assistant")

    # Speech-to-Text options
    stt_group = parser.add_argument_group("Speech-to-Text Options")
    stt_group.add_argument(
        "--stt-engine",
        choices=["speechrecognition", "vosk"],
        default="speechrecognition" if SPEECHRECOGNITION_AVAILABLE else "vosk",
        help="The speech recognition engine to use"
    )
    stt_group.add_argument(
        "--language",
        default="en-US",
        help="The language code to use for speech recognition"
    )
    stt_group.add_argument(
        "--vosk-model-path",
        default=None,
        help="Path to the Vosk model directory (required for Vosk)"
    )
    stt_group.add_argument(
        "--wake-word",
        default=None,
        help="Optional wake word to activate the assistant (e.g., 'hey assistant')"
    )

    # Text-to-Speech options
    tts_group = parser.add_argument_group("Text-to-Speech Options")
    tts_group.add_argument(
        "--tts-engine",
        choices=["pyttsx3", "gtts"],
        default=defaults["tts_engine"],
        help=f"The TTS engine to use (default: {defaults['tts_engine']})"
    )
    tts_group.add_argument(
        "--tts-voice",
        default=defaults["tts_voice_id"],
        help="The voice ID to use for TTS (for pyttsx3 only)"
    )
    tts_group.add_argument(
        "--tts-rate",
        type=int,
        default=defaults["tts_rate"],
        help=f"The speech rate (words per minute, for pyttsx3 only, default: {defaults['tts_rate']})"
    )
    tts_group.add_argument(
        "--tts-volume",
        type=float,
        default=defaults["tts_volume"],
        help=f"The speech volume (0.0 to 1.0, for pyttsx3 only, default: {defaults['tts_volume']})"
    )

    # LLM options
    llm_group = parser.add_argument_group("LLM Options")
    llm_group.add_argument(
        "--model",
        default=defaults["llm_model_name"],
        help=f"The LLM model to use (default: {defaults['llm_model_name']})"
    )
    llm_group.add_argument(
        "--model-type",
        default=defaults["llm_model_type"],
        choices=["ollama", "openai", "anthropic", "lmstudio"],
        help=f"The type of LLM to use (default: {defaults['llm_model_type']})"
    )
    llm_group.add_argument(
        "--base-url",
        default=defaults["llm_base_url"],
        help=f"The base URL for the LLM API (default: {defaults['llm_base_url']})"
    )

    # Other options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()


def main():
    """
    Main function to run the voice assistant demo.
    """
    # Set up paths and load environment variables
    paths = setup_paths()

    # Parse command-line arguments
    args = parse_arguments()

    # Print debug information
    print_debug_info(paths)

    # Import the query_helper module
    query_model = import_query_helper()

    # Import the TTS modules
    TextToSpeechOutputLayer, PYTTSX3_AVAILABLE, GTTS_AVAILABLE = import_tts_modules()

    # Create a TextToSpeechOutputLayer instance
    tts_layer = create_tts_layer(args)

    print("\n" + "=" * 80)
    print("VOICE ASSISTANT DEMO")
    print("=" * 80)
    print(f"STT Engine: {args.stt_engine}")
    print(f"TTS Engine: {args.tts_engine}")
    print(f"LLM Model: {args.model_type}/{args.model}")
    print(f"Base URL: {args.base_url}")
    if args.wake_word:
        print(f"Wake Word: '{args.wake_word}'")
    print("=" * 80 + "\n")

    # Welcome message
    welcome_message = "Welcome to the Always-On AI Assistant. I'm listening for your commands."
    print(welcome_message)
    tts_layer.output(welcome_message)

    # Flag to track if the assistant is active (for wake word mode)
    assistant_active = not args.wake_word

    # Define the callback function for processing recognized text
    def process_text(text):
        nonlocal assistant_active

        if not text:
            return

        # Check for wake word if specified
        if args.wake_word and not assistant_active:
            if args.wake_word.lower() in text.lower():
                assistant_active = True
                activation_message = "Yes, I'm listening."
                print("\nWake word detected! Assistant activated.")
                print(activation_message)
                tts_layer.output(activation_message)
                return
            else:
                # Wake word not detected, continue listening
                return

        # Check for exit commands
        if text.lower() in ["exit", "quit", "goodbye", "bye"]:
            print("\nExit command detected. Shutting down...")
            goodbye_message = "Goodbye! Have a great day."
            print(goodbye_message)
            tts_layer.output(goodbye_message)
            # Signal the main thread to exit
            os.kill(os.getpid(), signal.SIGINT)
            return

        # If wake word mode is active, check for sleep command
        if args.wake_word and assistant_active:
            if text.lower() in ["sleep", "stop listening", "go to sleep"]:
                assistant_active = False
                sleep_message = "Going to sleep. Say the wake word to activate me again."
                print("\nSleep command detected. Assistant deactivated.")
                print(sleep_message)
                tts_layer.output(sleep_message)
                return

        print("\nProcessing: " + text)

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
            tts_layer.output(error_message)

    try:
        # Create a speech input layer
        speech_layer = SpeechInputLayer(
            engine=args.stt_engine,
            language=args.language,
            vosk_model_path=args.vosk_model_path,
            print_text=True
        )

        # Listen continuously
        if args.wake_word:
            print(f"\nListening for wake word '{args.wake_word}'... (Press Ctrl+C to stop)")
        else:
            print("\nListening for commands... (Press Ctrl+C to stop)")

        speech_layer.listen_continuously(callback=process_text)

    except ImportError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        if 'speech_layer' in locals():
            speech_layer.close()

        print("\nVoice Assistant demo completed.")


if __name__ == "__main__":
    main()