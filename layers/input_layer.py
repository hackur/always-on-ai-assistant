#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input Layer for the Always-On AI Assistant.

This module defines the input layer interface and implementations for the assistant.
The input layer is responsible for collecting user input from various sources and
normalizing it to a standard format that can be processed by the assistant.

Classes:
    InputLayer: Abstract base class for all input layers.
    TextInputLayer: Implementation that gets text input from the command line.

Functions:
    create_input_layer: Factory function to create the appropriate input layer.

Typical usage example:
    config = load_config()
    input_layer = create_input_layer(config)
    user_input = input_layer.get_input()
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class InputLayer(ABC):
    """
    Abstract base class for all input layers.

    This class defines the interface that all input layer implementations must follow.
    Input layers are responsible for collecting user input from various sources
    (e.g., command line, speech-to-text, GUI) and normalizing it to a standard format.

    Attributes:
        None
    """

    @abstractmethod
    def get_input(self) -> Dict[str, Any]:
        """
        Get input from the user.

        This method should be implemented by subclasses to collect input from the user
        using the appropriate mechanism (e.g., command line, speech-to-text, GUI).

        Returns:
            Dict[str, Any]: A dictionary containing the user input.
                The dictionary should have at least a 'text' key with the user's text input.
                Additional keys may be added for other types of input or metadata.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        pass


class TextInputLayer(InputLayer):
    """
    Input layer that gets text input from the command line.

    This implementation uses the built-in input() function to get text input
    from the user via the command line.

    Attributes:
        prompt (str): The prompt to display to the user when requesting input.
    """

    def __init__(self, prompt: str = "You: "):
        """
        Initialize the TextInputLayer.

        Args:
            prompt (str, optional): The prompt to display to the user when requesting input.
                Defaults to "You: ".
        """
        self.prompt = prompt

    def get_input(self) -> Dict[str, Any]:
        """
        Get text input from the command line.

        This method displays a prompt to the user and waits for them to enter text.
        The entered text is returned as a dictionary with a 'text' key.

        Returns:
            Dict[str, Any]: A dictionary containing the user input.
                The dictionary has a 'text' key with the user's text input.

        Example:
            >>> layer = TextInputLayer()
            >>> user_input = layer.get_input()  # User enters "Hello"
            >>> user_input
            {'text': 'Hello'}
        """
        user_input = input(self.prompt)
        return {"text": user_input}


# TODO: Implement SpeechToTextInputLayer for voice input using a library like vosk or whisper.cpp


def create_input_layer(config: Dict[str, Any]) -> InputLayer:
    """
    Create an input layer based on the configuration.

    This factory function creates and returns an instance of the appropriate
    input layer based on the configuration dictionary.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
            Should contain an 'INPUT_LAYER' key that specifies the type of input layer to create.
            Additional keys may be required depending on the input layer type.

    Returns:
        InputLayer: An instance of the appropriate input layer.

    Raises:
        ValueError: If the input layer type specified in the configuration is not supported.

    Example:
        >>> config = {"INPUT_LAYER": "local_text"}
        >>> input_layer = create_input_layer(config)
        >>> isinstance(input_layer, TextInputLayer)
        True
    """
    input_layer_type = config.get("INPUT_LAYER", "local_text")

    if input_layer_type == "local_text":
        # Get custom prompt if specified
        prompt = config.get("INPUT_PROMPT", "You: ")
        return TextInputLayer(prompt=prompt)
    else:
        raise ValueError(f"Unsupported input layer type: {input_layer_type}")