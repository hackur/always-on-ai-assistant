"""
Unit tests for the input layer.
"""

import sys
import os
import unittest
from unittest.mock import patch

# Add the parent directory to sys.path to import layers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layers.input_layer import TextInputLayer, create_input_layer


class TestInputLayer(unittest.TestCase):
    """Test cases for the input layer."""

    def test_text_input_layer(self):
        """Test the TextInputLayer class."""
        # Create a TextInputLayer instance
        layer = TextInputLayer()

        # Mock the input function to return a predefined value
        with patch('builtins.input', return_value='Hello, world!'):
            # Get input from the layer
            result = layer.get_input()

            # Check that the result is a dictionary with the expected text
            self.assertIsInstance(result, dict)
            self.assertIn('text', result)
            self.assertEqual(result['text'], 'Hello, world!')

    def test_create_input_layer_default(self):
        """Test the create_input_layer function with default configuration."""
        # Create an input layer with an empty configuration
        layer = create_input_layer({})

        # Check that the layer is a TextInputLayer instance
        self.assertIsInstance(layer, TextInputLayer)

    def test_create_input_layer_text(self):
        """Test the create_input_layer function with text configuration."""
        # Create an input layer with a text configuration
        layer = create_input_layer({'INPUT_LAYER': 'local_text'})

        # Check that the layer is a TextInputLayer instance
        self.assertIsInstance(layer, TextInputLayer)

    def test_create_input_layer_invalid(self):
        """Test the create_input_layer function with an invalid configuration."""
        # Try to create an input layer with an invalid configuration
        with self.assertRaises(ValueError):
            create_input_layer({'INPUT_LAYER': 'invalid_type'})


if __name__ == '__main__':
    unittest.main()