# Always-On AI Assistant - Detailed Implementation Plan

This document outlines the steps to refactor the `always-on-ai-assistant` into a modular, configurable system.

## 1. Modular Architecture

The assistant will be structured into the following layers:

### 1.1 Input Layer

*   **Purpose:** Handles all user input.
*   **Responsibilities:**
    *   Accept text input.
    *   (Optional) Integrate with speech-to-text services (e.g., Google STT, Whisper).
    *   Normalize input format (e.g., to a standard `{"input": "user text"}` dictionary).
*   **Configuration:**  The `.env` file will specify the input method (e.g., `INPUT_LAYER=local_text`, `INPUT_LAYER=google_stt`).
*   **Implementation:** Create an `input_layer.py` module with a base class `InputLayer` and subclasses for each input method (e.g., `TextInputLayer`, `SpeechToTextLayer`).  The selected layer will be instantiated based on the `.env` configuration.

### 1.2 Processing Layer

*   **Purpose:** Core agent logic and workflow management.
*   **Responsibilities:**
    *   Receive normalized input from the Input Layer.
    *   Select and execute the appropriate workflow pattern (basic chaining, parallelization, routing, orchestrator-worker, evaluator-optimizer).
    *   Manage agent interactions (LLM calls, tool use).
    *   Interact with the Memory Layer.
*   **Configuration:** The `.env` file will specify the workflow pattern and agent configuration (e.g., `PROCESSING_LAYER=basic_chaining`, `AGENT_1_TYPE=openai`, `AGENT_1_MODEL=gpt-4-turbo`). Multiple agent configurations can be defined.
*   **Implementation:**
    *   Create an `agents.py` module to define agent classes.
    *   Leverage LangGraph for workflow management.
    *   Create separate modules for each workflow pattern (similar to the `workflows` directory structure) and integrate them into the agent logic.
    *   Use a factory pattern to create the appropriate agent based on the `.env` configuration.

### 1.3 Memory Layer

*   **Purpose:** Persist conversation history and other relevant state.
*   **Responsibilities:**
    *   Store and retrieve conversation history.
    *   (Optional) Store and retrieve other agent-specific state.
*   **Configuration:** The `.env` file will specify the memory implementation (e.g., `MEMORY_LAYER=in_memory`, `MEMORY_LAYER=redis`).
*   **Implementation:** Create a `memory_layer.py` module with a base class `MemoryLayer` and subclasses for each implementation (e.g., `InMemoryMemory`, `RedisMemory`).

### 1.4 Output Layer

*   **Purpose:** Present the assistant's responses to the user.
*   **Responsibilities:**
    *   Receive text output from the Processing Layer.
    *   (Optional) Integrate with text-to-speech services (e.g., Google TTS, ElevenLabs).
    *   Output the response to the user (e.g., print to console, play audio).
*   **Configuration:** The `.env` file will specify the output method (e.g., `OUTPUT_LAYER=local_text`, `OUTPUT_LAYER=google_tts`).
*   **Implementation:** Create an `output_layer.py` module with a base class `OutputLayer` and subclasses for each output method (e.g., `TextOutputLayer`, `SpeechOutputLayer`).

### 1.5 Tool Layer/External Services
* **Purpose:**  Provide access to external tools and services.
* **Responsibilities:**
    * Define tool interfaces using LangChain's tool definition.
    * Implement tool logic.
* **Configuration:** Tools can be enabled/disabled and configured via the `.env` file or a separate configuration file.
* **Implementation:** Create a `tools.py` module to define and implement tools.

## 2. .env File Structure

The `.env` file will be structured to allow easy switching between different configurations. Example:

```
# Input Layer
INPUT_LAYER=local_text  # Or google_stt, etc.

# Processing Layer
PROCESSING_LAYER=basic_chaining  # Or parallelization, routing, orchestrator-worker, evaluator-optimizer

# Agent 1 Configuration (can have multiple agents)
AGENT_1_TYPE=openai  # Or anthropic, ollama, lmstudio
AGENT_1_MODEL=gpt-4-turbo
AGENT_1_API_KEY=your_openai_key
#AGENT_1_BASE_URL=... (if needed, e.g., for local servers)

# Agent 2 Configuration (example)
#AGENT_2_TYPE=ollama
#AGENT_2_MODEL=mistralai/Mistral-7B-Instruct-v0.1
#AGENT_2_BASE_URL=http://localhost:11434

# Memory Layer
MEMORY_LAYER=in_memory  # Or redis, etc.

# Output Layer
OUTPUT_LAYER=local_text  # Or google_tts, etc.

# Tool Layer (example)
#SEARCH_TOOL_ENABLED=true
#SEARCH_TOOL_API_KEY=...
```

## 3. Workflow Integration

The workflow patterns from the `workflows` directory will serve as examples and templates for implementing the agent logic within the Processing Layer.  The `PROCESSING_LAYER` variable in the `.env` file will determine which workflow pattern is used.  The agent configuration (e.g., `AGENT_1_TYPE`, `AGENT_1_MODEL`) will determine the specific LLM and parameters used within that workflow.

## 4. Implementation Steps

