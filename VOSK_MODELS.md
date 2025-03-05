# Vosk Speech Recognition Models

This document provides information about Vosk speech recognition models and how to use them with the Always-On AI Assistant.

## Recommended Models

Vosk offers several models with different sizes and language support. Here are the recommended models for English:

| Model | Size | Description | Download Link |
|-------|------|-------------|--------------|
| **vosk-model-small-en-us-0.15** | ~40 MB | Small model for English (US), good balance of size and accuracy | [Download](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip) |
| vosk-model-en-us-0.22 | ~1.8 GB | Large model for English (US), higher accuracy but requires more resources | [Download](https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip) |
| vosk-model-en-us-0.42-gigaspeech | ~2.3 GB | Very large model for English (US), highest accuracy | [Download](https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip) |

For most desktop applications, the **small model** (vosk-model-small-en-us-0.15) is recommended as it provides a good balance between accuracy and resource usage.

## Installation

1. Download the recommended model (vosk-model-small-en-us-0.15) from the link above
2. Extract the ZIP file
3. Place the extracted folder in one of these locations:

   - **Recommended location**: Create a `models` directory in the project root and place the model there:
     ```
     always-on-ai-assistant/models/vosk-model-small-en-us-0.15/
     ```

   - **Alternative locations** (automatically detected by the application):
     - Your home directory: `~/vosk-model-small-en-us-0.15/`
     - The current working directory: `./vosk-model-small-en-us-0.15/`

## Usage

When running the speech recognition demos, you can specify the model path:

```bash
# Using the model in the recommended location
uv run voice_assistant_demo.py --stt-engine vosk --vosk-model-path models/vosk-model-small-en-us-0.15

# The application will also try to find the model automatically if you don't specify a path
uv run voice_assistant_demo.py --stt-engine vosk
```

## Non-English Models

Vosk supports many languages. Visit the [Vosk Models page](https://alphacephei.com/vosk/models) to find models for other languages.

When using a non-English model, make sure to also set the appropriate language code:

```bash
# Example for Spanish
uv run voice_assistant_demo.py --stt-engine vosk --vosk-model-path models/vosk-model-small-es-0.42 --language es-ES
```

## Model Performance

- **Small models** (40-50 MB): Good for command recognition and simple dictation
- **Medium models** (500-700 MB): Better accuracy for general dictation
- **Large models** (1.5-2.5 GB): Best accuracy, suitable for professional transcription

Choose the model size based on your hardware capabilities and accuracy requirements.