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
    python voice_assistant_demo.py --voice-profile british
    python voice_assistant_demo.py --tts-voice "com.apple.voice.compact.en-US.Samantha"
    python voice_assistant_demo.py --voice-profile british
"""

import sys
import os
import argparse
import time
import signal
import threading
import json
import logging
import datetime
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

# Check for speech recognition engines
VOSK_AVAILABLE = False
SPEECHRECOGNITION_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECHRECOGNITION_AVAILABLE = True
except ImportError:
    pass

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    pass

if not (SPEECHRECOGNITION_AVAILABLE or VOSK_AVAILABLE):
    print("Error: No speech recognition engine available.")
    print("Please install at least one of the following:")
    print("  - SpeechRecognition: uv pip install speechrecognition")
    print("  - Vosk: uv pip install vosk")
    sys.exit(1)

# Import the speech input layer
try:
    from layers.speech_input_layer import SpeechInputLayer
except ImportError as e:
    print(f"Error importing speech_input_layer: {e}")
    print("Make sure the speech_input_layer.py file exists in the layers directory.")
    sys.exit(1)


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Set up logging for the voice assistant.

    Args:
        verbose: Whether to enable verbose logging

    Returns:
        logging.Logger: Configured logger
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Create a timestamped log file
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(logs_dir, f"voice_assistant_{timestamp}.log")

    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create logger
    logger = logging.getLogger("voice_assistant")
    logger.setLevel(log_level)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger


def load_voice_profile(profile_name: str, logger: logging.Logger) -> Dict[str, Any]:
    """
    Load a voice profile from a JSON file.

    Args:
        profile_name: Name of the profile to load (without .json extension)
        logger: Logger instance

    Returns:
        Dict containing the voice profile settings
    """
    # Check if the profile exists in the voices directory
    profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voices', f"{profile_name}.json")

    if not os.path.exists(profile_path):
        logger.warning(f"Voice profile '{profile_name}' not found at {profile_path}")
        logger.info("Using default voice settings instead.")
        return {}

    try:
        with open(profile_path, 'r') as f:
            profile = json.load(f)
            logger.info(f"Loaded voice profile: {profile.get('name', profile_name)}")
            return profile
    except Exception as e:
        logger.error(f"Error loading voice profile: {e}")
        return {}


def list_voice_profiles(logger: logging.Logger):
    """
    List all available voice profiles in the voices directory.

    Args:
        logger: Logger instance
    """
    voices_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voices')

    if not os.path.exists(voices_dir):
        logger.warning("No voice profiles directory found.")
        return

    profiles = [f[:-5] for f in os.listdir(voices_dir) if f.endswith('.json')]

    if not profiles:
        logger.warning("No voice profiles found.")
        return

    print("\nAvailable voice profiles:")
    print("=" * 80)

    for profile_name in sorted(profiles):
        profile_path = os.path.join(voices_dir, f"{profile_name}.json")
        try:
            with open(profile_path, 'r') as f:
                profile = json.load(f)
                name = profile.get('name', profile_name)
                description = profile.get('description', '')
                engine = profile.get('engine', 'pyttsx3')
                voice_id = profile.get('voice_id', 'default')

                print(f"- {profile_name}: {name}")
                if description:
                    print(f"  Description: {description}")
                print(f"  Engine: {engine}, Voice: {voice_id}")
                print()
        except Exception as e:
            print(f"- {profile_name}: Error loading profile - {e}")
            logger.error(f"Error loading profile {profile_name}: {e}")

    print("\nTo use a voice profile, run:")
    print("python voice_assistant_demo.py --voice-profile PROFILE_NAME")
    print("Example: python voice_assistant_demo.py --voice-profile british")


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
        choices=["speechrecognition"] + (["vosk"] if VOSK_AVAILABLE else []),  # Only include 'vosk' if available
        default="speechrecognition" if SPEECHRECOGNITION_AVAILABLE else ("vosk" if VOSK_AVAILABLE else None), # default to speechrecognition, then vosk if available, otherwise None
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
    # Import PYTTSX3_AVAILABLE for default TTS engine selection
    from layers.output_layer import PYTTSX3_AVAILABLE

    tts_group = parser.add_argument_group("Text-to-Speech Options")
    tts_group.add_argument(
        "--tts-engine",
        choices=["pyttsx3", "gtts"],
        default="pyttsx3" if PYTTSX3_AVAILABLE else "gtts",
        help="The TTS engine to use (default: pyttsx3 if available, otherwise gtts)"
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
    tts_group.add_argument(
        "--list-voices",
        action="store_true",
        help="List available voices and exit"
    )
    tts_group.add_argument(
        "--voice-profile",
        help="Use a predefined voice profile from the voices directory"
    )
    tts_group.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available voice profiles and exit"
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


def list_available_voices(logger: logging.Logger):
    """
    List all available voices for the pyttsx3 engine.

    Args:
        logger: Logger instance
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')

        print("\nAvailable voices for pyttsx3:")
        print("=" * 80)

        # Group voices by language
        voice_by_language = {}
        for i, voice in enumerate(voices):
            lang = str(voice.languages[0]) if voice.languages else "unknown"
            if lang not in voice_by_language:
                voice_by_language[lang] = []
            voice_by_language[lang].append((i, voice))

        # Print voices grouped by language
        for lang, voice_list in sorted(voice_by_language.items()):
            print(f"\nLanguage: {lang}")
            print("-" * 40)
            for i, voice in voice_list:
                print(f"  {i}: {voice.id} - {voice.name}")

        print("\nTo use a specific voice, run the assistant with:")
        print("python voice_assistant_demo.py --tts-voice \"VOICE_ID\"")
        print("Replace VOICE_ID with the ID of the voice you want to use.")
        print("Example: python voice_assistant_demo.py --tts-voice \"com.apple.voice.compact.en-US.Samantha\"")

        print("\nFor more information about voice profiles, see:")
        print("voices/VOICES.md")

        # Clean up the engine
        engine.stop()

    except ImportError:
        logger.error("pyttsx3 is not installed. Install it with 'pip install pyttsx3'.")
        print("pyttsx3 is not installed. Install it with 'pip install pyttsx3'.")
    except Exception as e:
        logger.error(f"Error listing voices: {e}")
        print(f"Error listing voices: {e}")


