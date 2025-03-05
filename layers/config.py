#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for the Always-On AI Assistant.

This module handles loading and managing configuration settings for the assistant.
It provides functions to load configuration from environment variables and .env files,
and creates a configuration dictionary that can be used by other components.

Functions:
    load_config: Load configuration from environment variables and .env files.

Typical usage example:
    config = load_config()
    input_layer = create_input_layer(config)
    memory_layer = create_memory_layer(config)
    processing_layer = create_processing_layer(config, memory_layer)
    output_layer = create_output_layer(config)
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv


def load_config(env_file: str = ".env.local") -> Dict[str, Any]:
    """
    Load configuration from environment variables and .env files.

    This function loads configuration settings from environment variables and .env files.
    It first tries to load variables from the specified .env file, then creates a
    configuration dictionary with default values for any settings that are not defined.

    Args:
        env_file (str, optional): Path to the .env file, relative to the current directory.
            Defaults to ".env.local".

    Returns:
        Dict[str, Any]: Configuration dictionary containing all settings.
            The dictionary includes settings for the input layer, processing layer,
            agent configuration, prompt configuration, memory layer, and output layer.

    Note:
        If the specified .env file does not exist, a warning is printed but the function
        continues with default values.

    Example:
        >>> config = load_config()
        >>> config["INPUT_LAYER"]
        'local_text'
    """
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the .env file
    env_path = os.path.join(current_dir, env_file)

    # Load environment variables from .env file
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        print(f"Warning: Environment file {env_path} not found. Using default configuration.")

    # Create configuration dictionary with default values
    config = {
        # Input Layer Configuration
        "INPUT_LAYER": os.getenv("INPUT_LAYER", "local_text"),
        "INPUT_PROMPT": os.getenv("INPUT_PROMPT", "You: "),

        # Processing Layer Configuration
        "PROCESSING_LAYER": os.getenv("PROCESSING_LAYER", "basic_chaining"),

        # Agent Configuration
        "AGENT_1_TYPE": os.getenv("AGENT_1_TYPE", "ollama"),
        "AGENT_1_MODEL": os.getenv("AGENT_1_MODEL", "mistralai/Mistral-7B-Instruct-v0.1"),
        "AGENT_1_BASE_URL": os.getenv("AGENT_1_BASE_URL", "http://localhost:11434"),

        # Prompt Configuration
        "PROMPT_TEMPLATE": os.getenv("PROMPT_TEMPLATE", "basic_chaining"),
        "SYSTEM_PROMPT": os.getenv("SYSTEM_PROMPT",
            "You are a helpful, friendly AI assistant. Answer the user's questions concisely and accurately."),

        # Memory Layer Configuration
        "MEMORY_LAYER": os.getenv("MEMORY_LAYER", "in_memory"),
        "MEMORY_FILE_PATH": os.getenv("MEMORY_FILE_PATH", "conversation_history.json"),

        # Output Layer Configuration
        "OUTPUT_LAYER": os.getenv("OUTPUT_LAYER", "local_text"),
        "OUTPUT_COLOR": os.getenv("OUTPUT_COLOR", "blue"),
        "OUTPUT_PREFIX": os.getenv("OUTPUT_PREFIX", "Assistant: "),
    }

    return config


# TODO: Add support for loading configuration from JSON or YAML files
# TODO: Add validation for configuration values
# TODO: Add support for configuration profiles (e.g., development, production)
# TODO: Add support for command-line overrides of configuration values