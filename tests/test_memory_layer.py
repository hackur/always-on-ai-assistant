"""
Unit tests for the memory layer.
"""

import sys
import os
import unittest
import tempfile
import json
from datetime import datetime

# Add the parent directory to sys.path to import layers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layers.memory_layer import InMemoryMemory, JsonFileMemory, create_memory_layer


class TestMemoryLayer(unittest.TestCase):
    """Test cases for the memory layer."""

    def test_in_memory_memory(self):
        """Test the InMemoryMemory class."""
        # Create an InMemoryMemory instance
        memory = InMemoryMemory()

        # Check that the history is initially empty
        self.assertEqual(memory.get_history(), [])

        # Add an entry
        user_input = {"text": "Hello"}
        assistant_response = "Hi there!"
        memory.add_entry(user_input, assistant_response)

        # Check that the history contains the entry
        history = memory.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["user_input"], user_input)
        self.assertEqual(history[0]["assistant_response"], assistant_response)

        # Add another entry
        user_input2 = {"text": "How are you?"}
        assistant_response2 = "I'm doing well, thank you!"
        memory.add_entry(user_input2, assistant_response2)

        # Check that the history contains both entries
        history = memory.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[1]["user_input"], user_input2)
        self.assertEqual(history[1]["assistant_response"], assistant_response2)

        # Test the limit parameter
        limited_history = memory.get_history(limit=1)
        self.assertEqual(len(limited_history), 1)
        self.assertEqual(limited_history[0]["user_input"], user_input2)
        self.assertEqual(limited_history[0]["assistant_response"], assistant_response2)

        # Clear the history
        memory.clear()

        # Check that the history is empty
        self.assertEqual(memory.get_history(), [])

    def test_json_file_memory(self):
        """Test the JsonFileMemory class."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Create a JsonFileMemory instance
            memory = JsonFileMemory(temp_file_path)

            # Check that the history is initially empty
            self.assertEqual(memory.get_history(), [])

            # Add an entry
            user_input = {"text": "Hello"}
            assistant_response = "Hi there!"
            memory.add_entry(user_input, assistant_response)

            # Check that the history contains the entry
            history = memory.get_history()
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["user_input"], user_input)
            self.assertEqual(history[0]["assistant_response"], assistant_response)

            # Check that the file contains the entry
            with open(temp_file_path, "r") as f:
                file_content = json.load(f)
            self.assertEqual(len(file_content), 1)
            self.assertEqual(file_content[0]["user_input"], user_input)
            self.assertEqual(file_content[0]["assistant_response"], assistant_response)

            # Clear the history
            memory.clear()

            # Check that the history is empty
            self.assertEqual(memory.get_history(), [])

            # Check that the file is empty
            with open(temp_file_path, "r") as f:
                file_content = json.load(f)
            self.assertEqual(file_content, [])

        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_create_memory_layer_default(self):
        """Test the create_memory_layer function with default configuration."""
        # Create a memory layer with an empty configuration
        memory = create_memory_layer({})

        # Check that the memory is an InMemoryMemory instance
        self.assertIsInstance(memory, InMemoryMemory)

    def test_create_memory_layer_in_memory(self):
        """Test the create_memory_layer function with in-memory configuration."""
        # Create a memory layer with an in-memory configuration
        memory = create_memory_layer({"MEMORY_LAYER": "in_memory"})

        # Check that the memory is an InMemoryMemory instance
        self.assertIsInstance(memory, InMemoryMemory)

    def test_create_memory_layer_json_file(self):
        """Test the create_memory_layer function with JSON file configuration."""
        # Create a memory layer with a JSON file configuration
        memory = create_memory_layer({
            "MEMORY_LAYER": "json_file",
            "MEMORY_FILE_PATH": "test_conversation_history.json"
        })

        # Check that the memory is a JsonFileMemory instance
        self.assertIsInstance(memory, JsonFileMemory)
        self.assertEqual(memory.file_path, "test_conversation_history.json")

        # Clean up the file if it was created
        if os.path.exists("test_conversation_history.json"):
            os.unlink("test_conversation_history.json")

    def test_create_memory_layer_invalid(self):
        """Test the create_memory_layer function with an invalid configuration."""
        # Try to create a memory layer with an invalid configuration
        with self.assertRaises(ValueError):
            create_memory_layer({"MEMORY_LAYER": "invalid_type"})


if __name__ == "__main__":
    unittest.main()