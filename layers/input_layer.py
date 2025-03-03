"""
Input Layer for the Always-On AI Assistant.
This module handles user input from various sources.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class InputLayer(ABC):
    """Base class for all input layers."""

    @abstractmethod
    def get_input(self) -> Dict[str, Any]:
        """
        Get input from the user.

        Returns:
            Dict[str, Any]: A dictionary containing the user input.
                The dictionary should have at least a 'text' key.
        """
        pass


class TextInputLayer(InputLayer):
    """Input layer that gets text input from the command line."""

    def get_input(self) -> Dict[str, Any]:
        """
        Get text input from the command line.

        Returns:
            Dict[str, Any]: A dictionary containing the user input.
        """
        user_input = input("You: ")
        return {"text": user_input}


# Factory function to create the appropriate input layer based on configuration
def create_input_layer(config: Dict[str, Any]) -> InputLayer:
    """
    Create an input layer based on the configuration.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
            Should contain an 'INPUT_LAYER' key.

    Returns:
        InputLayer: An instance of the appropriate input layer.

    Raises:
        ValueError: If the input layer type is not supported.
    """
    input_layer_type = config.get("INPUT_LAYER", "local_text")

    if input_layer_type == "local_text":
        return TextInputLayer()
    else:
        raise ValueError(f"Unsupported input layer type: {input_layer_type}")