#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test module for the Speech Input Layer.

This module contains tests for the SpeechInputLayer class.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import the layers package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the SpeechInputLayer class
try:
    from layers.speech_input_layer import (
        SpeechInputLayer,
        SPEECHRECOGNITION_AVAILABLE,
        VOSK_AVAILABLE,
        PYAUDIO_AVAILABLE
    )
except ImportError as e:
    print(f"Error importing speech_input_layer: {e}")
    print("Make sure the speech_input_layer.py file exists in the layers directory.")
    sys.exit(1)


class TestSpeechInputLayer(unittest.TestCase):
    """Test cases for the SpeechInputLayer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.callback_called = False
        self.callback_text = None

    def callback(self, text):
        """Callback function for testing."""
        self.callback_called = True
        self.callback_text = text

    @unittest.skipIf(not SPEECHRECOGNITION_AVAILABLE, "SpeechRecognition not available")
    def test_speechrecognition_init(self):
        """Test initialization with SpeechRecognition."""
        with patch('speech_recognition.Recognizer') as mock_recognizer:
            with patch('speech_recognition.Microphone') as mock_microphone:
                # Mock the list_microphone_names method
                mock_microphone.list_microphone_names.return_value = ["mic1", "mic2"]

                # Create a SpeechInputLayer instance
                layer = SpeechInputLayer(
                    engine="speechrecognition",
                    print_text=False
                )

                # Check that the recognizer was created
                self.assertIsNotNone(layer.recognizer)

                # Check that the microphones were listed
                self.assertEqual(layer.microphones, ["mic1", "mic2"])

    @unittest.skipIf(not VOSK_AVAILABLE, "Vosk not available")
    def test_vosk_init(self):
        """Test initialization with Vosk."""
        with patch('vosk.Model') as mock_model:
            with patch('pyaudio.PyAudio') as mock_pyaudio:
                # Mock the get_device_count and get_device_info_by_index methods
                mock_pyaudio.return_value.get_device_count.return_value = 2
                mock_pyaudio.return_value.get_device_info_by_index.side_effect = [
                    {"maxInputChannels": 1, "name": "mic1"},
                    {"maxInputChannels": 0, "name": "not_a_mic"}
                ]

                # Create a SpeechInputLayer instance with a mock model path
                with patch('os.path.exists') as mock_exists:
                    mock_exists.return_value = True

                    layer = SpeechInputLayer(
                        engine="vosk",
                        vosk_model_path="/mock/path",
                        print_text=False
                    )

                # Check that the model was created
                self.assertIsNotNone(layer.model)

                # Check that the microphones were listed
                self.assertEqual(layer.microphones, ["mic1"])

    @unittest.skipIf(not SPEECHRECOGNITION_AVAILABLE, "SpeechRecognition not available")
    def test_speechrecognition_listen(self):
        """Test listening with SpeechRecognition."""
        with patch('speech_recognition.Recognizer') as mock_recognizer_class:
            with patch('speech_recognition.Microphone') as mock_microphone:
                # Mock the list_microphone_names method
                mock_microphone.list_microphone_names.return_value = ["mic1", "mic2"]

                # Mock the recognizer
                mock_recognizer = MagicMock()
                mock_recognizer_class.return_value = mock_recognizer

                # Mock the listen method
                mock_audio = MagicMock()
                mock_recognizer.listen.return_value = mock_audio

                # Mock the recognize_google method
                mock_recognizer.recognize_google.return_value = "test speech"

                # Create a SpeechInputLayer instance
                layer = SpeechInputLayer(
                    engine="speechrecognition",
                    print_text=False
                )

                # Listen for speech
                text = layer.listen()

                # Check that the correct text was returned
                self.assertEqual(text, "test speech")

                # Check that the recognizer methods were called
                mock_recognizer.adjust_for_ambient_noise.assert_called_once()
                mock_recognizer.listen.assert_called_once()
                mock_recognizer.recognize_google.assert_called_once_with(mock_audio, language="en-US")

    @unittest.skipIf(not VOSK_AVAILABLE, "Vosk not available")
    def test_vosk_listen(self):
        """Test listening with Vosk."""
        with patch('vosk.Model') as mock_model:
            with patch('vosk.KaldiRecognizer') as mock_recognizer_class:
                with patch('pyaudio.PyAudio') as mock_pyaudio:
                    # Mock the PyAudio methods
                    mock_stream = MagicMock()
                    mock_pyaudio.return_value.open.return_value = mock_stream
                    mock_pyaudio.return_value.get_device_count.return_value = 1
                    mock_pyaudio.return_value.get_device_info_by_index.return_value = {
                        "maxInputChannels": 1,
                        "name": "mic1"
                    }

                    # Mock the KaldiRecognizer
                    mock_recognizer = MagicMock()
                    mock_recognizer_class.return_value = mock_recognizer

                    # Mock the AcceptWaveform method
                    mock_recognizer.AcceptWaveform.return_value = True

                    # Mock the Result method
                    mock_recognizer.Result.return_value = '{"text": "test speech"}'

                    # Create a SpeechInputLayer instance
                    with patch('os.path.exists') as mock_exists:
                        mock_exists.return_value = True

                        layer = SpeechInputLayer(
                            engine="vosk",
                            vosk_model_path="/mock/path",
                            print_text=False
                        )

                    # Mock the stream.read method
                    mock_stream.read.return_value = b"test data"

                    # Listen for speech
                    text = layer.listen()

                    # Check that the correct text was returned
                    self.assertEqual(text, "test speech")

                    # Check that the stream methods were called
                    mock_stream.start_stream.assert_called_once()
                    mock_stream.read.assert_called_once()
                    mock_stream.stop_stream.assert_called_once()
                    mock_stream.close.assert_called_once()

                    # Check that the recognizer methods were called
                    mock_recognizer.AcceptWaveform.assert_called_once_with(b"test data")
                    mock_recognizer.Result.assert_called_once()

    @unittest.skipIf(not SPEECHRECOGNITION_AVAILABLE, "SpeechRecognition not available")
    def test_speechrecognition_callback(self):
        """Test callback with SpeechRecognition."""
        with patch('speech_recognition.Recognizer') as mock_recognizer_class:
            with patch('speech_recognition.Microphone') as mock_microphone:
                # Mock the list_microphone_names method
                mock_microphone.list_microphone_names.return_value = ["mic1", "mic2"]

                # Mock the recognizer
                mock_recognizer = MagicMock()
                mock_recognizer_class.return_value = mock_recognizer

                # Mock the listen method
                mock_audio = MagicMock()
                mock_recognizer.listen.return_value = mock_audio

                # Mock the recognize_google method
                mock_recognizer.recognize_google.return_value = "test speech"

                # Create a SpeechInputLayer instance with a callback
                layer = SpeechInputLayer(
                    engine="speechrecognition",
                    callback=self.callback,
                    print_text=False
                )

                # Listen for speech
                text = layer.listen()

                # Check that the callback was called with the correct text
                self.assertTrue(self.callback_called)
                self.assertEqual(self.callback_text, "test speech")

    @unittest.skipIf(not VOSK_AVAILABLE, "Vosk not available")
    def test_vosk_callback(self):
        """Test callback with Vosk."""
        with patch('vosk.Model') as mock_model:
            with patch('vosk.KaldiRecognizer') as mock_recognizer_class:
                with patch('pyaudio.PyAudio') as mock_pyaudio:
                    # Mock the PyAudio methods
                    mock_stream = MagicMock()
                    mock_pyaudio.return_value.open.return_value = mock_stream
                    mock_pyaudio.return_value.get_device_count.return_value = 1
                    mock_pyaudio.return_value.get_device_info_by_index.return_value = {
                        "maxInputChannels": 1,
                        "name": "mic1"
                    }

                    # Mock the KaldiRecognizer
                    mock_recognizer = MagicMock()
                    mock_recognizer_class.return_value = mock_recognizer

                    # Mock the AcceptWaveform method
                    mock_recognizer.AcceptWaveform.return_value = True

                    # Mock the Result method
                    mock_recognizer.Result.return_value = '{"text": "test speech"}'

                    # Create a SpeechInputLayer instance with a callback
                    with patch('os.path.exists') as mock_exists:
                        mock_exists.return_value = True

                        layer = SpeechInputLayer(
                            engine="vosk",
                            vosk_model_path="/mock/path",
                            callback=self.callback,
                            print_text=False
                        )

                    # Mock the stream.read method
                    mock_stream.read.return_value = b"test data"

                    # Listen for speech
                    text = layer.listen()

                    # Check that the callback was called with the correct text
                    self.assertTrue(self.callback_called)
                    self.assertEqual(self.callback_text, "test speech")


if __name__ == "__main__":
    unittest.main()