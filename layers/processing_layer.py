"""
Processing Layer for the Always-On AI Assistant.
This module handles the core agent logic and workflow management.
"""

import os
import sys
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

# Add the parent directory to sys.path to import query_helper
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../servers')))
try:
    from query_helper import query_model
except ImportError:
    # Fallback implementation if query_helper is not available
    def query_model(model_type, model_name, prompt, base_url=None, **kwargs):
        print(f"WARNING: query_helper not found. Using mock implementation.")
        print(f"Would query {model_type} model {model_name} at {base_url}")
        return f"This is a mock response. The actual implementation would query the {model_name} model."

from .memory_layer import MemoryLayer


class ProcessingLayer(ABC):
    """Base class for all processing layers."""

    @abstractmethod
    def process(self, user_input: Dict[str, Any]) -> str:
        """
        Process the user input and generate a response.

        Args:
            user_input (Dict[str, Any]): The user input.

        Returns:
            str: The assistant's response.
        """
        pass


class BasicChainingAgent(ProcessingLayer):
    """
    Processing layer that implements a basic prompt chaining workflow.
    Uses the query_helper to interact with LLM servers.
    """

    def __init__(self, memory: MemoryLayer, config: Dict[str, Any]):
        """
        Initialize the basic chaining agent.

        Args:
            memory (MemoryLayer): The memory layer to use.
            config (Dict[str, Any]): Configuration dictionary.
        """
        self.memory = memory
        self.model_type = config.get("AGENT_1_TYPE", "ollama")
        self.model_name = config.get("AGENT_1_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
        self.base_url = config.get("AGENT_1_BASE_URL", "http://localhost:11434")

        # Load prompt templates
        self.prompt_template_name = config.get("PROMPT_TEMPLATE", "basic_chaining")
        self.prompt_templates = self._load_prompt_templates()

        # Get the selected prompt template
        self.prompt_template = self.prompt_templates.get(
            self.prompt_template_name,
            self.prompt_templates.get("basic_chaining", {})
        )

        # Get system prompt from template or config
        self.system_prompt = self.prompt_template.get("system", config.get("SYSTEM_PROMPT",
            "You are a helpful, friendly AI assistant. Answer the user's questions concisely and accurately."))

    def _load_prompt_templates(self) -> Dict[str, Any]:
        """
        Load prompt templates from the JSON file.

        Returns:
            Dict[str, Any]: Prompt templates dictionary.
        """
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the prompt templates file
        templates_path = os.path.join(current_dir, "prompt_templates.json")

        # Load prompt templates
        if os.path.exists(templates_path):
            try:
                with open(templates_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse prompt templates file {templates_path}.")
                return {}
        else:
            print(f"Warning: Prompt templates file {templates_path} not found.")
            return {}

    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """
        Format the conversation history for inclusion in the prompt.

        Args:
            history (List[Dict[str, Any]]): The conversation history.

        Returns:
            str: The formatted history.
        """
        user_prefix = self.prompt_template.get("user_prefix", "User: ")
        assistant_prefix = self.prompt_template.get("assistant_prefix", "Assistant: ")

        formatted = ""
        for entry in history:
            user_text = entry["user_input"].get("text", "")
            assistant_text = entry["assistant_response"]
            formatted += f"{user_prefix}{user_text}\n{assistant_prefix}{assistant_text}\n\n"
        return formatted.strip()

    def process(self, user_input: Dict[str, Any]) -> str:
        """
        Process the user input using a basic prompt chaining workflow.

        Args:
            user_input (Dict[str, Any]): The user input.

        Returns:
            str: The assistant's response.
        """
        # Get conversation history
        history = self.memory.get_history()

        # Format history
        formatted_history = self._format_history(history)

        # Get user text
        user_text = user_input.get("text", "")

        # Prepare prompt using template format
        prompt_format = self.prompt_template.get("format", "{system}\n\n{history}\n\n{user_prefix}{user_input}\n{assistant_prefix}")
        user_prefix = self.prompt_template.get("user_prefix", "User: ")
        assistant_prefix = self.prompt_template.get("assistant_prefix", "Assistant: ")

        # Format the prompt
        prompt = prompt_format.format(
            system=self.system_prompt,
            history=formatted_history if formatted_history else "",
            user_prefix=user_prefix,
            user_input=user_text,
            assistant_prefix=assistant_prefix
        )

        # Query model using query_helper
        try:
            response = query_model(
                model_type=self.model_type,
                model_name=self.model_name,
                prompt=prompt,
                base_url=self.base_url
            )
        except Exception as e:
            response = f"I'm sorry, I encountered an error: {str(e)}"

        return response


# Factory function to create the appropriate processing layer based on configuration
def create_processing_layer(config: Dict[str, Any], memory: MemoryLayer) -> ProcessingLayer:
    """
    Create a processing layer based on the configuration.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
            Should contain a 'PROCESSING_LAYER' key.
        memory (MemoryLayer): The memory layer to use.

    Returns:
        ProcessingLayer: An instance of the appropriate processing layer.

    Raises:
        ValueError: If the processing layer type is not supported.
    """
    processing_layer_type = config.get("PROCESSING_LAYER", "basic_chaining")

    if processing_layer_type == "basic_chaining":
        return BasicChainingAgent(memory, config)
    else:
        raise ValueError(f"Unsupported processing layer type: {processing_layer_type}")