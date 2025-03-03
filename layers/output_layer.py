"""
Output Layer for the Always-On AI Assistant.
This module handles presenting the assistant's responses to the user.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class OutputLayer(ABC):
    """Base class for all output layers."""

    @abstractmethod
    def output(self, text: str) -> None:
        """
        Output the assistant's response to the user.

        Args:
            text (str): The text to output.
        """
        pass


class TextOutputLayer(OutputLayer):
    """Output layer that prints text to the console."""

    def output(self, text: str) -> None:
        """
        Print the text to the console.

        Args:
            text (str): The text to output.
        """
        print(f"Assistant: {text}")


class ColoredTextOutputLayer(OutputLayer):
    """Output layer that prints colored text to the console."""

    def __init__(self, color: str = "blue"):
        """
        Initialize the colored text output layer.

        Args:
            color (str): The color to use for the output.
                Options: 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan'.
        """
        self.color = color
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

        Args:
            text (str): The text to output.
        """
        color_code = self.color_codes.get(self.color, self.color_codes["blue"])
        reset_code = self.color_codes["reset"]
        print(f"{color_code}Assistant: {text}{reset_code}")


# Factory function to create the appropriate output layer based on configuration
def create_output_layer(config: Dict[str, Any]) -> OutputLayer:
    """
    Create an output layer based on the configuration.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
            Should contain an 'OUTPUT_LAYER' key.

    Returns:
        OutputLayer: An instance of the appropriate output layer.

    Raises:
        ValueError: If the output layer type is not supported.
    """
    output_layer_type = config.get("OUTPUT_LAYER", "local_text")

    if output_layer_type == "local_text":
        return TextOutputLayer()
    elif output_layer_type == "colored_text":
        color = config.get("OUTPUT_COLOR", "blue")
        return ColoredTextOutputLayer(color)
    else:
        raise ValueError(f"Unsupported output layer type: {output_layer_type}")