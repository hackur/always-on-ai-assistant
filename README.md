# Always-On AI Assistant

A versatile, modular AI assistant framework that provides continuous assistance through voice interaction and natural language processing.

## Features

- **Voice Interaction**: Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities for natural interaction
- **Modular Architecture**: Easily extensible with new capabilities and integrations
- **Multiple LLM Support**: Compatible with various Large Language Models (Ollama, OpenAI, Anthropic, etc.)
- **Customizable Prompts**: Configure how the assistant responds with template-based prompting
- **Environment Configuration**: Simple setup through environment variables and configuration files
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management (recommended)
- For TTS: speakers or headphones
- For STT: microphone

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/always-on-ai-assistant.git
   cd always-on-ai-assistant
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Create a `.env` file based on the sample:
   ```bash
   cp .env.sample .env
   ```

4. Edit the `.env` file to configure your assistant

5. For speech recognition with Vosk (optional but recommended for offline use):
   ```bash
   # Run the setup script to download and install a Vosk model
   uv run setup_vosk_model.py

   # Or specify a different model size
   uv run setup_vosk_model.py --model medium
   ```

### Running the Assistant

#### Text-to-Speech Demo

```bash
uv run live_tts_demo.py
```

#### Speech-to-Text Demo

```bash
# Using SpeechRecognition (online)
uv run live_stt_demo.py

# Using Vosk (offline)
uv run live_stt_demo.py --engine vosk
```

#### Complete Voice Assistant

```bash
# Basic usage
uv run voice_assistant_demo.py

# With wake word activation
uv run voice_assistant_demo.py --wake-word "hey assistant"

# With specific engines
uv run voice_assistant_demo.py --stt-engine vosk --tts-engine pyttsx3
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ASSISTANT_PROMPT_TEMPLATE` | Template for LLM prompts | Basic helpful assistant template |
| `TTS_ENGINE` | Text-to-speech engine | `pyttsx3` |
| `TTS_VOICE_ID` | Voice ID for TTS | System default |
| `TTS_RATE` | Speech rate (words per minute) | `150` |
| `TTS_VOLUME` | Speech volume (0.0 to 1.0) | `1.0` |
| `TTS_LANGUAGE` | Language code for gTTS | `en` |
| `LLM_MODEL_TYPE` | Type of LLM to use | `ollama` |
| `LLM_MODEL_NAME` | Name of the LLM model | `mistralai/Mistral-7B-Instruct-v0.1` |
| `LLM_BASE_URL` | Base URL for the LLM API | `http://localhost:11434` |

### Command Line Arguments

The assistant scripts support various command-line arguments:

#### Common Arguments

- `--verbose`: Enable verbose output

#### Text-to-Speech Arguments

- `--tts-engine`: TTS engine to use (`pyttsx3` or `gtts`)
- `--tts-voice`: Voice ID for pyttsx3
- `--tts-rate`: Speech rate in words per minute
- `--tts-volume`: Speech volume (0.0 to 1.0)

#### Speech-to-Text Arguments

- `--stt-engine` or `--engine`: STT engine to use (`speechrecognition` or `vosk`)
- `--language`: Language code for speech recognition
- `--vosk-model-path`: Path to the Vosk model directory
- `--wake-word`: Wake word to activate the assistant (e.g., "hey assistant")

#### LLM Arguments

- `--model`: LLM model to use
- `--model-type`: Type of LLM to use
- `--base-url`: Base URL for the LLM API

## Speech Recognition

The assistant supports two speech recognition engines:

### SpeechRecognition

- Uses Google's speech recognition API by default
- Requires an internet connection
- High accuracy
- No setup required

### Vosk

- Offline speech recognition
- Privacy-focused (no data sent to external servers)
- Requires downloading a model
- See [VOSK_MODELS.md](VOSK_MODELS.md) for more information

## Project Structure

```
always-on-ai-assistant/
├── .env.sample                # Sample environment variables
├── README.md                  # This file
├── VOSK_MODELS.md             # Information about Vosk models
├── main.py                    # Main entry point
├── live_tts_demo.py           # Text-to-speech demo
├── live_stt_demo.py           # Speech-to-text demo
├── voice_assistant_demo.py    # Complete voice assistant demo
├── setup_vosk_model.py        # Script to download Vosk models
├── requirements.txt           # Project dependencies
├── models/                    # Directory for Vosk models
├── ai_docs/                   # AI documentation
├── commands/                  # Command implementations
├── images/                    # Project images
├── layers/                    # Architectural layers
│   ├── __init__.py
│   ├── speech_input_layer.py  # Speech recognition layer
│   └── ...                    # Other layers
├── modules/                   # Core modules
│   ├── __init__.py
│   ├── assistant_config.py    # Configuration handling
│   ├── base_assistant.py      # Base assistant implementation
│   ├── data_types.py          # Data type definitions
│   ├── execute_python.py      # Python execution utilities
│   ├── ollama.py              # Ollama integration
│   ├── typer_agent.py         # Typer CLI agent
│   └── utils.py               # Utility functions
├── prompts/                   # Prompt templates
└── tests/                     # Test suite
    ├── __init__.py
    ├── .env.test              # Test environment variables
    ├── test_helper.py         # Test utilities
    ├── test_speech_input_layer.py # Speech input tests
    └── ...                    # Various test modules
```

## Extending the Assistant

### Adding New Voice Capabilities

The assistant uses a modular architecture that makes it easy to add new voice capabilities:

1. For new TTS engines, extend the `TextToSpeechOutputLayer` class
2. For new STT engines, extend the `SpeechInputLayer` class

### Custom Commands

Create new command modules in the `commands/` directory following the template pattern.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.