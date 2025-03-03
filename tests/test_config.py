"""
Unit tests for the configuration module.
"""

import sys
import os
import unittest
from unittest.mock import patch, mock_open

# Add the parent directory to sys.path to import layers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layers.config import load_config


class TestConfig(unittest.TestCase):
    """Test cases for the configuration module."""

    def test_load_config_default(self):
        """Test loading the default configuration."""
        # Mock the existence of the .env file
        with patch('os.path.exists', return_value=False):
            # Load the configuration
            config = load_config()

            # Check that the configuration contains the expected default values
            self.assertEqual(config["INPUT_LAYER"], "local_text")
            self.assertEqual(config["PROCESSING_LAYER"], "basic_chaining")
            self.assertEqual(config["AGENT_1_TYPE"], "ollama")
            self.assertEqual(config["AGENT_1_MODEL"], "mistralai/Mistral-7B-Instruct-v0.1")
            self.assertEqual(config["AGENT_1_BASE_URL"], "http://localhost:11434")
            self.assertEqual(config["MEMORY_LAYER"], "in_memory")
            self.assertEqual(config["OUTPUT_LAYER"], "local_text")

    def test_load_config_custom(self):
        """Test loading a custom configuration."""
        # Mock the existence of the .env file
        with patch('os.path.exists', return_value=True):
            # Mock the dotenv.load_dotenv function
            with patch('dotenv.load_dotenv'):
                # Mock the os.getenv function to return custom values
                with patch('os.getenv') as mock_getenv:
                    # Set up the mock to return custom values for specific keys
                    def mock_getenv_side_effect(key, default=None):
                        custom_values = {
                            "INPUT_LAYER": "custom_input",
                            "PROCESSING_LAYER": "custom_processing",
                            "AGENT_1_TYPE": "custom_agent",
                            "AGENT_1_MODEL": "custom_model",
                            "AGENT_1_BASE_URL": "custom_url",
                            "MEMORY_LAYER": "custom_memory",
                            "OUTPUT_LAYER": "custom_output"
                        }
                        return custom_values.get(key, default)

                    mock_getenv.side_effect = mock_getenv_side_effect

                    # Load the configuration
                    config = load_config()

                    # Check that the configuration contains the expected custom values
                    self.assertEqual(config["INPUT_LAYER"], "custom_input")
                    self.assertEqual(config["PROCESSING_LAYER"], "custom_processing")
                    self.assertEqual(config["AGENT_1_TYPE"], "custom_agent")
                    self.assertEqual(config["AGENT_1_MODEL"], "custom_model")
                    self.assertEqual(config["AGENT_1_BASE_URL"], "custom_url")
                    self.assertEqual(config["MEMORY_LAYER"], "custom_memory")
                    self.assertEqual(config["OUTPUT_LAYER"], "custom_output")


if __name__ == "__main__":
    unittest.main()