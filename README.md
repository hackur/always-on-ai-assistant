# Always-On AI Assistant

A versatile, modular AI assistant framework that provides continuous assistance through voice interaction and natural language processing.

## Features

- **Voice Interaction**: Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities for natural interaction
- **Modular Architecture**: Easily extensible with new capabilities and integrations
- **Multiple LLM Support**: Compatible with various Large Language Models (Ollama, OpenAI, Anthropic, etc.)
- **Customizable Prompts**: Configure how the assistant responds with template-based prompting
- **Voice Profiles**: Customize the assistant's voice with predefined or custom voice profiles
- **Logging System**: Comprehensive logging with timestamped log files for each session
- **macOS Integration**: Easy installation with Globe/Fn key shortcut support on MacBook Pro
- **Environment Configuration**: Simple setup through environment variables and configuration files
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management (recommended)
- For TTS: speakers or headphones
- For STT: microphone

### Installation

#### Standard Installation

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

#### macOS Installation with Globe/Fn Key Support

For MacBook Pro users who want to trigger the assistant with the Globe/Fn key:

```bash
# Run the macOS installer script
python install-to-mac.py

# Or specify a custom voice profile
python install-to-mac.py --voice-profile british

# Or specify a custom wake word
python install-to-mac.py --wake-word "hey computer"
```

The installer will:
1. Copy the assistant files to `~/Applications/AlwaysOnAIAssistant`
2. Install required dependencies
3. Set up a launch agent to run at login
4. Create a keyboard shortcut for the Globe/Fn key
5. Install the Vosk model for offline speech recognition

After installation, follow the on-screen instructions to complete the keyboard shortcut setup.

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

# With verbose logging
uv run voice_assistant_demo.py --verbose
```

## Voice Profiles

The assistant supports customizable voice profiles that define the voice characteristics:

### Listing Available Voices

To see all available system voices:

```bash
uv run voice_assistant_demo.py --list-voices
```

### Using Voice Profiles

The assistant comes with several predefined voice profiles:

```bash
# List available voice profiles
uv run voice_assistant_demo.py --list-profiles

# Use a specific voice profile
uv run voice_assistant_demo.py --voice-profile british
```

### Creating Custom Voice Profiles

You can create custom voice profiles by adding JSON files to the `voices` directory. See [VOICES.md](voices/VOICES.md) for details.

Example voice profile:

```json
{
  "name": "My Custom Voice",
  "description": "Custom voice with specific settings",
  "engine": "pyttsx3",
  "voice_id": "com.apple.voice.compact.en-US.Samantha",
  "rate": 150,
  "volume": 0.9,
  "language": "en-US"
}
```

## Logging System

The assistant includes a comprehensive logging system that records all activities:

- Logs are stored in the `logs` directory
- Each session creates a timestamped log file (e.g., `voice_assistant_2025-03-03_00-51-23.log`)
- Logs include information about:
  - Voice profile and engine settings
  - Speech recognition events
  - LLM queries and responses
  - Errors and warnings

To enable verbose logging:

```bash
uv run voice_assistant_demo.py --verbose
```

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
| `LLM_MODEL_NAME` | Name of the LLM model | `mistral:instruct` |
| `LLM_BASE_URL` | Base URL for the LLM API | `http://localhost:11434` |

### Command Line Arguments

The assistant scripts support various command-line arguments:

#### Common Arguments

- `--verbose`: Enable verbose output and detailed logging

#### Text-to-Speech Arguments

- `--tts-engine`: TTS engine to use (`pyttsx3` or `gtts`)
- `--tts-voice`: Voice ID for pyttsx3
- `--tts-rate`: Speech rate in words per minute
- `--tts-volume`: Speech volume (0.0 to 1.0)
- `--voice-profile`: Use a predefined voice profile
- `--list-voices`: List available system voices
- `--list-profiles`: List available voice profiles

#### Speech-to-Text Arguments

- `--stt-engine` or `--engine`: STT engine to use (`speechrecognition` or `vosk`)
- `--language`: Language code for speech recognition
- `--vosk-model-path`: Path to the Vosk model directory
- `--wake-word`: Wake word to activate the assistant (e.g., "hey assistant")

#### LLM Arguments

- `--model`: LLM model to use
- `--model-type`: Type of LLM to use
- `--base-url`: Base URL for the LLM API

#### macOS Installer Arguments

- `--voice-profile`: Voice profile to use (default: default)
- `--model`: LLM model to use (default: mistral:instruct)
- `--wake-word`: Wake word to activate the assistant (default: "hey assistant")
- `--install-dir`: Installation directory (default: ~/Applications/AlwaysOnAIAssistant)

## Project Structure

```
always-on-ai-assistant/
├── .env.sample                # Sample environment variables
├── README.md                  # This file
├── VOSK_MODELS.md             # Information about Vosk models
├── install-to-mac.py          # macOS installation script
├── main.py                    # Main entry point
├── live_tts_demo.py           # Text-to-speech demo
├── live_stt_demo.py           # Speech-to-text demo
├── voice_assistant_demo.py    # Complete voice assistant demo
├── setup_vosk_model.py        # Script to download Vosk models
├── requirements.txt           # Project dependencies
├── logs/                      # Directory for log files
├── models/                    # Directory for Vosk models
├── voices/                    # Voice profiles
│   ├── VOICES.md              # Documentation for voice profiles
│   ├── default.json           # Default voice profile
│   ├── british.json           # British voice profile
│   └── technical.json         # Technical voice profile
├── ai_docs/                   # AI documentation
├── commands/                  # Command implementations
├── images/                    # Project images
├── layers/                    # Architectural layers
│   ├── __init__.py
│   ├── speech_input_layer.py  # Speech recognition layer
│   ├── output_layer.py        # Output layer (including TTS)
│   └── ...                    # Other layers
├── modules/                   # Core modules
│   ├── __init__.py
│   ├── assistant_config.py    # Configuration handling
│   ├── base_assistant.py      # Base assistant implementation
│   ├── data_types.py          # Data type definitions
│   ├── execute_python.py      # Python execution utilities
│   ├── ollama.py              # Ollama integration
│   ├── query_helper.py        # LLM query helper
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