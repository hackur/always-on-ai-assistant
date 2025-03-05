#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Speech Input Layer for the Always-On AI Assistant.

This module provides speech recognition capabilities using various engines:
- SpeechRecognition with Google, Sphinx, or other providers
- Vosk for offline speech recognition

Usage:
    from layers.speech_input_layer import SpeechInputLayer

    # Create a speech input layer
    speech_layer = SpeechInputLayer(engine="vosk")

    # Listen for speech and get the recognized text
    text = speech_layer.listen()

    # Process the text with your assistant
    response = process_with_assistant(text)
"""

import os
import json
import time
import logging
import threading
from typing import Optional, Dict, Any, List, Union, Callable

# Check for SpeechRecognition
try:
    import speech_recognition as sr
    SPEECHRECOGNITION_AVAILABLE = True
except ImportError:
    SPEECHRECOGNITION_AVAILABLE = False

# Check for Vosk
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

# Check for PyAudio
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class SpeechInputLayer:
    """Speech input layer for the Always-On AI Assistant."""

    def __init__(
        self,
        engine: str = "speechrecognition",
        language: str = "en-US",
        vosk_model_path: Optional[str] = None,
        energy_threshold: int = 300,
        pause_threshold: float = 0.8,
        dynamic_energy_threshold: bool = True,
        timeout: Optional[float] = None,
        phrase_time_limit: Optional[float] = None,
        callback: Optional[Callable[[str], None]] = None,
        print_text: bool = True,
    ):
        """
        Initialize the speech input layer.

        Args:
            engine: The speech recognition engine to use ("speechrecognition" or "vosk")
            language: The language code to use for speech recognition
            vosk_model_path: Path to the Vosk model directory (required for Vosk)
            energy_threshold: Energy level threshold for detecting speech
            pause_threshold: Seconds of non-speaking audio before a phrase is considered complete
            dynamic_energy_threshold: Whether to dynamically adjust the energy threshold
            timeout: Maximum seconds to wait for speech before giving up
            phrase_time_limit: Maximum seconds for a phrase before stopping
            callback: Function to call with recognized text
            print_text: Whether to print recognized text to the console
        """
        if engine is None:
            raise ImportError("No speech recognition engine available. Please install either 'speechrecognition' or 'vosk'.")

        if engine is None:
            raise ValueError("No speech recognition engine available. At least one of 'speechrecognition' or 'vosk' is required.")

        self.engine = engine.lower()
        self.language = language
        self.vosk_model_path = vosk_model_path
        self.energy_threshold = energy_threshold
        self.pause_threshold = pause_threshold
        self.dynamic_energy_threshold = dynamic_energy_threshold
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        self.callback = callback
        self.print_text = print_text

        # Add flags for pausing and stopping
        self.is_paused = False
        self.is_listening = False
        self.listening_thread = None
        self.stream = None

        # Check if the required dependencies are available
        if self.engine == "speechrecognition" and not SPEECHRECOGNITION_AVAILABLE:
            raise ImportError("SpeechRecognition is not installed. Install it with 'uv pip install speechrecognition'")
        elif self.engine == "vosk" and not VOSK_AVAILABLE:
            raise ImportError("Vosk is not installed. Install it with 'uv pip install vosk'")

        if not PYAUDIO_AVAILABLE:
            raise ImportError("PyAudio is not installed. Install it with 'uv pip install pyaudio'")

        # Initialize the appropriate recognizer
        if self.engine == "speechrecognition":
            self._init_speechrecognition()
        elif self.engine == "vosk":
            self._init_vosk()
        else:
            raise ValueError(f"Unsupported engine: {self.engine}. Use 'speechrecognition' or 'vosk'.")

    def _init_speechrecognition(self):
        """Initialize the SpeechRecognition recognizer."""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.pause_threshold = self.pause_threshold
        self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold

        # Get the list of available microphones
        self.microphones = sr.Microphone.list_microphone_names()
        if self.print_text:
            print(f"Available microphones ({len(self.microphones)}):")
            for i, mic in enumerate(self.microphones):
                print(f"  {i}: {mic}")

    def _init_vosk(self):
        """Initialize the Vosk recognizer."""
        if not self.vosk_model_path:
            # Try to find a default model path
            default_paths = [
                os.path.join(os.path.expanduser("~"), "vosk-model"),
                os.path.join(os.path.expanduser("~"), "vosk-model-small"),
                os.path.join(os.path.expanduser("~"), "vosk-model-en-us-0.22"),
                os.path.join(os.getcwd(), "vosk-model"),
                os.path.join(os.getcwd(), "models", "vosk-model-small-en-us-0.15"),
            ]

            for path in default_paths:
                if os.path.exists(path):
                    self.vosk_model_path = path
                    break

            if not self.vosk_model_path:
                raise ValueError(
                    "No Vosk model path provided and no default model found. "
                    "Please download a model from https://alphacephei.com/vosk/models "
                    "and specify the path with vosk_model_path."
                )

        if self.print_text:
            print(f"Loading Vosk model from {self.vosk_model_path}...")

        self.model = Model(self.vosk_model_path)
        self.p = pyaudio.PyAudio()

        # Get the list of available microphones
        self.microphones = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:
                self.microphones.append(device_info.get('name'))

        if self.print_text:
            print(f"Available microphones ({len(self.microphones)}):")
            for i, mic in enumerate(self.microphones):
                print(f"  {i}: {mic}")

    def listen(self, source=None, mic_index=None) -> str:
        """
        Listen for speech and return the recognized text.

        Args:
            source: Optional audio source (for SpeechRecognition)
            mic_index: Optional microphone index to use

        Returns:
            The recognized text
        """
        if self.engine == "speechrecognition":
            return self._listen_speechrecognition(source, mic_index)
        elif self.engine == "vosk":
            return self._listen_vosk(mic_index)

    def _listen_speechrecognition(self, source=None, mic_index=None) -> str:
        """
        Listen for speech using SpeechRecognition.

        Args:
            source: Optional audio source
            mic_index: Optional microphone index to use

        Returns:
            The recognized text
        """
        if source is None:
            # Use the default microphone or the specified one
            mic_source = sr.Microphone(device_index=mic_index)
            with mic_source as source:
                if self.print_text:
                    print("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source)
                if self.print_text:
                    print("Listening...")
                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=self.timeout,
                        phrase_time_limit=self.phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    if self.print_text:
                        print("Listening timed out. No speech detected.")
                    return ""
        else:
            # Use the provided source
            if self.print_text:
                print("Listening...")
            audio = self.recognizer.listen(
                source,
                timeout=self.timeout,
                phrase_time_limit=self.phrase_time_limit
            )

        # Try to recognize the speech
        try:
            if self.print_text:
                print("Recognizing...")
            text = self.recognizer.recognize_google(audio, language=self.language)
            if self.print_text:
                print(f"You said: {text}")
            if self.callback:
                self.callback(text)
            return text
        except sr.UnknownValueError:
            if self.print_text:
                print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            if self.print_text:
                print(f"Could not request results; {e}")
            return ""

    def _listen_vosk(self, mic_index=None) -> str:
        """
        Listen for speech using Vosk.

        Args:
            mic_index: Optional microphone index to use

        Returns:
            The recognized text
        """
        # Set up the audio stream
        device_index = mic_index if mic_index is not None else None
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000,
            input_device_index=device_index
        )

        # Create a Vosk recognizer
        rec = KaldiRecognizer(self.model, 16000)

        if self.print_text:
            print("Listening...")

        # Start listening
        stream.start_stream()

        try:
            # Listen until we get a result or timeout
            start_time = time.time()
            while True:
                data = stream.read(4000, exception_on_overflow=False)
                if len(data) == 0:
                    break

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if "text" in result and result["text"]:
                        text = result["text"]
                        if self.print_text:
                            print(f"You said: {text}")
                        if self.callback:
                            self.callback(text)
                        return text

                # Check for timeout
                if self.timeout and (time.time() - start_time) > self.timeout:
                    if self.print_text:
                        print("Listening timed out. No speech detected.")
                    break
        finally:
            # Clean up
            stream.stop_stream()
            stream.close()

        # Get any final result
        result = json.loads(rec.FinalResult())
        text = result.get("text", "")
        if text and self.print_text:
            print(f"You said: {text}")
        if text and self.callback:
            self.callback(text)
        return text

    def listen_continuously(self, callback: Optional[Callable[[str], None]] = None, mic_index=None):
        """
        Listen continuously for speech and call the callback function with the recognized text.

        Args:
            callback: Function to call with recognized text
            mic_index: Optional microphone index to use
        """
        if callback:
            self.callback = callback

        if not self.callback:
            raise ValueError("No callback function provided for continuous listening.")

        # Set the listening flag
        self.is_listening = True
        self.is_paused = False

        # Start listening in a separate thread
        self.listening_thread = threading.Thread(
            target=self._listen_continuously_thread,
            args=(mic_index,)
        )
        self.listening_thread.daemon = True
        self.listening_thread.start()

    def _listen_continuously_thread(self, mic_index=None):
        """
        Thread function for continuous listening.

        Args:
            mic_index: Optional microphone index to use
        """
        if self.engine == "speechrecognition":
            self._listen_continuously_speechrecognition(mic_index)
        elif self.engine == "vosk":
            self._listen_continuously_vosk(mic_index)

    def _listen_continuously_speechrecognition(self, mic_index=None):
        """
        Listen continuously using SpeechRecognition.

        Args:
            mic_index: Optional microphone index to use
        """
        # Use the default microphone or the specified one
        mic_source = sr.Microphone(device_index=mic_index)

        with mic_source as source:
            if self.print_text:
                print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source)

            if self.print_text:
                print("Listening continuously... (Press Ctrl+C to stop)")

            try:
                while self.is_listening:
                    # Check if listening is paused
                    if self.is_paused:
                        time.sleep(0.1)  # Sleep briefly to avoid busy waiting
                        continue

                    if self.print_text:
                        print("Listening...")
                    try:
                        audio = self.recognizer.listen(
                            source,
                            timeout=self.timeout,
                            phrase_time_limit=self.phrase_time_limit
                        )
                    except sr.WaitTimeoutError:
                        if self.print_text:
                            print("Listening timed out. No speech detected.")
                        continue

                    # Check if we've been paused while listening
                    if self.is_paused:
                        continue

                    # Try to recognize the speech
                    try:
                        if self.print_text:
                            print("Recognizing...")
                        text = self.recognizer.recognize_google(audio, language=self.language)
                        if self.print_text:
                            print(f"You said: {text}")
                        self.callback(text)
                    except sr.UnknownValueError:
                        if self.print_text:
                            print("Could not understand audio")
                    except sr.RequestError as e:
                        if self.print_text:
                            print(f"Could not request results; {e}")
            except KeyboardInterrupt:
                if self.print_text:
                    print("\nStopped listening.")

    def _listen_continuously_vosk(self, mic_index=None):
        """
        Listen continuously using Vosk.

        Args:
            mic_index: Optional microphone index to use
        """
        # Set up the audio stream
        device_index = mic_index if mic_index is not None else None
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000,
            input_device_index=device_index
        )

        # Create a Vosk recognizer
        rec = KaldiRecognizer(self.model, 16000)

        if self.print_text:
            print("Listening continuously... (Press Ctrl+C to stop)")

        # Start listening
        self.stream.start_stream()

        try:
            while self.is_listening:
                # Check if listening is paused
                if self.is_paused:
                    time.sleep(0.1)  # Sleep briefly to avoid busy waiting
                    continue

                data = self.stream.read(4000, exception_on_overflow=False)
                if len(data) == 0:
                    break

                # Check if we've been paused while processing
                if self.is_paused:
                    continue

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if "text" in result and result["text"]:
                        text = result["text"]
                        if self.print_text:
                            print(f"You said: {text}")
                        self.callback(text)
        except KeyboardInterrupt:
            if self.print_text:
                print("\nStopped listening.")
        finally:
            # Clean up
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None

    def pause(self):
        """Pause listening temporarily."""
        if self.print_text:
            print("Pausing speech recognition...")
        self.is_paused = True

    def resume(self):
        """Resume listening after being paused."""
        if self.print_text:
            print("Resuming speech recognition...")
        self.is_paused = False

    def stop(self):
        """Stop listening completely."""
        if self.print_text:
            print("Stopping speech recognition...")
        self.is_listening = False
        self.is_paused = False

        # Wait for the listening thread to finish
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=1.0)

    def close(self):
        """Clean up resources."""
        self.stop()
        if self.engine == "vosk" and hasattr(self, 'p'):
            self.p.terminate()


# Example usage
if __name__ == "__main__":
    # Simple test function
    def process_text(text):
        print(f"Processing: {text}")
        # Here you would typically send the text to your assistant

    # Choose the engine based on availability
    if VOSK_AVAILABLE:
        engine = "vosk"
        # You need to download a model from https://alphacephei.com/vosk/models
        # and specify the path here
        vosk_model_path = os.path.join(os.path.expanduser("~"), "vosk-model-small-en-us-0.15")
    else:
        engine = "speechrecognition"
        vosk_model_path = None

    try:
        # Create a speech input layer
        speech_layer = SpeechInputLayer(
            engine=engine,
            vosk_model_path=vosk_model_path,
            print_text=True
        )

        # Listen for a single utterance
        print("\nTesting single utterance recognition:")
        text = speech_layer.listen()
        process_text(text)

        # Listen continuously
        print("\nTesting continuous recognition:")
        speech_layer.listen_continuously(callback=process_text)
    except ImportError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        if 'speech_layer' in locals():
            speech_layer.close()