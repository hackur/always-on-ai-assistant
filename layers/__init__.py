"""
Layers package for the Always-On AI Assistant.
This package contains the modular components of the assistant.
"""

from .input_layer import InputLayer, TextInputLayer, create_input_layer
from .memory_layer import MemoryLayer, InMemoryMemory, JsonFileMemory, create_memory_layer
from .output_layer import OutputLayer, TextOutputLayer, ColoredTextOutputLayer, create_output_layer
from .processing_layer import ProcessingLayer, BasicChainingAgent, create_processing_layer
from .config import load_config

__all__ = [
    'InputLayer', 'TextInputLayer', 'create_input_layer',
    'MemoryLayer', 'InMemoryMemory', 'JsonFileMemory', 'create_memory_layer',
    'OutputLayer', 'TextOutputLayer', 'ColoredTextOutputLayer', 'create_output_layer',
    'ProcessingLayer', 'BasicChainingAgent', 'create_processing_layer',
    'load_config'
]