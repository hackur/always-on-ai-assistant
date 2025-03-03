# Always-On AI Assistant

This project aims to create a flexible and configurable AI assistant that can be adapted to various use cases and environments. It leverages a modular architecture and supports different LLM workflow patterns.

## Architecture

The assistant is designed with a layered architecture:

1.  **Input Layer:** Handles user input (e.g., speech-to-text).
2.  **Processing Layer:** Core agent logic, utilizing LangGraph and workflow patterns.
3.  **Memory Layer:** Manages conversation history and state.
4.  **Output Layer:** Presents the assistant's responses (e.g., text-to-speech).
5. **Tool Layer:** External services the agent can use.

## Configuration

The assistant is configured via `.env` files. Different configurations can be used to switch between:

*   Local and remote LLM servers (e.g., LM Studio, OpenRouter, Anthropic).
*   Different input and output methods.
*   Different memory implementations.
*   Different agent configurations (including workflow patterns).

Example `.env` structure:

```
INPUT_LAYER=...
PROCESSING_LAYER=...
AGENT_1_TYPE=...
AGENT_1_MODEL=...
AGENT_1_API_KEY=...
# ... (additional agent configurations)
MEMORY_LAYER=...
OUTPUT_LAYER=...
```

## Free and Open Source Implementation

This project is designed to be implemented entirely with free and open-source resources:

* **Local LLM Serving:** Ollama, LM Studio, or LocalAI for running models locally
* **Models:** Open-source models like Mistral, Llama 3, Phi-3, etc.
* **Speech Processing:** Local STT/TTS solutions like Vosk, Whisper.cpp, pyttsx3
* **Storage:** SQLite, JSON files, or Redis for conversation history
* **Tools:** Self-hosted or free API services for search, weather, etc.

See [FREE_RESOURCES.md](FREE_RESOURCES.md) for a comprehensive list of free resources and implementation examples.

## Workflow Patterns

The processing layer can leverage various workflow patterns from the `workflows` directory, including:

*   Basic Prompt Chaining
*   Parallelization
*   Routing
*   Orchestrator-Worker
*   Evaluator-Optimizer

## Getting Started

1.  Set up your desired `.env` configuration.
2.  Install dependencies: `uv pip install -r requirements.txt`
3.  Run the assistant.

## Detailed Plans

* [PLAN.md](PLAN.md) - Detailed implementation plan for the modular architecture
* [FREE_RESOURCES.md](FREE_RESOURCES.md) - Comprehensive list of free resources and code examples