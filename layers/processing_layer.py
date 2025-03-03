#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processing Layer for the Always-On AI Assistant.

This module defines the processing layer interface and implementations for the assistant.
The processing layer is responsible for the core agent logic and workflow management,
including interacting with language models to generate responses to user input.

Classes:
    ProcessingLayer: Abstract base class for all processing layers.
    BasicChainingAgent: Implementation that uses a basic prompt chaining workflow.

Functions:
    create_processing_layer: Factory function to create the appropriate processing layer.

Typical usage example:
    config = load_config()
    memory_layer = create_memory_layer(config)
    processing_layer = create_processing_layer(config, memory_layer)
    response = processing_layer.process(user_input)
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
        """
        Mock implementation of query_model for when the actual module is not available.

        Args:
            model_type (str): The type of model to query (e.g., 'ollama', 'openai').
            model_name (str): The name of the model to query.
            prompt (str): The prompt to send to the model.
            base_url (str, optional): The base URL for the API. Defaults to None.
            **kwargs: Additional keyword arguments to pass to the API.

        Returns:
            str: A mock response indicating that this is a fallback implementation.

        Note:
            This function is only used when the actual query_helper module cannot be imported.
            It prints a warning message and returns a mock response.
        """
        print(f"WARNING: query_helper not found. Using mock implementation.")
        print(f"Would query {model_type} model {model_name} at {base_url}")
        return f"This is a mock response. The actual implementation would query the {model_name} model."

from .memory_layer import MemoryLayer


class ProcessingLayer(ABC):
    """
    Abstract base class for all processing layers.

    This class defines the interface that all processing layer implementations must follow.
    Processing layers are responsible for the core agent logic and workflow management,
    including interacting with language models to generate responses to user input.

    Attributes:
        None
    """

    @abstractmethod
    def process(self, user_input: Dict[str, Any]) -> str:
        """
        Process the user input and generate a response.

        This method should be implemented by subclasses to process the user input
        using the appropriate workflow and generate a response.

        Args:
            user_input (Dict[str, Any]): The user input, typically containing a 'text' key.

        Returns:
            str: The assistant's response.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        pass


class BasicChainingAgent(ProcessingLayer):
    """
    Processing layer that implements a basic prompt chaining workflow.

    This implementation uses a simple prompt chaining workflow to generate responses.
    It formats a prompt with the system prompt, conversation history, and user input,
    then sends it to a language model to generate a response.

    Attributes:
        memory (MemoryLayer): The memory layer to use for storing and retrieving conversation history.
        model_type (str): The type of model to query (e.g., 'ollama', 'openai').
        model_name (str): The name of the model to query.
        base_url (str): The base URL for the API.
        prompt_template_name (str): The name of the prompt template to use.
        prompt_templates (Dict[str, Any]): A dictionary of prompt templates.
        prompt_template (Dict[str, Any]): The selected prompt template.
        system_prompt (str): The system prompt to use.
    """

    def __init__(self, memory: MemoryLayer, config: Dict[str, Any]):
        """
        Initialize the basic chaining agent.

        Args:
            memory (MemoryLayer): The memory layer to use for storing and retrieving conversation history.
            config (Dict[str, Any]): Configuration dictionary containing settings for the agent.

        Note:
            The configuration dictionary should contain the following keys:
            - AGENT_1_TYPE: The type of model to query (e.g., 'ollama', 'openai').
            - AGENT_1_MODEL: The name of the model to query.
            - AGENT_1_BASE_URL: The base URL for the API.
            - PROMPT_TEMPLATE: The name of the prompt template to use.
            - SYSTEM_PROMPT: (Optional) The system prompt to use, overriding the template.
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

        This method loads prompt templates from a JSON file in the same directory.
        If the file does not exist or cannot be parsed, an empty dictionary is returned.

        Returns:
            Dict[str, Any]: A dictionary of prompt templates.

        Note:
            The prompt templates file should be named 'prompt_templates.json' and located
            in the same directory as this module.
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

        This method formats the conversation history as a string that can be included
        in the prompt sent to the language model.

        Args:
            history (List[Dict[str, Any]]): The conversation history.
                Each entry is a dictionary with 'user_input', 'assistant_response',
                and 'timestamp' keys.

        Returns:
            str: The formatted history as a string.

        Example:
            >>> history = [
            ...     {"user_input": {"text": "Hello"}, "assistant_response": "Hi there!", "timestamp": "2025-03-02T23:24:45.123456"},
            ...     {"user_input": {"text": "How are you?"}, "assistant_response": "I'm doing well, thanks!", "timestamp": "2025-03-02T23:24:46.123456"}
            ... ]
            >>> agent = BasicChainingAgent(memory, config)
            >>> agent._format_history(history)
            'User: Hello\\nAssistant: Hi there!\\n\\nUser: How are you?\\nAssistant: I\\'m doing well, thanks!'
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

        This method formats a prompt with the system prompt, conversation history,
        and user input, then sends it to a language model to generate a response.

        Args:
            user_input (Dict[str, Any]): The user input, typically containing a 'text' key.

        Returns:
            str: The assistant's response.

        Raises:
            Exception: If there is an error querying the language model.

        Example:
            >>> user_input = {"text": "What is the capital of France?"}
            >>> agent = BasicChainingAgent(memory, config)
            >>> response = agent.process(user_input)
            >>> response
            'The capital of France is Paris.'
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
            # Log the error and return a fallback response
            print(f"Error querying model: {str(e)}")
            response = f"I'm sorry, I encountered an error: {str(e)}"
            # TODO: Implement proper error handling and logging
            # TODO: Implement retry logic for transient errors

        return response


# TODO: Implement RoutingAgent for routing queries to different models based on content
# TODO: Implement OrchestratorWorkerAgent for complex tasks requiring multiple steps
# TODO: Implement EvaluatorOptimizerAgent for iterative response improvement
# TODO: Implement ParallelizationAgent for parallel processing of subtasks


def create_processing_layer(config: Dict[str, Any], memory: MemoryLayer) -> ProcessingLayer:
    """
    Create a processing layer based on the configuration.

    This factory function creates and returns an instance of the appropriate
    processing layer based on the configuration dictionary.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
            Should contain a 'PROCESSING_LAYER' key that specifies the type of processing layer to create.
            Additional keys may be required depending on the processing layer type.
        memory (MemoryLayer): The memory layer to use for storing and retrieving conversation history.

    Returns:
        ProcessingLayer: An instance of the appropriate processing layer.

    Raises:
        ValueError: If the processing layer type specified in the configuration is not supported.

    Example:
        >>> config = {"PROCESSING_LAYER": "basic_chaining"}
        >>> memory = InMemoryMemory()
        >>> processing_layer = create_processing_layer(config, memory)
        >>> isinstance(processing_layer, BasicChainingAgent)
        True
    """
    processing_layer_type = config.get("PROCESSING_LAYER", "basic_chaining")

    if processing_layer_type == "basic_chaining":
        return BasicChainingAgent(memory, config)
    else:
        raise ValueError(f"Unsupported processing layer type: {processing_layer_type}")