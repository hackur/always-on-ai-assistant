"""
Unit tests for the output layer.
"""

import sys
import os
import unittest
from unittest.mock import patch
from io import StringIO

# Add the parent directory to sys.path to import layers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layers.output_layer import TextOutputLayer, ColoredTextOutputLayer, create_output_layer


class TestOutputLayer(unittest.TestCase):
    """Test cases for the output layer."""

    def test_text_output_layer(self):
        """Test the TextOutputLayer class."""
        # Create a TextOutputLayer instance
        layer = TextOutputLayer()

        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            # Output a message
            layer.output("Hello, world!")

            # Check that the message was printed to stdout
            self.assertEqual(fake_stdout.getvalue(), "Assistant: Hello, world!\n")

    def test_colored_text_output_layer(self):
        """Test the ColoredTextOutputLayer class."""
        # Create a ColoredTextOutputLayer instance with default color (blue)
        layer = ColoredTextOutputLayer()

        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            # Output a message
            layer.output("Hello, world!")

            # Check that the message was printed to stdout with color codes
            # The exact output depends on the color codes, but we can check that it contains the message
            self.assertIn("Hello, world!", fake_stdout.getvalue())
            self.assertIn("Assistant:", fake_stdout.getvalue())

            # Check that it contains color codes
            self.assertIn("\033[", fake_stdout.getvalue())

    def test_colored_text_output_layer_custom_color(self):
        """Test the ColoredTextOutputLayer class with a custom color."""
        # Create a ColoredTextOutputLayer instance with a custom color (red)
        layer = ColoredTextOutputLayer(color="red")

        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            # Output a message
            layer.output("Hello, world!")

            # Check that the message was printed to stdout with color codes
            # The exact output depends on the color codes, but we can check that it contains the message
            self.assertIn("Hello, world!", fake_stdout.getvalue())
            self.assertIn("Assistant:", fake_stdout.getvalue())

            # Check that it contains color codes
            self.assertIn("\033[", fake_stdout.getvalue())

    def test_create_output_layer_default(self):
        """Test the create_output_layer function with default configuration."""
        # Create an output layer with an empty configuration
        layer = create_output_layer({})

        # Check that the layer is a TextOutputLayer instance
        self.assertIsInstance(layer, TextOutputLayer)

    def test_create_output_layer_text(self):
        """Test the create_output_layer function with text configuration."""
        # Create an output layer with a text configuration
        layer = create_output_layer({"OUTPUT_LAYER": "local_text"})

        # Check that the layer is a TextOutputLayer instance
        self.assertIsInstance(layer, TextOutputLayer)

    def test_create_output_layer_colored_text(self):
        """Test the create_output_layer function with colored text configuration."""
        # Create an output layer with a colored text configuration
        layer = create_output_layer({
            "OUTPUT_LAYER": "colored_text",
            "OUTPUT_COLOR": "green"
        })

        # Check that the layer is a ColoredTextOutputLayer instance
        self.assertIsInstance(layer, ColoredTextOutputLayer)
        self.assertEqual(layer.color, "green")

    def test_create_output_layer_invalid(self):
        """Test the create_output_layer function with an invalid configuration."""
        # Try to create an output layer with an invalid configuration
        with self.assertRaises(ValueError):
            create_output_layer({"OUTPUT_LAYER": "invalid_type"})


if __name__ == "__main__":
    unittest.main()