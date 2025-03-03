#!/usr/bin/env python3
"""
Main application for the Always-On AI Assistant.
This module connects all the layers and runs the assistant.
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
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Always-On AI Assistant")
    parser.add_argument(
        "--env-file",
        default=".env.local",
        help="Path to the environment file (default: .env.local)"
    )
    return parser.parse_args()


def main():
    """Main function to run the assistant."""
    # Parse command line arguments
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
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue


if __name__ == "__main__":
    main()