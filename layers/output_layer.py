#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output Layer for the Always-On AI Assistant.

This module defines the output layer interface and implementations for the assistant.
The output layer is responsible for presenting the assistant's responses to the user
through various output methods (e.g., console text, speech synthesis, GUI).

Classes:
    OutputLayer: Abstract base class for all output layers.
    TextOutputLayer: Implementation that prints text to the console.
    ColoredTextOutputLayer: Implementation that prints colored text to the console.
    TextToSpeechOutputLayer: Implementation that converts text to speech.

Functions:
    create_output_layer: Factory function to create the appropriate output layer.

Typical usage example:
    config = load_config()
    output_layer = create_output_layer(config)
    output_layer.output("Hello, world!")
"""

import os
import sys
import time
import platform
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union

# Import text-to-speech libraries conditionally to handle missing dependencies gracefully
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from gtts import gTTS
    import tempfile
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Import Kokoro TTS dependencies
try:
    import torch
    import torchaudio
    from transformers import AutoProcessor, AutoTokenizer, AutoModel
    import numpy as np
    import soundfile as sf
    import sounddevice as sd
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False


class OutputLayer(ABC):
    """
    Abstract base class for all output layers.

    This class defines the interface that all output layer implementations must follow.
    Output layers are responsible for presenting the assistant's responses to the user
    through various output methods (e.g., console text, speech synthesis, GUI).

    Attributes:
        None
    """

    @abstractmethod
    def output(self, text: str) -> None:
        """
        Output the assistant's response to the user.

        This method should be implemented by subclasses to present the assistant's
        response to the user using the appropriate mechanism (e.g., console text,
        speech synthesis, GUI).

        Args:
            text (str): The text to output.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        pass


class TextOutputLayer(OutputLayer):
    """
    Output layer that prints text to the console.

    This implementation uses the built-in print() function to output text
    to the console.

    Attributes:
        prefix (str): The prefix to prepend to the output text.
    """

    def __init__(self, prefix: str = "Assistant: "):
        """
        Initialize the TextOutputLayer.

        Args:
            prefix (str, optional): The prefix to prepend to the output text.
                Defaults to "Assistant: ".
        """
        self.prefix = prefix

    def output(self, text: str) -> None:
        """
        Print the text to the console.

        This method prints the text to the console with a prefix to indicate
        that it's from the assistant.

        Args:
            text (str): The text to output.

        Example:
            >>> layer = TextOutputLayer()
            >>> layer.output("Hello, world!")
            Assistant: Hello, world!
        """
        print(f"{self.prefix}{text}")


