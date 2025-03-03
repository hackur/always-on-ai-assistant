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

Functions:
    create_output_layer: Factory function to create the appropriate output layer.

Typical usage example:
    config = load_config()
    output_layer = create_output_layer(config)
    output_layer.output("Hello, world!")
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


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


# TODO: Implement TextToSpeechOutputLayer for voice output using a library like pyttsx3 or gTTS
# TODO: Implement FileOutputLayer for logging responses to a file
# TODO: Implement MultiOutputLayer to support multiple output methods simultaneously


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
    else:
        raise ValueError(f"Unsupported output layer type: {output_layer_type}")