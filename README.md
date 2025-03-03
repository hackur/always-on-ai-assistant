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

### Running the Assistant

#### Basic Usage

```bash
uv run main.py
```

#### Text-to-Speech Demo

```bash
uv run live_tts_demo.py
```

#### With Custom Configuration

```bash
uv run live_tts_demo.py --engine gtts --voice "en-US" --rate 150
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

The `live_tts_demo.py` script supports the following arguments:

- `--engine`: TTS engine to use (`pyttsx3` or `gtts`)
- `--voice`: Voice ID for pyttsx3
- `--rate`: Speech rate in words per minute
- `--volume`: Speech volume (0.0 to 1.0)
- `--language`: Language code for gTTS
- `--model`: LLM model to use
- `--model-type`: Type of LLM to use
- `--base-url`: Base URL for the LLM API
- `--verbose`: Enable verbose output

## Project Structure

```
always-on-ai-assistant/
├── .env.sample                # Sample environment variables
├── README.md                  # This file
├── main.py                    # Main entry point
├── live_tts_demo.py           # Text-to-speech demo
├── requirements.txt           # Project dependencies
├── ai_docs/                   # AI documentation
├── commands/                  # Command implementations
├── images/                    # Project images
├── layers/                    # Architectural layers
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
    └── ...                    # Various test modules
```

## Extending the Assistant

### Adding New Voice Capabilities

The assistant uses a modular architecture that makes it easy to add new voice capabilities:

1. For new TTS engines, extend the `TextToSpeechOutputLayer` class
2. For new STT engines, implement a new input layer based on the existing patterns

### Custom Commands

Create new command modules in the `commands/` directory following the template pattern.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.