class ColoredTextOutputLayer(OutputLayer):
    """
    Output layer that prints colored text to the console.

    This implementation uses ANSI escape codes to output colored text
    to the console.

    Attributes:
        color (str): The color to use for the output.
        prefix (str): The prefix to prepend to the output text.
        color_codes (Dict[str, str]): A dictionary mapping color names to ANSI color codes.
    """

    def __init__(self, color: str = "blue", prefix: str = "Assistant: "):
        """
        Initialize the colored text output layer.

        Args:
            color (str, optional): The color to use for the output.
                Options: 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan'.
                Defaults to "blue".
            prefix (str, optional): The prefix to prepend to the output text.
                Defaults to "Assistant: ".
        """
        self.color = color
        self.prefix = prefix
        self.color_codes = {
            "red": "\033[91m",
            "green": "\033[92m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "reset": "\033[0m"
        }

    def output(self, text: str) -> None:
        """
        Print colored text to the console.

        This method prints the text to the console with a prefix and in the specified color.

        Args:
            text (str): The text to output.

        Note:
            This method uses ANSI escape codes for coloring, which may not work
            in all terminal environments.

        Example:
            >>> layer = ColoredTextOutputLayer(color="green")
            >>> layer.output("Hello, world!")
            # Outputs "Assistant: Hello, world!" in green text
        """
        color_code = self.color_codes.get(self.color, self.color_codes["blue"])
        reset_code = self.color_codes["reset"]
        print(f"{color_code}{self.prefix}{text}{reset_code}")


class TextToSpeechOutputLayer(OutputLayer):
    """
    Output layer that converts text to speech.

    This implementation uses text-to-speech libraries to convert the assistant's
    response to speech. It supports multiple TTS engines:
    - pyttsx3: Offline TTS engine that works across platforms
    - gTTS: Google Text-to-Speech (requires internet connection)
    - kokoro: Local Kokoro-82M model from HuggingFace (high quality, 82MB model)

    Attributes:
        engine (str): The TTS engine to use ('pyttsx3', 'gtts', or 'kokoro').
        voice_id (Optional[str]): The voice ID to use (engine-specific).
        rate (int): The speech rate (words per minute, for pyttsx3).
        volume (float): The speech volume (0.0 to 1.0, for pyttsx3).
        language (str): The language code (for gTTS).
        print_text (bool): Whether to also print the text to the console.
        prefix (str): The prefix to prepend to the output text if printed.
        model_id (str): Model ID for Kokoro TTS (defaults to "hexgrad/Kokoro-82M").
        sample_rate (int): Sample rate for audio output (for Kokoro TTS).
    """

    def __init__(self,
                 engine: str = "pyttsx3",
                 voice_id: Optional[str] = None,
                 rate: int = 150,
                 volume: float = 1.0,
                 language: str = "en",
                 print_text: bool = True,
                 prefix: str = "Assistant: ",
                 model_id: str = "hexgrad/Kokoro-82M",
                 sample_rate: int = 24000):
        """
        Initialize the text-to-speech output layer.

        Args:
            engine (str, optional): The TTS engine to use ('pyttsx3', 'gtts', or 'kokoro').
                Defaults to "pyttsx3".
            voice_id (Optional[str], optional): The voice ID to use (engine-specific).
                For pyttsx3, this is the ID of the voice to use.
                For gTTS, this is not used.
                For kokoro, this is not used as the model has a fixed voice.
                Defaults to None, which uses the default voice.
            rate (int, optional): The speech rate (words per minute, for pyttsx3).
                Defaults to 150.
            volume (float, optional): The speech volume (0.0 to 1.0, for pyttsx3).
                Defaults to 1.0.
            language (str, optional): The language code (for gTTS).
                Defaults to "en".
            print_text (bool, optional): Whether to also print the text to the console.
                Defaults to True.
            prefix (str, optional): The prefix to prepend to the output text if printed.
                Defaults to "Assistant: ".
            model_id (str, optional): The Hugging Face model ID for Kokoro TTS.
                Defaults to "hexgrad/Kokoro-82M".
            sample_rate (int, optional): Sample rate for audio output (for Kokoro TTS).
                Defaults to 24000.

        Raises:
            ImportError: If the required TTS library is not available.
        """
        self.engine = engine
        self.voice_id = voice_id
        self.rate = rate
        self.volume = volume
        self.language = language
        self.print_text = print_text
        self.prefix = prefix
        self.model_id = model_id
        self.sample_rate = sample_rate
        self.kokoro_model = None
        self.kokoro_processor = None

        # Initialize the TTS engine
        if engine == "pyttsx3":
            if not PYTTSX3_AVAILABLE:
                raise ImportError(
                    "pyttsx3 is not installed. Install it with 'uv pip install pyttsx3'."
                )
            self.tts_engine = None  # Initialize to None

        elif engine == "gtts":
            if not GTTS_AVAILABLE:
                raise ImportError(
                    "gTTS and pygame are not installed. Install them with 'uv pip install gtts pygame'."
                )
            # Initialize pygame mixer for audio playback
            pygame.mixer.init()

        elif engine == "kokoro":
            if not KOKORO_AVAILABLE:
                raise ImportError(
                    "Kokoro TTS dependencies are not installed. Install them with 'uv pip install torch torchaudio transformers numpy soundfile sounddevice'."
                )
            print(f"Initializing Kokoro TTS model from {self.model_id}...")
            try:
                # Let's try a direct approach using HuggingFace endpoints instead
                import requests
                import io
                import tempfile

                self.kokoro_api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
                self.kokoro_headers = {"Authorization": f"Bearer {os.environ.get('HF_TOKEN', 'hf_dummy')}"}
                self.kokoro_model = None  # We'll use API endpoint instead
                self.kokoro_processor = None

                # Test connection
                response = requests.get(
                    "https://huggingface.co/hexgrad/Kokoro-82M",
                    timeout=5
                )
                if response.status_code == 200:
                    print("Kokoro TTS model found on HuggingFace")
                else:
                    print(f"Warning: Couldn't verify Kokoro TTS model: {response.status_code}")

                # Check for HF_TOKEN in a case-insensitive way
                token_found = False
                for key in os.environ:
                    if key.upper() == "HF_TOKEN":
                        token_found = True
                        # Set it to the standard name if it's with a different case
                        if key != "HF_TOKEN":
                            os.environ["HF_TOKEN"] = os.environ[key]

                if not token_found:
                    print("Warning: HF_TOKEN not set in environment. API access may be rate-limited.")
                    print("For better performance, set the HF_TOKEN environment variable with your HuggingFace token.")

            except Exception as e:
                print(f"Warning: Issue setting up Kokoro TTS: {e}")
                print("Kokoro TTS will use gTTS as a fallback")

        else:
            raise ValueError(f"Unsupported TTS engine: {engine}")

    def output(self, text: str) -> None:
        """
        Convert text to speech and optionally print it to the console.

        This method converts the text to speech using the configured TTS engine
        and plays it through the system's audio output.

        Args:
            text (str): The text to output.

        Raises:
            RuntimeError: If there is an error generating or playing the speech.

        Example:
            >>> layer = TextToSpeechOutputLayer()
            >>> layer.output("Hello, world!")
            # Speaks "Hello, world!" and prints "Assistant: Hello, world!"
        """
        # Print the text if configured to do so
        if self.print_text:
            print(f"{self.prefix}{text}")

        try:
            # Generate and play speech using the configured engine
            if self.engine == "pyttsx3":
                if self.tts_engine is None:
                    self.tts_engine = pyttsx3.init()
                    # Configure the engine
                    if self.voice_id is not None:
                        self.tts_engine.setProperty('voice', self.voice_id)
                    self.tts_engine.setProperty('rate', self.rate)
                    self.tts_engine.setProperty('volume', self.volume)

                    # List available voices (for debugging)
                    voices = self.tts_engine.getProperty('voices')
                    print(f"Available voices ({len(voices)}):")
                    for i, voice in enumerate(voices):
                        print(f"  {i}: {voice.id} - {voice.name} ({voice.languages})")

                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                finally:
                    self.tts_engine.endLoop()


            elif self.engine == "gtts":
                # Create a temporary file for the audio
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_path = temp_file.name

                try:
                    # Generate the speech
                    tts = gTTS(text=text, lang=self.language, slow=False)
                    tts.save(temp_path)

                    # Play the speech
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()

                    # Wait for the speech to finish
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)

                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

            elif self.engine == "kokoro":
                try:
                    import requests
                    import io
                    import tempfile

                    # Split long text into chunks for better TTS processing
                    import re
                    max_length = 250  # Maximum recommended chunk size
                    text_chunks = []

                    if len(text) > max_length:
                        # Split text at natural breaks
                        sentences = re.split(r'(?<=[.!?,:;])\s+', text)
                        current_chunk = ""

                        for sentence in sentences:
                            if len(current_chunk) + len(sentence) < max_length:
                                current_chunk += " " + sentence if current_chunk else sentence
                            else:
                                text_chunks.append(current_chunk)
                                current_chunk = sentence

                        if current_chunk:
                            text_chunks.append(current_chunk)
                    else:
                        text_chunks = [text]

                    # Process each chunk
                    for chunk in text_chunks:
                        print(f"Processing text chunk ({len(chunk)} chars)...")

                        try:
                            # First try using HuggingFace Inference API
                            api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
                            token = None

                            # Check for HF_TOKEN in env vars (case insensitive)
                            for key in os.environ:
                                if key.upper() == "HF_TOKEN":
                                    token = os.environ[key]
                                    break

                            headers = {"Authorization": f"Bearer {token}" if token else "Bearer hf_dummy"}

                            print(f"Making request to HuggingFace API with token: {'Available' if token else 'Not available'}")

                            # Request TTS generation with error handling and backoff
                            try:
                                response = requests.post(
                                    api_url,
                                    headers=headers,
                                    json={"inputs": chunk},
                                    timeout=15  # Increase timeout for slow connections
                                )

                                print(f"API Response status: {response.status_code}")

                                # Log the full response to a file for debugging
                                try:
                                    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
                                    os.makedirs(log_dir, exist_ok=True)

                                    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
                                    log_file = os.path.join(log_dir, f"kokoro_api_response_{timestamp}.log")

                                    with open(log_file, 'w') as f:
                                        f.write(f"Status Code: {response.status_code}\n")
                                        f.write(f"Headers: {dict(response.headers)}\n")

                                        # Try to log the response content - could be binary or text
                                        try:
                                            f.write(f"Content (text): {response.text[:2000]}...\n")
                                        except:
                                            f.write(f"Content: Binary data of length {len(response.content)} bytes\n")

                                        # Log environment variables (excluding sensitive values)
                                        f.write("\nEnvironment Variables:\n")
                                        for key in os.environ:
                                            if key.upper() == "HF_TOKEN":
                                                f.write(f"{key}: [REDACTED]\n")
                                            else:
                                                f.write(f"{key}: {os.environ[key]}\n")

                                    print(f"API response logged to {log_file}")
                                except Exception as log_e:
                                    print(f"Error logging API response: {log_e}")

                                if response.status_code == 200:
                                    content_type = response.headers.get('content-type', '')
                                    if 'audio' in content_type.lower() or len(response.content) > 100:
                                        # Looks like valid audio data
                                        print(f"Received audio data: {len(response.content)} bytes")

                                        # Create a temporary file to save the audio
                                        file_suffix = '.wav'
                                        with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as temp_file:
                                            temp_path = temp_file.name
                                            temp_file.write(response.content)

                                        print(f"Saved to {temp_path}")

                                        # Play audio with multiple methods for robustness
                                        try:
                                            # Try soundfile/sounddevice first
                                            print("Attempting playback with sounddevice...")
                                            data, samplerate = sf.read(temp_path)
                                            sd.play(data, samplerate)
                                            sd.wait()  # Wait for playback to finish
                                            print("✓ Audio playback complete with sounddevice")
                                        except Exception as e1:
                                            print(f"sounddevice playback failed: {e1}")

                                            # Fall back to system player
                                            try:
                                                print("Attempting playback with system player...")
                                                if platform.system() == "Darwin":  # macOS
                                                    os.system(f"afplay {temp_path}")
                                                    print("✓ Audio playback complete with afplay")
                                                elif platform.system() == "Windows":
                                                    os.system(f"start {temp_path}")
                                                    print("✓ Audio playback complete with start")
                                                elif platform.system() == "Linux":
                                                    os.system(f"aplay {temp_path}")
                                                    print("✓ Audio playback complete with aplay")
                                            except Exception as e2:
                                                print(f"System player failed: {e2}")
                                        finally:
                                            # Clean up the temporary file
                                            if os.path.exists(temp_path):
                                                os.unlink(temp_path)
                                    else:
                                        # Not audio data
                                        print(f"Error: Response is not audio data. Content type: {content_type}")
                                        self._use_gtts_fallback(chunk)
                                else:
                                    # If API fails, fall back to gTTS
                                    print(f"Kokoro API error: {response.status_code}, falling back to gTTS")
                                    if response.status_code == 401:
                                        print("Authentication error. Make sure HF_TOKEN is set correctly.")
                                    else:
                                        print(f"Error content: {response.text[:200]}")
                                    self._use_gtts_fallback(chunk)
                            except requests.exceptions.RequestException as e:
                                print(f"Request failed: {e}")
                                self._use_gtts_fallback(chunk)
                            else:
                                # If API fails, fall back to gTTS
                                print(f"Kokoro API error: {response.status_code}, falling back to gTTS")
                                self._use_gtts_fallback(chunk)

                        except Exception as e:
                            print(f"Error with Kokoro TTS: {e}")
                            self._use_gtts_fallback(chunk)

                except Exception as e:
                    print(f"Error generating speech with Kokoro TTS: {e}")
                    # Use gTTS as a fallback
                    self._use_gtts_fallback(text)

        except Exception as e:
            print(f"Error generating or playing speech: {e}")
            # TODO: Implement proper error handling and logging

    def _use_gtts_fallback(self, text: str) -> None:
        """
        Use gTTS as a fallback TTS option when Kokoro TTS fails.

        Args:
            text (str): The text to convert to speech.
        """
        if not GTTS_AVAILABLE:
            print("Cannot use gTTS fallback: gTTS not available")
            return

        print("Using gTTS as fallback...")

        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Generate the speech
            tts = gTTS(text=text, lang=self.language, slow=False)
            tts.save(temp_path)

            # Make sure pygame is initialized
            if not pygame.get_init():
                pygame.init()

            # Make sure the mixer is initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            # Play the speech
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()

            # Wait for the speech to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            print("✓ Fallback audio playback complete")

        except Exception as e:
            print(f"Error in gTTS fallback: {e}")
            print("Attempting to play with system default audio player...")
            try:
                # Try to play with system default player as last resort
                if platform.system() == "Darwin":  # macOS
                    os.system(f"afplay {temp_path}")
                elif platform.system() == "Windows":
                    os.system(f"start {temp_path}")
                elif platform.system() == "Linux":
                    os.system(f"aplay {temp_path}")
            except Exception as e2:
                print(f"Also failed with system player: {e2}")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

