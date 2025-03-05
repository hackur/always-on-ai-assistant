# Voice Profiles for Always-On AI Assistant

This document provides information about recommended voice profiles for the Always-On AI Assistant. These profiles can be used with the `--tts-voice` parameter when running the voice assistant.

## Available Voice Engines

The Always-On AI Assistant supports three text-to-speech engines:

1. **pyttsx3** - An offline TTS engine that works across platforms
2. **gTTS** - Google Text-to-Speech (requires internet connection)
3. **kokoro** - High-quality Kokoro-82M model from HuggingFace (local, 82MB)

## Listing Available Voices

To see all available voices on your system, run:

```bash
python voice_assistant_demo.py --list-voices
```

This will display all available voices grouped by language, along with their IDs.

## Recommended Voice Profiles

Below are some recommended voice profiles for different languages and use cases. The voice IDs may vary depending on your operating system.

### English Voices

| Voice ID | Name | Description | Best For |
|----------|------|-------------|----------|
| `com.apple.voice.compact.en-US.Samantha` | Samantha | Clear, natural female voice (US English) | General purpose, default voice |
| `com.apple.eloquence.en-US.Eddy` | Eddy | Male voice with US accent | Technical explanations |
| `com.apple.voice.compact.en-GB.Daniel` | Daniel | Male voice with British accent | Formal interactions |
| `com.apple.voice.compact.en-AU.Karen` | Karen | Female voice with Australian accent | Casual conversations |
| `com.apple.voice.compact.en-IN.Rishi` | Rishi | Male voice with Indian accent | Multilingual contexts |

### Other Languages

| Voice ID | Name | Language | Description |
|----------|------|----------|-------------|
| `com.apple.voice.compact.fr-FR.Thomas` | Thomas | French | Clear male voice |
| `com.apple.voice.compact.de-DE.Anna` | Anna | German | Natural female voice |
| `com.apple.voice.compact.es-ES.Monica` | Mónica | Spanish | Warm female voice |
| `com.apple.voice.compact.it-IT.Alice` | Alice | Italian | Friendly female voice |
| `com.apple.voice.compact.ja-JP.Kyoko` | Kyoko | Japanese | Professional female voice |
| `com.apple.voice.compact.zh-CN.Tingting` | Tingting | Chinese | Clear female voice |

## Using Voice Profiles

To use a specific voice profile, run the voice assistant with the `--tts-voice` parameter:

```bash
python voice_assistant_demo.py --tts-voice "com.apple.voice.compact.en-US.Samantha"
```

You can combine this with other parameters:

```bash
python voice_assistant_demo.py --stt-engine vosk --tts-engine pyttsx3 --tts-voice "com.apple.voice.compact.en-GB.Daniel" --tts-rate 150
```

## Voice Parameters

In addition to selecting a voice, you can customize other voice parameters:

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--tts-rate` | Speech rate (words per minute) | 150 | `--tts-rate 180` for faster speech |
| `--tts-volume` | Speech volume (0.0 to 1.0) | 1.0 | `--tts-volume 0.8` for quieter speech |
## Creating Voice Profiles

You can create custom voice profiles by saving your preferred voice settings in a JSON file in the `voices` directory. For example:

```json
{
  "name": "British Assistant",
  "engine": "pyttsx3",
  "voice_id": "com.apple.voice.compact.en-GB.Daniel",
  "rate": 150,
  "volume": 0.9
}
```

Save this as `voices/british.json` and then use it with:

```bash
python voice_assistant_demo.py --voice-profile british
```

### Kokoro TTS Voice Profile

The assistant includes a high-quality TTS option using the Kokoro-82M model (from HuggingFace):

```json
{
  "name": "Kokoro TTS",
  "description": "High-quality local TTS using the Kokoro-82M model from HuggingFace",
  "engine": "kokoro",
  "model_id": "hexgrad/Kokoro-82M",
  "sample_rate": 24000,
  "language": "en-US"
}
```

To use the Kokoro TTS voice:

```bash
python voice_assistant_demo.py --voice-profile kokoro
```

First-time use will download the model (approximately 82MB) from HuggingFace. Requires PyTorch, transformers, and sounddevice packages. Install with:

```bash
uv pip install torch transformers numpy soundfile sounddevice
```
```

## Platform-Specific Notes

### macOS

macOS has a rich set of high-quality voices available through the system. You can install additional voices through System Settings > Accessibility > Spoken Content > System Voice > Manage Voices.

### Windows

Windows uses SAPI5 voices. The default voices include "Microsoft David" and "Microsoft Zira".

### Linux

Linux typically uses espeak voices, which may sound more robotic than macOS or Windows voices.

## Troubleshooting

If you encounter issues with a specific voice:

1. Verify the voice is installed on your system with `--list-voices`
2. Try a different voice ID
3. Check if the voice is compatible with your TTS engine
4. For pyttsx3, ensure you have the latest version installed