1.  **Create directory structure:**  Create the necessary directories and files within `always-on-ai-assistant` (e.g., `input_layer.py`, `processing_layer.py`, `memory_layer.py`, `output_layer.py`, `agents.py`, `tools.py`).
2.  **Implement base classes:** Create base classes for each layer (e.g., `InputLayer`, `ProcessingLayer`, `MemoryLayer`, `OutputLayer`).
3.  **Implement specific layer implementations:** Create subclasses for each layer based on the desired functionality (e.g., `TextInputLayer`, `OpenAIAgent`, `InMemoryMemory`, `TextOutputLayer`).
4.  **Implement .env loading and configuration:** Use `python-dotenv` to load the `.env` file and create a configuration object to manage settings.
5.  **Implement agent factory:** Create a factory function in `agents.py` to create the appropriate agent based on the configuration.
6.  **Integrate workflow patterns:**  Adapt the code from the `workflows` directory examples into the `processing_layer.py` and `agents.py` modules.
7.  **Connect layers:**  Connect the input, processing, memory, and output layers in the main application logic (likely in `main.py`).
8.  **Implement tool integration:** Define and implement tools in `tools.py` and integrate them with the agent.
9. **Add error handling:** Implement error handling at each layer and in the main application logic.
10. **Add logging:** Implement logging to track the assistant's behavior and debug issues.

## 5. Error Handling

*   Each layer should handle potential errors (e.g., API connection errors, invalid input, tool failures).
*   Use `try-except` blocks to catch exceptions and provide appropriate responses or fallback mechanisms.
*   Log errors for debugging.

## 6. Testing

*   **Unit tests:**  Test individual components (layers, tools, utility functions).
*   **Integration tests:** Test the interaction between different layers.
*   **End-to-end tests:** Test the complete assistant workflow with various inputs and scenarios.
*   **Test different configurations:** Test with different `.env` configurations to ensure flexibility.

## 7. Minimum Viable Product (MVP) Implementation Plan - Free and Open Source

This section outlines a plan for a minimal, free, and open-source implementation of the always-on AI assistant, leveraging locally running models and services.

### 7.1.  Goals

*   Create a functional, text-based AI assistant.
*   Use only free and open-source tools and models.
*   Run entirely locally (no paid APIs).
*   Demonstrate the basic layered architecture.
*   Use the simplest possible workflow (basic prompt chaining).

### 7.2. Technology Choices

*   **LLM Serving:** Ollama (for ease of use and local execution).
*   **Model:**  `mistralai/Mistral-7B-Instruct-v0.1` (a good balance of performance and resource requirements, readily available via Ollama).
*   **Input:**  Text input from the command line.
*   **Output:** Text output to the command line.
*   **Memory:**  Simple in-memory storage (e.g., a Python list).
*   **Workflow:** Basic prompt chaining.
*   **Query Helper:** Utilize `servers/query_helper.py` for efficient local model querying.

### 7.3.  .env Configuration

Create a file named `.env.local` with the following content:

```
INPUT_LAYER=local_text
PROCESSING_LAYER=basic_chaining
AGENT_1_TYPE=ollama
AGENT_1_MODEL=mistralai/Mistral-7B-Instruct-v0.1
AGENT_1_BASE_URL=http://localhost:11434  # Default Ollama URL
MEMORY_LAYER=in_memory
OUTPUT_LAYER=local_text
```

### 7.4. Implementation Steps

1.  **Set up Ollama:** Download and install Ollama. Pull the `mistralai/Mistral-7B-Instruct-v0.1` model.  This can be done with the command: `ollama pull mistralai/Mistral-7B-Instruct-v0.1`
2.  **Create `input_layer.py`:** Implement a `TextInputLayer` class that takes input from the command line using the `input()` function.
3.  **Create `processing_layer.py`:**
    *   Implement a `BasicChainingAgent` class.
    *   Use `servers/query_helper.py` to interact with the Ollama server.
    *   Implement a simple prompt chaining workflow (e.g., take user input, generate a response, print the response).
4.  **Create `memory_layer.py`:** Implement an `InMemoryMemory` class that stores conversation history in a Python list.
5.  **Create `output_layer.py`:** Implement a `TextOutputLayer` class that prints output to the console.
6.  **Modify `main.py`:**
    *   Load the `.env.local` configuration.
    *   Instantiate the appropriate layer classes based on the configuration.
    *   Implement the main loop: get input, process, store in memory, output response.
7. **Create a basic `prompt_templates.json`:** Define a simple prompt template for the basic chaining workflow.
8. **Create a `presets.json`:** Define a preset for the basic chaining workflow, referencing the prompt template.

### 7.5.  Testing

1.  Run the assistant and interact with it via the command line.
2.  Verify that the input, processing, memory, and output layers are working correctly.
3.  Test different input prompts to ensure the agent responds appropriately.

### 7.6.  Further Development

This MVP provides a foundation for further development.  Future enhancements could include:

*   Adding support for more complex workflow patterns.
*   Integrating with speech-to-text and text-to-speech services.
*   Implementing more sophisticated memory mechanisms.
*   Adding support for external tools.
*   Improving error handling and robustness.
*   Adding more comprehensive testing.