def create_output_layer(config: Dict[str, Any]) -> OutputLayer:
    """
    Create an output layer based on the configuration.

    This factory function creates and returns an instance of the appropriate
    output layer based on the configuration dictionary.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
            Should contain an 'OUTPUT_LAYER' key that specifies the type of output layer to create.
            Additional keys may be required depending on the output layer type.

    Returns:
        OutputLayer: An instance of the appropriate output layer.

    Raises:
        ValueError: If the output layer type specified in the configuration is not supported.

    Example:
        >>> config = {"OUTPUT_LAYER": "local_text"}
        >>> output_layer = create_output_layer(config)
        >>> isinstance(output_layer, TextOutputLayer)
        True
    """
    output_layer_type = config.get("OUTPUT_LAYER", "local_text")

    if output_layer_type == "local_text":
        prefix = config.get("OUTPUT_PREFIX", "Assistant: ")
        return TextOutputLayer(prefix=prefix)

    elif output_layer_type == "colored_text":
        color = config.get("OUTPUT_COLOR", "blue")
        prefix = config.get("OUTPUT_PREFIX", "Assistant: ")
        return ColoredTextOutputLayer(color=color, prefix=prefix)

    elif output_layer_type == "text_to_speech":
        engine = config.get("TTS_ENGINE", "pyttsx3")
        voice_id = config.get("TTS_VOICE_ID")
        rate = int(config.get("TTS_RATE", "150"))
        volume = float(config.get("TTS_VOLUME", "1.0"))
        language = config.get("TTS_LANGUAGE", "en")
        print_text = config.get("TTS_PRINT_TEXT", "true").lower() == "true"
        prefix = config.get("OUTPUT_PREFIX", "Assistant: ")
        model_id = config.get("TTS_MODEL_ID", "hexgrad/Kokoro-82M")
        sample_rate = int(config.get("TTS_SAMPLE_RATE", "24000"))

        try:
            return TextToSpeechOutputLayer(
                engine=engine,
                voice_id=voice_id,
                rate=rate,
                volume=volume,
                language=language,
                print_text=print_text,
                prefix=prefix,
                model_id=model_id,
                sample_rate=sample_rate
            )
        except ImportError as e:
            print(f"Warning: {e} Falling back to text output.")
            return TextOutputLayer(prefix=prefix)

    else:
        raise ValueError(f"Unsupported output layer type: {output_layer_type}")