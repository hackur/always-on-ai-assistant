# Future Plans for Always-On AI Assistant

This document outlines planned features and improvements for future versions of
 the Always-On AI Assistant.

## Voice Assistant Enhancements

### Voice Profile Switching

- **Dynamic Voice Profile Changes**: Allow the assistant to change its voice or

  - "Change your voice to British"
  - "Switch to technical voice profile"
  - "Use a different voice"

- **Implementation Plan**:
  1. Add a command handler in the voice assistant that recognizes voice change requests
  2. Implement a mechanism to reload the TTS layer with new voice settings
  3. Add confirmation responses when voice is changed
  4. Update documentation with new voice commands

### Additional Voice Features

- Adjust speech rate during conversation
- Control volume dynamically
- Add more diverse voice profiles
- ✅ Support for additional TTS engines (Added Kokoro-82M HuggingFace model)
- Emotion detection and response tone matching

## Other Planned Improvements

- Improved wake word detection with fewer false positives
- Better noise cancellation for speech recognition
- Multi-language support
- Customizable command keywords
- User-specific voice profiles
- Persistent conversation history
- Integration with smart home devices

## Technical Debt and Improvements

- Fix "run loop not started" warning with pyttsx3
- Improve error handling for all TTS and STT engines
- Create more comprehensive tests for voice interactions
- Add metrics for speech recognition accuracy