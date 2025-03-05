#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the text-to-speech output layer.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import layers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the pyttsx3 and gtts modules
sys.modules['pyttsx3'] = MagicMock()
sys.modules['gtts'] = MagicMock()
sys.modules['pygame'] = MagicMock()

from layers.output_layer import TextToSpeechOutputLayer, create_output_layer


class TestTextToSpeechOutputLayer(unittest.TestCase):
    """Test cases for the text-to-speech output layer."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the pyttsx3 engine
        self.mock_engine = MagicMock()
        sys.modules['pyttsx3'].init.return_value = self.mock_engine

        # Mock the engine's getProperty method to return a list of voices
        mock_voice = MagicMock()
        mock_voice.id = "mock_voice_id"
        mock_voice.name = "Mock Voice"
        mock_voice.languages = ["en-US"]
        self.mock_engine.getProperty.return_value = [mock_voice]

        # Set PYTTSX3_AVAILABLE and GTTS_AVAILABLE to True for testing
        from layers.output_layer import PYTTSX3_AVAILABLE, GTTS_AVAILABLE
        sys.modules['layers.output_layer'].PYTTSX3_AVAILABLE = True
        sys.modules['layers.output_layer'].GTTS_AVAILABLE = True

    def test_pyttsx3_output_layer(self):
        """Test the TextToSpeechOutputLayer with pyttsx3 engine."""
        # Create a TextToSpeechOutputLayer instance with pyttsx3 engine
        layer = TextToSpeechOutputLayer(engine="pyttsx3", print_text=False)

        # Check that the engine was initialized
        sys.modules['pyttsx3'].init.assert_called_once()

        # Output a message
        with patch('builtins.print') as mock_print:
            layer.output("Hello, world!")

            # Check that the engine's say method was called with the message
            self.mock_engine.say.assert_called_once_with("Hello, world!")

            # Check that the engine's runAndWait method was called
            self.mock_engine.runAndWait.assert_called_once()

            # Check that print was not called (print_text=False)
            mock_print.assert_not_called()

    def test_pyttsx3_output_layer_with_print(self):
        """Test the TextToSpeechOutputLayer with pyttsx3 engine and print_text=True."""
        # Create a TextToSpeechOutputLayer instance with pyttsx3 engine and print_text=True
        layer = TextToSpeechOutputLayer(engine="pyttsx3", print_text=True)

        # Output a message
        with patch('builtins.print') as mock_print:
            layer.output("Hello, world!")

            # Check that print was called with the message
            mock_print.assert_called_once_with("Assistant: Hello, world!")

    def test_gtts_output_layer(self):
        """Test the TextToSpeechOutputLayer with gTTS engine."""
        # Mock the gTTS class and tempfile
        mock_gtts = MagicMock()
        sys.modules['gtts'].gTTS.return_value = mock_gtts

        # Mock tempfile.NamedTemporaryFile
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/mock_temp_file.mp3"
        mock_temp_file.__enter__.return_value = mock_temp_file

        with patch('tempfile.NamedTemporaryFile', return_value=mock_temp_file):
            # Create a TextToSpeechOutputLayer instance with gTTS engine
            layer = TextToSpeechOutputLayer(engine="gtts", print_text=False)

            # Output a message
            with patch('builtins.print') as mock_print:
                layer.output("Hello, world!")

                # Check that gTTS was called with the message
                sys.modules['gtts'].gTTS.assert_called_once_with(
                    text="Hello, world!", lang="en", slow=False
                )

                # Check that the gTTS instance's save method was called
                mock_gtts.save.assert_called_once_with("/tmp/mock_temp_file.mp3")

                # Check that pygame.mixer.music.load was called
                sys.modules['pygame'].mixer.music.load.assert_called_once_with("/tmp/mock_temp_file.mp3")

                # Check that pygame.mixer.music.play was called
                sys.modules['pygame'].mixer.music.play.assert_called_once()

                # Check that print was not called (print_text=False)
                mock_print.assert_not_called()

    def test_create_output_layer_text_to_speech(self):
        """Test the create_output_layer function with text-to-speech configuration."""
        # Create a configuration dictionary for text-to-speech
        config = {
            "OUTPUT_LAYER": "text_to_speech",
            "TTS_ENGINE": "pyttsx3",
            "TTS_RATE": "160",
            "TTS_VOLUME": "0.8",
            "TTS_PRINT_TEXT": "true"
        }

        # Create an output layer
        layer = create_output_layer(config)

        # Check that the layer is a TextToSpeechOutputLayer instance
        self.assertIsInstance(layer, TextToSpeechOutputLayer)

        # Check that the layer has the expected attributes
        self.assertEqual(layer.engine, "pyttsx3")
        self.assertEqual(layer.rate, 160)
        self.assertEqual(layer.volume, 0.8)
        self.assertTrue(layer.print_text)


if __name__ == "__main__":
    unittest.main()