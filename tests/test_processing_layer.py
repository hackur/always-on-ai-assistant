"""
Unit tests for the processing layer.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json

# Add the parent directory to sys.path to import layers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the query_helper module
sys.modules['query_helper'] = MagicMock()

from layers.processing_layer import BasicChainingAgent, create_processing_layer
from layers.memory_layer import InMemoryMemory


class TestProcessingLayer(unittest.TestCase):
    """Test cases for the processing layer."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary prompt templates file
        self.temp_dir = os.path.dirname(os.path.abspath(__file__))
        self.templates_path = os.path.join(self.temp_dir, "prompt_templates.json")

        # Create a simple prompt templates dictionary
        self.templates = {
            "basic_chaining": {
                "system": "You are a test assistant.",
                "user_prefix": "User: ",
                "assistant_prefix": "Assistant: ",
                "format": "{system}\n\n{history}\n\n{user_prefix}{user_input}\n{assistant_prefix}"
            }
        }

        # Write the templates to the file
        with open(self.templates_path, "w") as f:
            json.dump(self.templates, f)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary prompt templates file
        if os.path.exists(self.templates_path):
            os.unlink(self.templates_path)

    def test_basic_chaining_agent(self):
        """Test the BasicChainingAgent class."""
        # Create a memory layer
        memory = InMemoryMemory()

        # Create a configuration
        config = {
            "AGENT_1_TYPE": "test_type",
            "AGENT_1_MODEL": "test_model",
            "AGENT_1_BASE_URL": "test_url",
            "PROMPT_TEMPLATE": "basic_chaining"
        }

        # Mock the _load_prompt_templates method to return our test templates
        with patch.object(BasicChainingAgent, '_load_prompt_templates', return_value=self.templates):
            # Create a BasicChainingAgent instance
            agent = BasicChainingAgent(memory, config)

            # Check that the agent has the expected attributes
            self.assertEqual(agent.model_type, "test_type")
            self.assertEqual(agent.model_name, "test_model")
            self.assertEqual(agent.base_url, "test_url")
            self.assertEqual(agent.prompt_template_name, "basic_chaining")
            self.assertEqual(agent.system_prompt, "You are a test assistant.")

    def test_process(self):
        """Test the process method."""
        # Create a memory layer
        memory = InMemoryMemory()

        # Add some history
        memory.add_entry({"text": "Hello"}, "Hi there!")

        # Create a configuration
        config = {
            "AGENT_1_TYPE": "test_type",
            "AGENT_1_MODEL": "test_model",
            "AGENT_1_BASE_URL": "test_url",
            "PROMPT_TEMPLATE": "basic_chaining"
        }

        # Mock the _load_prompt_templates method to return our test templates
        with patch.object(BasicChainingAgent, '_load_prompt_templates', return_value=self.templates):
            # Create a BasicChainingAgent instance
            agent = BasicChainingAgent(memory, config)

            # Mock the query_model function
            with patch('layers.processing_layer.query_model', return_value="Test response") as mock_query:
                # Process a user input
                response = agent.process({"text": "How are you?"})

                # Check that the response is as expected
                self.assertEqual(response, "Test response")

                # Check that query_model was called with the expected arguments
                mock_query.assert_called_once()
                args, kwargs = mock_query.call_args
                self.assertEqual(kwargs["model_type"], "test_type")
                self.assertEqual(kwargs["model_name"], "test_model")
                self.assertEqual(kwargs["base_url"], "test_url")

                # Check that the prompt contains the expected elements
                prompt = kwargs["prompt"]
                self.assertIn("You are a test assistant.", prompt)
                self.assertIn("User: Hello", prompt)
                self.assertIn("Assistant: Hi there!", prompt)
                self.assertIn("User: How are you?", prompt)

    def test_create_processing_layer(self):
        """Test the create_processing_layer function."""
        # Create a memory layer
        memory = InMemoryMemory()

        # Create a configuration
        config = {
            "PROCESSING_LAYER": "basic_chaining",
            "AGENT_1_TYPE": "test_type",
            "AGENT_1_MODEL": "test_model",
            "AGENT_1_BASE_URL": "test_url"
        }

        # Mock the BasicChainingAgent constructor
        with patch('layers.processing_layer.BasicChainingAgent') as mock_agent:
            # Create a processing layer
            create_processing_layer(config, memory)

            # Check that BasicChainingAgent was called with the expected arguments
            mock_agent.assert_called_once_with(memory, config)

    def test_create_processing_layer_invalid(self):
        """Test the create_processing_layer function with an invalid configuration."""
        # Create a memory layer
        memory = InMemoryMemory()

        # Create an invalid configuration
        config = {
            "PROCESSING_LAYER": "invalid_type"
        }

        # Try to create a processing layer with an invalid configuration
        with self.assertRaises(ValueError):
            create_processing_layer(config, memory)


if __name__ == "__main__":
    unittest.main()