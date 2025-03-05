#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layers package for the Always-On AI Assistant.

This package contains the modular components of the assistant, organized into layers.
Each layer is responsible for a specific aspect of the assistant's functionality:

- Input Layer: Handles user input from various sources.
- Memory Layer: Manages conversation history and state.
- Processing Layer: Implements the core agent logic and workflow management.
- Output Layer: Presents the assistant's responses to the user.

The package also includes a configuration module for loading and managing settings.

Classes:
    InputLayer: Abstract base class for all input layers.
    TextInputLayer: Input layer that gets text input from the command line.

    MemoryLayer: Abstract base class for all memory layers.
    InMemoryMemory: Memory layer that stores conversation history in memory.
    JsonFileMemory: Memory layer that stores conversation history in a JSON file.

    ProcessingLayer: Abstract base class for all processing layers.
    BasicChainingAgent: Processing layer that implements a basic prompt chaining workflow.

    OutputLayer: Abstract base class for all output layers.
    TextOutputLayer: Output layer that prints text to the console.
    ColoredTextOutputLayer: Output layer that prints colored text to the console.

Functions:
    create_input_layer: Factory function to create the appropriate input layer.
    create_memory_layer: Factory function to create the appropriate memory layer.
    create_processing_layer: Factory function to create the appropriate processing layer.
    create_output_layer: Factory function to create the appropriate output layer.
    load_config: Load configuration from environment variables and .env files.

Typical usage example:
    from layers import (
        load_config,
        create_input_layer,
        create_memory_layer,
        create_processing_layer,
        create_output_layer
    )

    config = load_config()
    input_layer = create_input_layer(config)
    memory_layer = create_memory_layer(config)
    processing_layer = create_processing_layer(config, memory_layer)
    output_layer = create_output_layer(config)

    user_input = input_layer.get_input()
    response = processing_layer.process(user_input)
    memory_layer.add_entry(user_input, response)
    output_layer.output(response)
"""

from .input_layer import InputLayer, TextInputLayer, create_input_layer
from .memory_layer import MemoryLayer, InMemoryMemory, JsonFileMemory, create_memory_layer
from .output_layer import OutputLayer, TextOutputLayer, ColoredTextOutputLayer, create_output_layer
from .processing_layer import ProcessingLayer, BasicChainingAgent, create_processing_layer
from .config import load_config

__all__ = [
    # Input Layer
    'InputLayer',
    'TextInputLayer',
    'create_input_layer',

    # Memory Layer
    'MemoryLayer',
    'InMemoryMemory',
    'JsonFileMemory',
    'create_memory_layer',

    # Output Layer
    'OutputLayer',
    'TextOutputLayer',
    'ColoredTextOutputLayer',
    'create_output_layer',

    # Processing Layer
    'ProcessingLayer',
    'BasicChainingAgent',
    'create_processing_layer',

    # Configuration
    'load_config'
]

# Version information
__version__ = '0.1.0'
__author__ = 'Always-On AI Assistant Team'