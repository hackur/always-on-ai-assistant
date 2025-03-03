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

    Attributes:
        engine (str): The TTS engine to use ('pyttsx3' or 'gtts').
        voice_id (Optional[str]): The voice ID to use (engine-specific).
        rate (int): The speech rate (words per minute, for pyttsx3).
        volume (float): The speech volume (0.0 to 1.0, for pyttsx3).
        language (str): The language code (for gTTS).
        print_text (bool): Whether to also print the text to the console.
        prefix (str): The prefix to prepend to the output text if printed.
    """

    def __init__(self,
                 engine: str = "pyttsx3",
                 voice_id: Optional[str] = None,
                 rate: int = 150,
                 volume: float = 1.0,
                 language: str = "en",
                 print_text: bool = True,
                 prefix: str = "Assistant: "):
        """
        Initialize the text-to-speech output layer.

        Args:
            engine (str, optional): The TTS engine to use ('pyttsx3' or 'gtts').
                Defaults to "pyttsx3".
            voice_id (Optional[str], optional): The voice ID to use (engine-specific).
                For pyttsx3, this is the ID of the voice to use.
                For gTTS, this is not used.
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

        # Initialize the TTS engine
        if engine == "pyttsx3":
            if not PYTTSX3_AVAILABLE:
                raise ImportError(
                    "pyttsx3 is not installed. Install it with 'pip install pyttsx3'."
                )
            self.tts_engine = None  # Initialize to None

        elif engine == "gtts":
            if not GTTS_AVAILABLE:
                raise ImportError(
                    "gTTS and pygame are not installed. Install them with 'pip install gtts pygame'."
                )
            # Initialize pygame mixer for audio playback
            pygame.mixer.init()

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

        except Exception as e:
            print(f"Error generating or playing speech: {e}")
            # TODO: Implement proper error handling and logging


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

        try:
            return TextToSpeechOutputLayer(
                engine=engine,
                voice_id=voice_id,
                rate=rate,
                volume=volume,
                language=language,
                print_text=print_text,
                prefix=prefix
            )
        except ImportError as e:
            print(f"Warning: {e} Falling back to text output.")
            return TextOutputLayer(prefix=prefix)

    else:
        raise ValueError(f"Unsupported output layer type: {output_layer_type}")