#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Layer for the Always-On AI Assistant.

This module defines the memory layer interface and implementations for the assistant.
The memory layer is responsible for storing and retrieving conversation history and
other state information that needs to persist across interactions.

Classes:
    MemoryLayer: Abstract base class for all memory layers.
    InMemoryMemory: Implementation that stores conversation history in memory.
    JsonFileMemory: Implementation that stores conversation history in a JSON file.

Functions:
    create_memory_layer: Factory function to create the appropriate memory layer.

Typical usage example:
    config = load_config()
    memory_layer = create_memory_layer(config)
    memory_layer.add_entry(user_input, assistant_response)
    history = memory_layer.get_history()
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime


class MemoryLayer(ABC):
    """
    Abstract base class for all memory layers.

    This class defines the interface that all memory layer implementations must follow.
    Memory layers are responsible for storing and retrieving conversation history and
    other state information that needs to persist across interactions.

    Attributes:
        None
    """

    @abstractmethod
    def add_entry(self, user_input: Dict[str, Any], assistant_response: str) -> None:
        """
        Add a new entry to the conversation history.

        This method should be implemented by subclasses to store a new conversation
        entry in the appropriate storage medium.

        Args:
            user_input (Dict[str, Any]): The user input, typically containing a 'text' key.
            assistant_response (str): The assistant's response text.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        pass

    @abstractmethod
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history.

        This method should be implemented by subclasses to retrieve the conversation
        history from the appropriate storage medium.

        Args:
            limit (Optional[int]): Maximum number of entries to return.
                If None, return all entries.

        Returns:
            List[Dict[str, Any]]: A list of conversation entries.
                Each entry is a dictionary with 'user_input', 'assistant_response',
                and 'timestamp' keys.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the conversation history.

        This method should be implemented by subclasses to clear all conversation
        history from the appropriate storage medium.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        pass


class InMemoryMemory(MemoryLayer):
    """
    Memory layer that stores conversation history in memory.

    This implementation stores the conversation history in a list in memory.
    The history is not persisted across program restarts.

    Attributes:
        history (List[Dict[str, Any]]): The conversation history.
    """

    def __init__(self):
        """
        Initialize the in-memory storage.

        Creates an empty list to store the conversation history.
        """
        self.history = []

    def add_entry(self, user_input: Dict[str, Any], assistant_response: str) -> None:
        """
        Add a new entry to the conversation history.

        Args:
            user_input (Dict[str, Any]): The user input, typically containing a 'text' key.
            assistant_response (str): The assistant's response text.

        Example:
            >>> memory = InMemoryMemory()
            >>> memory.add_entry({"text": "Hello"}, "Hi there!")
            >>> memory.get_history()
            [{'user_input': {'text': 'Hello'}, 'assistant_response': 'Hi there!', 'timestamp': '2025-03-02T23:23:45.123456'}]
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
                Each entry is a dictionary with 'user_input', 'assistant_response',
                and 'timestamp' keys.

        Example:
            >>> memory = InMemoryMemory()
            >>> memory.add_entry({"text": "Hello"}, "Hi there!")
            >>> memory.add_entry({"text": "How are you?"}, "I'm doing well, thanks!")
            >>> memory.get_history(limit=1)  # Get only the most recent entry
            [{'user_input': {'text': 'How are you?'}, 'assistant_response': "I'm doing well, thanks!", 'timestamp': '2025-03-02T23:23:46.123456'}]
        """
        if limit is None:
            return self.history
        return self.history[-limit:]

    def clear(self) -> None:
        """
        Clear the conversation history.

        Resets the history list to an empty list.

        Example:
            >>> memory = InMemoryMemory()
            >>> memory.add_entry({"text": "Hello"}, "Hi there!")
            >>> memory.clear()
            >>> memory.get_history()
            []
        """
        self.history = []


class JsonFileMemory(MemoryLayer):
    """
    Memory layer that stores conversation history in a JSON file.

    This implementation stores the conversation history in a JSON file on disk.
    The history is persisted across program restarts.

    Attributes:
        file_path (str): Path to the JSON file.
        history (List[Dict[str, Any]]): The conversation history.
    """

    def __init__(self, file_path: str = "conversation_history.json"):
        """
        Initialize the JSON file storage.

        Args:
            file_path (str, optional): Path to the JSON file.
                Defaults to "conversation_history.json".

        Note:
            If the file exists, the conversation history is loaded from it.
            If the file does not exist or is corrupted, an empty history is created.
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
            user_input (Dict[str, Any]): The user input, typically containing a 'text' key.
            assistant_response (str): The assistant's response text.

        Note:
            This method updates both the in-memory history and the JSON file on disk.

        Raises:
            IOError: If there is an error writing to the file.
        """
        self.history.append({
            "user_input": user_input,
            "assistant_response": assistant_response,
            "timestamp": datetime.now().isoformat()
        })

        # Save to file
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            # Log the error but don't crash the program
            print(f"Error saving conversation history to file: {e}")
            # TODO: Implement proper error handling and logging

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
        if limit is None:
            return self.history
        return self.history[-limit:]

    def clear(self) -> None:
        """
        Clear the conversation history and the file.

        This method clears both the in-memory history and the JSON file on disk.

        Raises:
            IOError: If there is an error writing to the file.
        """
        self.history = []

        # Save empty history to file
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            # Log the error but don't crash the program
            print(f"Error saving empty conversation history to file: {e}")
            # TODO: Implement proper error handling and logging


# TODO: Implement VectorStoreMemory for semantic search capabilities
# TODO: Implement SQLiteMemory for more robust storage with query capabilities
# TODO: Implement RedisMemory for distributed memory with expiration capabilities


def create_memory_layer(config: Dict[str, Any]) -> MemoryLayer:
    """
    Create a memory layer based on the configuration.

    This factory function creates and returns an instance of the appropriate
    memory layer based on the configuration dictionary.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
            Should contain a 'MEMORY_LAYER' key that specifies the type of memory layer to create.
            Additional keys may be required depending on the memory layer type.

    Returns:
        MemoryLayer: An instance of the appropriate memory layer.

    Raises:
        ValueError: If the memory layer type specified in the configuration is not supported.

    Example:
        >>> config = {"MEMORY_LAYER": "in_memory"}
        >>> memory_layer = create_memory_layer(config)
        >>> isinstance(memory_layer, InMemoryMemory)
        True
    """
    memory_layer_type = config.get("MEMORY_LAYER", "in_memory")

    if memory_layer_type == "in_memory":
        return InMemoryMemory()
    elif memory_layer_type == "json_file":
        file_path = config.get("MEMORY_FILE_PATH", "conversation_history.json")
        return JsonFileMemory(file_path)
    else:
        raise ValueError(f"Unsupported memory layer type: {memory_layer_type}")