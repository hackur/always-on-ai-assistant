# Always-On AI Assistant - Layered Implementation

This is a modular implementation of the Always-On AI Assistant, designed to be configurable and extensible. It uses a layered architecture to separate concerns and allow for easy swapping of components.

## Architecture

The assistant is designed with a layered architecture:

1. **Input Layer:** Handles user input (e.g., text input from the command line).
2. **Processing Layer:** Core agent logic, using LLMs for generating responses.
3. **Memory Layer:** Manages conversation history and state.
4. **Output Layer:** Presents the assistant's responses (e.g., text output to the command line).

## Prerequisites

- Python 3.8 or higher
- Ollama (for local LLM serving)
- Required Python packages (install with `pip install -r requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd always-on-ai-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install and start Ollama:
   ```bash
   # Follow instructions at https://ollama.ai/download
   # Start the Ollama server
   ollama serve
   ```

4. Pull the Mistral model:
   ```bash
   ollama pull mistralai/Mistral-7B-Instruct-v0.1
   ```

## Configuration

The assistant is configured via the `.env.local` file in the `layers` directory. You can modify this file to change the behavior of the assistant.

Available configurations:

- **Input Layer:** `local_text` (command line input)
- **Processing Layer:** `basic_chaining` (simple prompt chaining)
- **Agent Type:** `ollama` (local LLM serving)
- **Agent Model:** `mistralai/Mistral-7B-Instruct-v0.1` (or any other model available in Ollama)
- **Memory Layer:** `in_memory` (stores conversation history in memory) or `json_file` (stores in a JSON file)
- **Output Layer:** `local_text` (plain text output) or `colored_text` (colored text output)

## Running the Assistant

Run the assistant with:

```bash
python main_layered.py
```

Or, if you made the script executable:

```bash
./main_layered.py
```

You can specify a different environment file with:

```bash
python main_layered.py --env-file custom.env
```

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

To use a different template, set the `PROMPT_TEMPLATE` variable in the `.env.local` file.

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

### Adding a New Memory Layer

1. Create a new class that inherits from `MemoryLayer` in `layers/memory_layer.py`
2. Implement the required methods
3. Update the `create_memory_layer` function to handle the new layer type

### Adding a New Output Layer

1. Create a new class that inherits from `OutputLayer` in `layers/output_layer.py`
2. Implement the `output` method
3. Update the `create_output_layer` function to handle the new layer type

### Adding a New Processing Layer

1. Create a new class that inherits from `ProcessingLayer` in `layers/processing_layer.py`
2. Implement the `process` method
3. Update the `create_processing_layer` function to handle the new layer type

## TODO

- [ ] Add support for speech-to-text input
- [ ] Add support for text-to-speech output
- [ ] Implement more sophisticated memory mechanisms (e.g., vector storage)
- [ ] Add support for external tools and APIs
- [ ] Implement more complex workflow patterns (e.g., routing, orchestrator-worker)