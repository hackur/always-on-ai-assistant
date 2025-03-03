# Always-On AI Assistant

This project aims to create a flexible and configurable AI assistant that can be adapted to various use cases and environments. It leverages a modular architecture and supports different LLM workflow patterns.

## Architecture

The assistant is designed with a layered architecture:

1. **Input Layer:** Handles user input (e.g., speech-to-text).
2. **Processing Layer:** Core agent logic, utilizing LLMs and workflow patterns.
3. **Memory Layer:** Manages conversation history and state.
4. **Output Layer:** Presents the assistant's responses (e.g., text-to-speech).
5. **Tool Layer:** External services the agent can use.

## Current Implementation

We have implemented a modular, layered architecture with the following components:

- **Input Layer:** Currently supports text input from the command line.
- **Processing Layer:** Implements a basic prompt chaining workflow using Ollama for local LLM serving.
- **Memory Layer:** Supports in-memory storage and JSON file storage for conversation history.
- **Output Layer:** Supports plain text and colored text output to the console.

The implementation follows a clean, modular design with well-defined interfaces for each layer, making it easy to extend with new capabilities.

## Next Steps: Voice Integration Plan

### Phase 1: Text-to-Speech Integration (Current Priority)

1. **Research and Select TTS Library:**
   - **Option 1:** pyttsx3 (offline, cross-platform)
   - **Option 2:** gTTS (Google Text-to-Speech, requires internet)
   - **Option 3:** Edge-TTS (Microsoft Edge TTS, good quality)

2. **Implementation Steps:**
   - Create a `TextToSpeechOutputLayer` class in `layers/output_layer.py`
   - Implement the `output` method to convert text to speech
   - Update the `create_output_layer` function to handle the new layer type
   - Add configuration options in `.env.local`
   - Update requirements.txt with the selected TTS library

3. **Testing and Refinement:**
   - Test with different voices and speech rates
   - Add configuration options for voice selection, rate, and volume
   - Implement error handling for TTS failures

### Phase 2: Speech-to-Text Integration (Future)

1. **Research and Select STT Library:**
   - **Option 1:** Vosk (offline, lightweight)
   - **Option 2:** Whisper.cpp (offline, high accuracy)
   - **Option 3:** SpeechRecognition with Google (requires internet)

2. **Implementation Steps:**
   - Create a `SpeechToTextInputLayer` class in `layers/input_layer.py`
   - Implement the `get_input` method to convert speech to text
   - Update the `create_input_layer` function to handle the new layer type
   - Add configuration options in `.env.local`

3. **Testing and Refinement:**
   - Test with different microphones and environments
   - Add wake word detection
   - Implement noise filtering and silence detection

### Phase 3: Full Voice Assistant Integration

1. **Continuous Listening Mode:**
   - Implement a continuous listening loop
   - Add wake word detection
   - Implement conversation state management

2. **Multi-modal Integration:**
   - Support both voice and text input/output simultaneously
   - Add visual indicators for listening/speaking states

3. **Performance Optimization:**
   - Optimize for low latency
   - Implement caching for frequently used phrases
   - Add streaming TTS for faster response times

## Configuration

The assistant is configured via `.env` files. Different configurations can be used to switch between:

* Local and remote LLM servers (e.g., LM Studio, OpenRouter, Anthropic).
* Different input and output methods.
* Different memory implementations.
* Different agent configurations (including workflow patterns).

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

* Basic Prompt Chaining
* Parallelization
* Routing
* Orchestrator-Worker
* Evaluator-Optimizer

## Getting Started

1. Set up your desired `.env` configuration in the `layers` directory.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the assistant: `python main_layered.py`

## Usage

Once the assistant is running, you can interact with it via the command line. Type your message and press Enter to send it. The assistant will respond with its generated reply.

Type `exit` or `quit` to end the conversation.

## Prompt Templates

The assistant uses prompt templates defined in `layers/prompt_templates.json`. You can modify these templates or add new ones to change how the assistant formats prompts for the LLM.

Available templates:
- `basic_chaining`: A simple template for general conversation
- `detailed_response`: A template for generating detailed, comprehensive answers
- `concise_response`: A template for generating brief, to-the-point answers
- `coding_assistant`: A template for programming-related questions

## Testing

Run the tests with:

```bash
python -m unittest discover -s tests
```

## Extending the Assistant

### Adding a New Input Layer

1. Create a new class that inherits from `InputLayer` in `layers/input_layer.py`
2. Implement the `get_input` method
3. Update the `create_input_layer` function to handle the new layer type

### Adding a New Output Layer

1. Create a new class that inherits from `OutputLayer` in `layers/output_layer.py`
2. Implement the `output` method
3. Update the `create_output_layer` function to handle the new layer type

## Detailed Plans

* [PLAN.md](PLAN.md) - Detailed implementation plan for the modular architecture
* [FREE_RESOURCES.md](FREE_RESOURCES.md) - Comprehensive list of free resources and code examples
* [LAYERED_README.md](LAYERED_README.md) - Detailed documentation for the layered implementation