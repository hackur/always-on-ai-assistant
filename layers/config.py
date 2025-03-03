"""
Configuration module for the Always-On AI Assistant.
This module handles loading and managing configuration settings.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv


def load_config(env_file: str = ".env.local") -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    Args:
        env_file (str): Path to the .env file.

    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the .env file
    env_path = os.path.join(current_dir, env_file)

    # Load environment variables from .env file
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        print(f"Warning: Environment file {env_path} not found.")

    # Create configuration dictionary
    config = {
        # Input Layer
        "INPUT_LAYER": os.getenv("INPUT_LAYER", "local_text"),

        # Processing Layer
        "PROCESSING_LAYER": os.getenv("PROCESSING_LAYER", "basic_chaining"),

        # Agent Configuration
        "AGENT_1_TYPE": os.getenv("AGENT_1_TYPE", "ollama"),
        "AGENT_1_MODEL": os.getenv("AGENT_1_MODEL", "mistralai/Mistral-7B-Instruct-v0.1"),
        "AGENT_1_BASE_URL": os.getenv("AGENT_1_BASE_URL", "http://localhost:11434"),

        # Prompt Configuration
        "PROMPT_TEMPLATE": os.getenv("PROMPT_TEMPLATE", "basic_chaining"),
        "SYSTEM_PROMPT": os.getenv("SYSTEM_PROMPT",
            "You are a helpful, friendly AI assistant. Answer the user's questions concisely and accurately."),

        # Memory Layer
        "MEMORY_LAYER": os.getenv("MEMORY_LAYER", "in_memory"),
        "MEMORY_FILE_PATH": os.getenv("MEMORY_FILE_PATH", "conversation_history.json"),

        # Output Layer
        "OUTPUT_LAYER": os.getenv("OUTPUT_LAYER", "local_text"),
        "OUTPUT_COLOR": os.getenv("OUTPUT_COLOR", "blue"),
    }

    return config