def main():
    """
    Main function to run the voice assistant demo.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Set up logging
    logger = setup_logging(args.verbose)

    # Set up paths and load environment variables
    paths = setup_paths()

    # If --list-voices is specified, list available voices and exit
    if args.list_voices:
        list_available_voices(logger)
        return

    # If --list-profiles is specified, list available voice profiles and exit
    if args.list_profiles:
        list_voice_profiles(logger)
        return

    # If a voice profile is specified, load it and override the command-line arguments
    if args.voice_profile:
        profile = load_voice_profile(args.voice_profile, logger)
        if profile:
            # Override command-line arguments with profile settings
            if 'engine' in profile:
                args.tts_engine = profile['engine']
                logger.info(f"Using voice profile engine: {args.tts_engine}")
            if 'voice_id' in profile:
                args.tts_voice = profile['voice_id']
                logger.info(f"Using voice profile voice ID: {args.tts_voice}")
            if 'rate' in profile:
                args.tts_rate = profile['rate']
                logger.info(f"Using voice profile rate: {args.tts_rate}")
            if 'volume' in profile:
                args.tts_volume = profile['volume']
                logger.info(f"Using voice profile volume: {args.tts_volume}")
            if 'language' in profile and not args.language:
                args.language = profile['language']
                logger.info(f"Using voice profile language: {args.language}")

    # Print debug information
    print_debug_info(paths)

    # Import the query_helper module
    query_model = import_query_helper()
    logger.info("Imported query_helper module")

    # Import the TTS modules
    TextToSpeechOutputLayer, PYTTSX3_AVAILABLE, GTTS_AVAILABLE = import_tts_modules()
    logger.info(f"Imported TTS modules. pyttsx3: {PYTTSX3_AVAILABLE}, gTTS: {GTTS_AVAILABLE}")

    # Create a TextToSpeechOutputLayer instance
    tts_layer = create_tts_layer(args)
    logger.info(f"Created TTS layer with engine: {args.tts_engine}")

    print("\n" + "=" * 80)
    print("VOICE ASSISTANT DEMO")
    print("=" * 80)
    print(f"STT Engine: {args.stt_engine}")
    print(f"TTS Engine: {args.tts_engine}")
    if args.tts_voice:
        print(f"TTS Voice: {args.tts_voice}")
    if args.voice_profile:
        print(f"Voice Profile: {args.voice_profile}")
    print(f"LLM Model: {args.model_type}/{args.model}")
    print(f"Base URL: {args.base_url}")
    if args.wake_word:
        print(f"Wake Word: '{args.wake_word}'")
    print("=" * 80 + "\n")

    logger.info(f"STT Engine: {args.stt_engine}")
    logger.info(f"TTS Engine: {args.tts_engine}")
    if args.tts_voice:
        logger.info(f"TTS Voice: {args.tts_voice}")
    if args.voice_profile:
        logger.info(f"Voice Profile: {args.voice_profile}")
    logger.info(f"LLM Model: {args.model_type}/{args.model}")
    logger.info(f"Base URL: {args.base_url}")
    if args.wake_word:
        logger.info(f"Wake Word: '{args.wake_word}'")

    # Create a speech input layer
    speech_layer = SpeechInputLayer(
        engine=args.stt_engine,
        language=args.language,
        vosk_model_path=args.vosk_model_path,
        print_text=True
    )
    logger.info(f"Created speech input layer with engine: {args.stt_engine}")

    # Flag to track if the assistant is active (for wake word mode)
    assistant_active = not args.wake_word

    # Flag to track if the assistant is speaking
    is_speaking = False

    # Create a lock for thread safety
    lock = threading.Lock()

    # Create a semaphore to ensure only one TTS operation at a time
    tts_semaphore = threading.Semaphore(1)

    # Define a function to handle the assistant's speech
    def speak_response(text):
        nonlocal is_speaking

        # Acquire the TTS semaphore to ensure only one TTS operation at a time
        if not tts_semaphore.acquire(blocking=False):
            logger.warning("TTS already in progress, skipping this response")
            return

        try:
            with lock:
                is_speaking = True
                # Pause speech recognition to prevent the assistant from hearing itself
                speech_layer.pause()
                logger.debug("Paused speech recognition")

            try:
                # Speak the response
                logger.debug(f"Speaking: {text[:50]}...")
                tts_layer.output(text)
                logger.debug("Finished speaking")
            except Exception as e:
                logger.error(f"Error generating or playing speech: {e}")
                print(f"Error generating or playing speech: {e}")
        finally:
            # Always resume listening and release the semaphore, even if there was an error
            with lock:
                is_speaking = False
                # Resume speech recognition
                speech_layer.resume()
                logger.debug("Resumed speech recognition")

            # Release the TTS semaphore
            tts_semaphore.release()

    # Define the callback function for processing recognized text
    def process_text(text):
        nonlocal assistant_active

        if not text:
            return

        # Skip processing if the assistant is currently speaking
        with lock:
            if is_speaking:
                if args.verbose:
                    logger.debug("Ignoring input while speaking...")
                return

        # Check for wake word if specified
        if args.wake_word and not assistant_active:
            if args.wake_word.lower() in text.lower():
                assistant_active = True
                activation_message = "Yes, I'm listening."
                print("\nWake word detected! Assistant activated.")
                print(activation_message)
                logger.info("Wake word detected, assistant activated")

                # Speak the activation message
                threading.Thread(target=speak_response, args=(activation_message,)).start()
                return
            else:
                # Wake word not detected, continue listening
                return

        # Check for exit commands
        if text.lower() in ["exit", "quit", "goodbye", "bye"]:
            print("\nExit command detected. Shutting down...")
            goodbye_message = "Goodbye! Have a great day."
            print(goodbye_message)
            logger.info("Exit command detected, shutting down")

            # Speak the goodbye message
            speak_response(goodbye_message)

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
                logger.info("Sleep command detected, assistant deactivated")

                # Speak the sleep message
                threading.Thread(target=speak_response, args=(sleep_message,)).start()
                return

        print("\nProcessing: " + text)
        logger.info(f"Processing: {text}")

        # Format the prompt
        prompt = format_prompt(text)
        logger.debug(f"Formatted prompt: {prompt[:50]}...")

        if args.verbose:
            print("DEBUG: Formatted prompt:")
            print("-" * 40)
            print(prompt)
            print("-" * 40 + "\n")

        # Query the LLM
        print("Querying the LLM...")
        logger.info(f"Querying LLM: {args.model_type}/{args.model}")
        start_time = time.time()

        try:
            # Check if the model exists (for Ollama)
            if args.model_type == "ollama":
                try:
                    import requests
                    # Check if the model exists in Ollama
                    response = requests.get(f"{args.base_url}/api/tags")
                    if response.status_code == 200:
                        models = [model["name"] for model in response.json().get("models", [])]
                        if args.model not in models:
                            available_models = ", ".join(models[:5]) + (", ..." if len(models) > 5 else "")
                            error_message = f"Model '{args.model}' not found in Ollama. Available models: {available_models}"
                            print(error_message)
                            logger.error(error_message)
                            threading.Thread(target=speak_response, args=(error_message,)).start()
                            return
                except Exception as e:
                    logger.warning(f"Could not check if model exists: {e}")
                    print(f"Warning: Could not check if model exists: {e}")

            # Query the model
            response = query_model(
                model_type=args.model_type,
                model_name=args.model,
                prompt=prompt,
                base_url=args.base_url,
                verbose=args.verbose
            )

            query_time = time.time() - start_time
            print(f"Query completed in {query_time:.2f} seconds.")
            logger.info(f"Query completed in {query_time:.2f} seconds")

            # Print and speak the response
            print("\nAI Response:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            logger.info(f"AI Response: {response[:100]}...")

            # Check if the response indicates an error
            if "Error:" in response:
                error_message = "I encountered an error while processing your request. Please check if the LLM server is running and the model is available."
                print(error_message)
                logger.error(f"LLM error: {response}")
                threading.Thread(target=speak_response, args=(error_message,)).start()
            else:
                # Speak the response in a separate thread
                threading.Thread(target=speak_response, args=(response,)).start()

        except Exception as e:
            error_message = f"Error querying the LLM: {e}"
            print(error_message)
            logger.error(error_message)

            # Speak the error message
            threading.Thread(target=speak_response, args=(error_message,)).start()

    try:
        # Welcome message
        welcome_message = "Welcome to the Always-On AI Assistant. I'm listening for your commands."
        print(welcome_message)
        logger.info("Starting voice assistant")

        # Speak the welcome message and wait for it to complete
        speak_response(welcome_message)

        # Listen continuously
        if args.wake_word:
            print(f"\nListening for wake word '{args.wake_word}'... (Press Ctrl+C to stop)")
            logger.info(f"Listening for wake word: {args.wake_word}")
        else:
            print("\nListening for commands... (Press Ctrl+C to stop)")
            logger.info("Listening for commands")

        speech_layer.listen_continuously(callback=process_text)

        # Keep the main thread alive
        while True:
            time.sleep(0.1)

    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error: {e}")
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down")
        print("\nInterrupted by user. Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        if 'speech_layer' in locals():
            logger.info("Closing speech layer")
            speech_layer.close()

        logger.info("Voice Assistant demo completed")
        print("\nVoice Assistant demo completed.")


if __name__ == "__main__":
    main()
