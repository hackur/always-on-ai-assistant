#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the query_helper module.

This script tests the functionality of the query_helper module,
which provides integration with local LLMs via LM Studio and Ollama.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import the modules package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the test helper module
from test_helper import setup_paths, print_debug_info

# Set up paths
paths = setup_paths()
print_debug_info(paths)

# Try to import the query_helper module
try:
    from modules.query_helper import (
        get_available_models,
        is_server_running,
        query_model,
        list_available_models,
        QUERY_COMMON_AVAILABLE
    )
    QUERY_HELPER_AVAILABLE = True
except ImportError as e:
    print(f"Error importing query_helper: {e}")
    print("Make sure the query_helper.py file exists in the modules directory.")
    QUERY_HELPER_AVAILABLE = False


@unittest.skipIf(not QUERY_HELPER_AVAILABLE, "query_helper module not available")
class TestQueryHelper(unittest.TestCase):
    """Test cases for the query_helper module."""

    def test_is_server_running(self):
        """Test the is_server_running function."""
        # We'll mock the check_server function to avoid actual network calls
        if QUERY_COMMON_AVAILABLE:
            with patch('query_common.check_server') as mock_check_server:
                # Test with server running
                mock_check_server.return_value = True
                self.assertTrue(is_server_running("lmstudio"))
                mock_check_server.assert_called_with("lmstudio")

                # Test with server not running
                mock_check_server.return_value = False
                self.assertFalse(is_server_running("ollama"))
                mock_check_server.assert_called_with("ollama")
        else:
            # If query_common is not available, we'll mock subprocess.run
            with patch('subprocess.run') as mock_run:
                # Test with server running
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "Available LM Studio models:"
                mock_run.return_value = mock_result

                self.assertTrue(is_server_running("lmstudio"))
                mock_run.assert_called()

                # Test with server not running
                mock_result.returncode = 1
                mock_run.return_value = mock_result

                self.assertFalse(is_server_running("lmstudio"))
                mock_run.assert_called()

    def test_get_available_models(self):
        """Test the get_available_models function."""
        # We'll mock the get_server_models function to avoid actual network calls
        if QUERY_COMMON_AVAILABLE:
            with patch('query_common.get_server_models') as mock_get_server_models:
                # Test with LM Studio
                mock_get_server_models.return_value = ["model1.py", "model2.py"]
                models = get_available_models("lmstudio")
                self.assertEqual(models, ["model1.py", "model2.py"])
                mock_get_server_models.assert_called_with("lmstudio")

                # Test with Ollama
                mock_get_server_models.return_value = ["llama3", "phi3"]
                models = get_available_models("ollama")
                self.assertEqual(models, ["llama3", "phi3"])
                mock_get_server_models.assert_called_with("ollama")
        else:
            # If query_common is not available, we'll mock subprocess.run
            with patch('subprocess.run') as mock_run:
                # Test with LM Studio
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "Available LM Studio models:\n- model1.py\n- model2.py"
                mock_run.return_value = mock_result

                models = get_available_models("lmstudio")
                self.assertEqual(models, ["model1.py", "model2.py"])
                mock_run.assert_called()

                # Test with Ollama
                mock_result.stdout = "Available Ollama models:\n- llama3\n- phi3"
                mock_run.return_value = mock_result

                models = get_available_models("ollama")
                self.assertEqual(models, ["llama3", "phi3"])
                mock_run.assert_called()

    def test_query_model(self):
        """Test the query_model function."""
        # We'll mock the run_query_common function to avoid actual network calls
        if QUERY_COMMON_AVAILABLE:
            with patch('query_common.run_query') as mock_run_query:
                with patch('modules.query_helper.is_server_running') as mock_is_server_running:
                    # Test with server running
                    mock_is_server_running.return_value = True
                    mock_run_query.return_value = "/tmp/output.txt"

                    # Mock the open function to return a file-like object
                    mock_file = MagicMock()
                    mock_file.__enter__.return_value.read.return_value = "Test response"

                    with patch('builtins.open', return_value=mock_file):
                        response = query_model(
                            model_type="ollama",
                            model_name="llama3",
                            prompt="Test prompt",
                            prompt_type="General Instruction Following",
                            verbose=True
                        )

                        self.assertEqual(response, "Test response")
                        mock_run_query.assert_called_with(
                            model="llama3",
                            query="Test prompt",
                            prompt_type="General Instruction Following",
                            output_dir=unittest.mock.ANY,
                            server_type="ollama",
                            api_url=None
                        )

                    # Test with server not running
                    mock_is_server_running.return_value = False

                    response = query_model(
                        model_type="lmstudio",
                        model_name="model1.py",
                        prompt="Test prompt",
                        verbose=True
                    )

                    self.assertTrue("Error" in response)
                    mock_run_query.assert_not_called()
        else:
            # If query_common is not available, we'll mock subprocess.run
            with patch('subprocess.run') as mock_run:
                with patch('modules.query_helper.is_server_running') as mock_is_server_running:
                    with patch('os.path.getmtime') as mock_getmtime:
                        with patch('os.listdir') as mock_listdir:
                            # Test with server running
                            mock_is_server_running.return_value = True
                            mock_result = MagicMock()
                            mock_result.returncode = 0
                            mock_run.return_value = mock_result

                            # Mock the listdir function to return a list of files
                            mock_listdir.return_value = ["output_query_result.txt"]

                            # Mock the getmtime function to return a timestamp
                            mock_getmtime.return_value = 123456789

                            # Mock the open function to return a file-like object
                            mock_file = MagicMock()
                            mock_file.__enter__.return_value.read.return_value = "Test response"

                            with patch('builtins.open', return_value=mock_file):
                                response = query_model(
                                    model_type="ollama",
                                    model_name="llama3",
                                    prompt="Test prompt",
                                    prompt_type="General Instruction Following",
                                    verbose=True
                                )

                                self.assertEqual(response, "Test response")
                                mock_run.assert_called()

                            # Test with server not running
                            mock_is_server_running.return_value = False

                            response = query_model(
                                model_type="lmstudio",
                                model_name="model1.py",
                                prompt="Test prompt",
                                verbose=True
                            )

                            self.assertTrue("Error" in response)
                            mock_run.assert_not_called()


def run_live_test():
    """Run a live test of the query_helper module."""
    print("\n===== Live Test of Query Helper =====\n")

    # Check if servers are running
    print("Checking if servers are running...")
    lmstudio_running = is_server_running("lmstudio")
    ollama_running = is_server_running("ollama")

    print(f"LM Studio running: {lmstudio_running}")
    print(f"Ollama running: {ollama_running}")

    # List available models
    print("\nListing available models...")
    models = list_available_models(verbose=True)

    if not models:
        print("No models available. Make sure at least one server is running.")
        return

    # Prefer Ollama over LM Studio for the live test
    if "ollama" in models:
        server_type = "ollama"
        model_name = models["ollama"][0]  # Use the first Ollama model
    else:
        server_type = next(iter(models.keys()))
        model_name = models[server_type][0]

    print(f"\nSelected server: {server_type}")
    print(f"Selected model: {model_name}")

    # Query the model
    print("\nQuerying the model...")
    response = query_model(
        model_type=server_type,
        model_name=model_name,
        prompt="What is the capital of France?",
        verbose=True
    )

    print("\nResponse:")
    print("-" * 40)
    print(response)
    print("-" * 40)


if __name__ == "__main__":
    # Check if we should run the live test
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        run_live_test()
    else:
        unittest.main()