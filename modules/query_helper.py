#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Helper Module for the Always-On AI Assistant.

This module provides functions to query local LLMs using the query.py script
from the servers directory. It supports both LM Studio and Ollama models.
"""

import os
import sys
import json
import subprocess
import tempfile
from typing import Dict, Any, Optional, List, Union

# Add the servers directory to sys.path to import query_common
SERVERS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'servers'))
if SERVERS_DIR not in sys.path:
    sys.path.append(SERVERS_DIR)

# Try to import query_common
try:
    from query_common import (
        check_server,
        get_server_models,
        run_query as run_query_common
    )
    QUERY_COMMON_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import query_common: {e}")
    print("Falling back to subprocess implementation.")
    QUERY_COMMON_AVAILABLE = False


def get_available_models(server_type: str = "lmstudio") -> List[str]:
    """
    Get a list of available models from the specified server.

    Args:
        server_type (str): Type of server to check ("lmstudio" or "ollama")

    Returns:
        List[str]: List of available models
    """
    if QUERY_COMMON_AVAILABLE:
        return get_server_models(server_type)
    else:
        # Fallback implementation using subprocess
        try:
            result = subprocess.run(
                ["python", os.path.join(SERVERS_DIR, "query.py"), "--server", server_type, "--list"],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse the output to extract model names
            models = []
            for line in result.stdout.split('\n'):
                if line.strip().startswith('- '):
                    models.append(line.strip()[2:].split(' ')[0])

            return models
        except subprocess.CalledProcessError as e:
            print(f"Error getting models: {e}")
            return []


def is_server_running(server_type: str = "lmstudio") -> bool:
    """
    Check if the specified server is running.

    Args:
        server_type (str): Type of server to check ("lmstudio" or "ollama")

    Returns:
        bool: True if server is running, False otherwise
    """
    if QUERY_COMMON_AVAILABLE:
        return check_server(server_type)
    else:
        # Fallback implementation using subprocess
        try:
            result = subprocess.run(
                ["python", os.path.join(SERVERS_DIR, "query.py"), "--server", server_type, "--list"],
                capture_output=True,
                text=True
            )

            # If the command succeeded and returned models, the server is running
            return result.returncode == 0 and "Available" in result.stdout
        except Exception:
            return False


def query_model(
    model_type: str = "ollama",
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.1",
    prompt: str = "",
    prompt_type: str = "General Instruction Following",
    base_url: Optional[str] = None,
    verbose: bool = False
) -> str:
    """
    Query a model with the given prompt.

    Args:
        model_type (str): Type of model to use ("lmstudio" or "ollama")
        model_name (str): Name of the model to use
        prompt (str): Prompt to send to the model
        prompt_type (str): Type of prompt to use
        base_url (str, optional): Base URL for the API
        verbose (bool): Whether to print verbose output

    Returns:
        str: Model response
    """
    if verbose:
        print(f"Querying {model_type} model {model_name}")
        print(f"Prompt type: {prompt_type}")
        print(f"Base URL: {base_url}")

    # Check if server is running
    if not is_server_running(model_type):
        error_msg = f"Error: {model_type.capitalize()} server is not running. Please start it and try again."
        print(error_msg)
        return error_msg

    # Create a temporary file to store the output
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
        temp_path = temp_file.name

    try:
        if QUERY_COMMON_AVAILABLE:
            # Use the imported run_query function
            output_file = run_query_common(
                model=model_name,
                query=prompt,
                prompt_type=prompt_type,
                output_dir=os.path.dirname(temp_path),
                server_type=model_type,
                api_url=base_url
            )

            # Read the output file
            if output_file and os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    response = f.read()
                return response
            else:
                return "Error: Failed to query model."
        else:
            # Fallback implementation using subprocess
            cmd = [
                "python",
                os.path.join(SERVERS_DIR, "query.py"),
                "--server", model_type,
                "--prompt-type", prompt_type,
                "--output-dir", os.path.dirname(temp_path),
                model_name,
                prompt
            ]

            if verbose:
                print(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Find the output file in the output directory
                output_files = [f for f in os.listdir(os.path.dirname(temp_path))
                               if f.endswith('_query_result.txt') and os.path.getmtime(os.path.join(os.path.dirname(temp_path), f)) > os.path.getmtime(temp_path)]

                if output_files:
                    # Get the most recent output file
                    output_file = os.path.join(os.path.dirname(temp_path), sorted(output_files)[-1])
                    with open(output_file, 'r') as f:
                        response = f.read()
                    return response
                else:
                    return "Error: Output file not found."
            else:
                error_msg = f"Error: Command failed with exit code {result.returncode}.\n{result.stderr}"
                print(error_msg)
                return error_msg
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def list_available_models(verbose: bool = False) -> Dict[str, List[str]]:
    """
    List all available models from all servers.

    Args:
        verbose (bool): Whether to print verbose output

    Returns:
        Dict[str, List[str]]: Dictionary mapping server types to lists of models
    """
    models = {}

    # Check LM Studio
    if is_server_running("lmstudio"):
        lmstudio_models = get_available_models("lmstudio")
        if lmstudio_models:
            models["lmstudio"] = lmstudio_models
            if verbose:
                print(f"Found {len(lmstudio_models)} LM Studio models")

    # Check Ollama
    if is_server_running("ollama"):
        ollama_models = get_available_models("ollama")
        if ollama_models:
            models["ollama"] = ollama_models
            if verbose:
                print(f"Found {len(ollama_models)} Ollama models")

    return models


# Example usage
if __name__ == "__main__":
    # List available models
    print("Available models:")
    models = list_available_models(verbose=True)

    for server_type, model_list in models.items():
        print(f"\n{server_type.capitalize()} models:")
        for model in model_list:
            print(f"- {model}")

    # Query a model
    if models:
        server_type = list(models.keys())[0]
        model_name = models[server_type][0]

        print(f"\nQuerying {server_type} model {model_name}...")
        response = query_model(
            model_type=server_type,
            model_name=model_name,
            prompt="What is the capital of France?",
            verbose=True
        )

        print("\nResponse:")
        print(response)