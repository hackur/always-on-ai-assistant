#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main application for the Always-On AI Assistant.

This module connects all the layers and runs the assistant. It handles command-line
arguments, initializes the layers, and implements the main interaction loop.

The assistant uses a modular architecture with the following layers:
- Input Layer: Handles user input from various sources.
- Memory Layer: Manages conversation history and state.
- Processing Layer: Implements the core agent logic and workflow management.
- Output Layer: Presents the assistant's responses to the user.

Functions:
    parse_arguments: Parse command-line arguments.
    main: Main function to run the assistant.

Typical usage:
    $ python main_layered.py
    $ python main_layered.py --env-file custom.env
"""

import sys
import os
import argparse
from typing import Dict, Any

# Add the parent directory to sys.path to import layers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from layers import (
        load_config,
        create_input_layer,
        create_memory_layer,
        create_processing_layer,
        create_output_layer
    )
except ImportError as e:
    print(f"Error importing layers: {e}")
    print("Make sure you have installed the required dependencies.")
    sys.exit(1)


def parse_arguments():
    """
    Parse command-line arguments.

    This function sets up the argument parser and parses the command-line arguments.

    Returns:
        argparse.Namespace: The parsed command-line arguments.

    Command-line arguments:
        --env-file: Path to the environment file (default: .env.local)

    Example:
        $ python main_layered.py --env-file custom.env
    """
    parser = argparse.ArgumentParser(description="Always-On AI Assistant")
    parser.add_argument(
        "--env-file",
        default=".env.local",
        help="Path to the environment file (default: .env.local)"
    )
    return parser.parse_args()


def main():
    """
    Main function to run the assistant.

    This function initializes the layers, runs the main interaction loop,
    and handles errors and exceptions.

    The main interaction loop:
    1. Get input from the user.
    2. Process the input to generate a response.
    3. Store the interaction in memory.
    4. Output the response to the user.
    5. Repeat until the user exits.

    The user can exit by typing 'exit' or 'quit', or by pressing Ctrl+C.

    Raises:
        SystemExit: If there is an error initializing the layers.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Load configuration
    try:
        config = load_config(args.env_file)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Create layers
    try:
        input_layer = create_input_layer(config)
        memory_layer = create_memory_layer(config)
        processing_layer = create_processing_layer(config, memory_layer)
        output_layer = create_output_layer(config)
    except Exception as e:
        print(f"Error creating layers: {e}")
        sys.exit(1)

    # Print initialization message
    print("Always-On AI Assistant initialized.")
    print(f"Using {config['AGENT_1_TYPE']} model: {config['AGENT_1_MODEL']}")
    print("Type 'exit' to quit.")
    print("-" * 50)

    # Main loop
    while True:
        try:
            # Get input
            user_input = input_layer.get_input()

            # Check for exit command
            if user_input.get("text", "").lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            # Process input
            response = processing_layer.process(user_input)

            # Store in memory
            memory_layer.add_entry(user_input, response)

            # Output response
            output_layer.output(response)

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nGoodbye!")
            break
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            # TODO: Implement proper error handling and logging
            continue


if __name__ == "__main__":
    main()