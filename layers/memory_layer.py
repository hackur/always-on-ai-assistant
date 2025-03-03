"""
Memory Layer for the Always-On AI Assistant.
This module handles conversation history and state.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime


class MemoryLayer(ABC):
    """Base class for all memory layers."""

    @abstractmethod
    def add_entry(self, user_input: Dict[str, Any], assistant_response: str) -> None:
        """
        Add a new entry to the conversation history.

        Args:
            user_input (Dict[str, Any]): The user input.
            assistant_response (str): The assistant's response.
        """
        pass

    @abstractmethod
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history.

        Args:
            limit (Optional[int]): Maximum number of entries to return.
                If None, return all entries.

        Returns:
            List[Dict[str, Any]]: A list of conversation entries.
                Each entry is a dictionary with 'user_input', 'assistant_response',
                and 'timestamp' keys.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the conversation history."""
        pass


class InMemoryMemory(MemoryLayer):
    """Memory layer that stores conversation history in memory."""

    def __init__(self):
        """Initialize the in-memory storage."""
        self.history = []

    def add_entry(self, user_input: Dict[str, Any], assistant_response: str) -> None:
        """
        Add a new entry to the conversation history.

        Args:
            user_input (Dict[str, Any]): The user input.
            assistant_response (str): The assistant's response.
        """
        self.history.append({
            "user_input": user_input,
            "assistant_response": assistant_response,
            "timestamp": datetime.now().isoformat()
        })

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history.

        Args:
            limit (Optional[int]): Maximum number of entries to return.
                If None, return all entries.

        Returns:
            List[Dict[str, Any]]: A list of conversation entries.
        """
        if limit is None:
            return self.history
        return self.history[-limit:]

    def clear(self) -> None:
        """Clear the conversation history."""
        self.history = []


class JsonFileMemory(MemoryLayer):
    """Memory layer that stores conversation history in a JSON file."""

    def __init__(self, file_path: str = "conversation_history.json"):
        """
        Initialize the JSON file storage.

        Args:
            file_path (str): Path to the JSON file.
        """
        self.file_path = file_path
        self.history = []

        # Load existing history if file exists
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                # If the file is corrupted, start with an empty history
                self.history = []

    def add_entry(self, user_input: Dict[str, Any], assistant_response: str) -> None:
        """
        Add a new entry to the conversation history and save to file.

        Args:
            user_input (Dict[str, Any]): The user input.
            assistant_response (str): The assistant's response.
        """
        self.history.append({
            "user_input": user_input,
            "assistant_response": assistant_response,
            "timestamp": datetime.now().isoformat()
        })

        # Save to file
        with open(self.file_path, "w") as f:
            json.dump(self.history, f, indent=2)

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history.

        Args:
            limit (Optional[int]): Maximum number of entries to return.
                If None, return all entries.

        Returns:
            List[Dict[str, Any]]: A list of conversation entries.
        """
        if limit is None:
            return self.history
        return self.history[-limit:]

    def clear(self) -> None:
        """Clear the conversation history and the file."""
        self.history = []

        # Save empty history to file
        with open(self.file_path, "w") as f:
            json.dump(self.history, f, indent=2)


# Factory function to create the appropriate memory layer based on configuration
def create_memory_layer(config: Dict[str, Any]) -> MemoryLayer:
    """
    Create a memory layer based on the configuration.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
            Should contain a 'MEMORY_LAYER' key.

    Returns:
        MemoryLayer: An instance of the appropriate memory layer.

    Raises:
        ValueError: If the memory layer type is not supported.
    """
    memory_layer_type = config.get("MEMORY_LAYER", "in_memory")

    if memory_layer_type == "in_memory":
        return InMemoryMemory()
    elif memory_layer_type == "json_file":
        file_path = config.get("MEMORY_FILE_PATH", "conversation_history.json")
        return JsonFileMemory(file_path)
    else:
        raise ValueError(f"Unsupported memory layer type: {memory_layer_type}")