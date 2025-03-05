#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacOS Installation Script for Always-On AI Assistant.

This script sets up the Always-On AI Assistant to be triggered by the Globe/Fn key
on MacBook Pro M3 models. It creates the necessary files and configurations to:

1. Install the required dependencies
2. Create a launch agent to run at login
3. Set up a keyboard shortcut to trigger the assistant
4. Configure the assistant with default settings

Usage:
    python install-to-mac.py [--voice-profile PROFILE]

Example:
    python install-to-mac.py
    python install-to-mac.py --voice-profile british
"""

import os
import sys
import argparse
import subprocess
import shutil
import json
import plistlib
from pathlib import Path
import getpass

# Constants
APP_NAME = "AlwaysOnAIAssistant"
LAUNCH_AGENT_NAME = "com.user.alwaysonaiassistant"
SHORTCUT_NAME = "Launch AI Assistant"


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Install Always-On AI Assistant on macOS")
    parser.add_argument(
        "--voice-profile",
        default="default",
        help="Voice profile to use (default: default)"
    )
    parser.add_argument(
        "--model",
        default="mistral:instruct",
        help="LLM model to use (default: mistral:instruct)"
    )
    parser.add_argument(
        "--wake-word",
        default="hey assistant",
        help="Wake word to activate the assistant (default: 'hey assistant')"
    )
    parser.add_argument(
        "--install-dir",
        default=os.path.expanduser("~/Applications/AlwaysOnAIAssistant"),
        help="Installation directory (default: ~/Applications/AlwaysOnAIAssistant)"
    )
    return parser.parse_args()


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("Error: Python 3.10 or higher is required.")
        print(f"Current version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        sys.exit(1)

    # Check if uv is installed
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: uv is not installed. Installing...")
        try:
            subprocess.run(["pip", "install", "uv"], check=True)
        except subprocess.CalledProcessError:
            print("Error: Failed to install uv. Please install it manually.")
            print("Run: pip install uv")
            sys.exit(1)

    # Check if Ollama is installed
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: Ollama is not installed.")
        print("Please install Ollama from https://ollama.ai/download")
        print("After installation, run: ollama pull mistral:instruct")
        input("Press Enter to continue after installing Ollama...")

    print("Dependencies checked.")


def create_installation_directory(install_dir):
    """Create the installation directory."""
    print(f"Creating installation directory: {install_dir}")
    os.makedirs(install_dir, exist_ok=True)
    return install_dir


def copy_files(source_dir, install_dir):
    """Copy the necessary files to the installation directory."""
    print(f"Copying files from {source_dir} to {install_dir}...")

    # Directories to copy
    dirs_to_copy = [
        "layers", "modules", "prompts", "voices", "tests", "models"
    ]

    # Files to copy
    files_to_copy = [
        "voice_assistant_demo.py", "requirements.txt", ".env.sample",
        "README.md", "VOSK_MODELS.md", "setup_vosk_model.py"
    ]

    # Create directories
    for dir_name in dirs_to_copy:
        src_dir = os.path.join(source_dir, dir_name)
        dst_dir = os.path.join(install_dir, dir_name)
        if os.path.exists(src_dir):
            os.makedirs(dst_dir, exist_ok=True)
            for item in os.listdir(src_dir):
                src_item = os.path.join(src_dir, item)
                dst_item = os.path.join(dst_dir, item)
                if os.path.isdir(src_item):
                    shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_item, dst_item)

    # Create logs directory
    os.makedirs(os.path.join(install_dir, "logs"), exist_ok=True)

    # Copy files
    for file_name in files_to_copy:
        src_file = os.path.join(source_dir, file_name)
        dst_file = os.path.join(install_dir, file_name)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)

    print("Files copied successfully.")


def create_env_file(install_dir, args):
    """Create the .env file with default settings."""
    print("Creating .env file...")

    env_file = os.path.join(install_dir, ".env")
    sample_env_file = os.path.join(install_dir, ".env.sample")

    if os.path.exists(sample_env_file):
        shutil.copy2(sample_env_file, env_file)
    else:
        # Create a basic .env file
        with open(env_file, "w") as f:
            f.write(f"# AI Assistant Configuration\n")
            f.write(f"LLM_MODEL_TYPE=ollama\n")
            f.write(f"LLM_MODEL_NAME={args.model}\n")
            f.write(f"LLM_BASE_URL=http://localhost:11434\n")
            f.write(f"TTS_ENGINE=pyttsx3\n")
            f.write(f"TTS_RATE=150\n")
            f.write(f"TTS_VOLUME=1.0\n")

    print(f".env file created at {env_file}")


def create_launch_script(install_dir, args):
    """Create the launch script."""
    print("Creating launch script...")

    launch_script_path = os.path.join(install_dir, "launch_assistant.py")

    with open(launch_script_path, "w") as f:
        f.write(f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Launch script for Always-On AI Assistant.
\"\"\"

import os
import sys
import subprocess
import time

# Change to the installation directory
os.chdir("{install_dir}")

# Ensure Ollama is running
try:
    subprocess.run(["pgrep", "ollama"], check=True, capture_output=True)
except subprocess.CalledProcessError:
    print("Starting Ollama...")
    subprocess.Popen(["open", "-a", "Ollama"])
    # Wait for Ollama to start
    time.sleep(5)

# Launch the voice assistant
cmd = [
    sys.executable,
    "voice_assistant_demo.py",
    "--voice-profile", "{args.voice_profile}",
    "--wake-word", "{args.wake_word}"
]

subprocess.run(cmd)
""")

    # Make the script executable
    os.chmod(launch_script_path, 0o755)

    print(f"Launch script created at {launch_script_path}")
    return launch_script_path


def create_launch_agent(install_dir, launch_script):
    """Create a launch agent to run the assistant at login."""
    print("Creating launch agent...")

    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Create the LaunchAgents directory if it doesn't exist
    launch_agents_dir = os.path.join(home_dir, "Library", "LaunchAgents")
    os.makedirs(launch_agents_dir, exist_ok=True)

    # Create the plist file
    plist_path = os.path.join(launch_agents_dir, f"{LAUNCH_AGENT_NAME}.plist")

    plist_content = {
        "Label": LAUNCH_AGENT_NAME,
        "ProgramArguments": [
            sys.executable,
            launch_script
        ],
        "RunAtLoad": True,
        "KeepAlive": False,
        "StandardOutPath": os.path.join(install_dir, "logs", "launch_agent_stdout.log"),
        "StandardErrorPath": os.path.join(install_dir, "logs", "launch_agent_stderr.log")
    }

    with open(plist_path, "wb") as f:
        plistlib.dump(plist_content, f)

    # Load the launch agent
    subprocess.run(["launchctl", "load", plist_path], check=True)

    print(f"Launch agent created at {plist_path}")


def create_keyboard_shortcut(launch_script):
    """Create a keyboard shortcut to trigger the assistant."""
    print("Creating keyboard shortcut...")

    # Create an AppleScript to run the launch script
    applescript = f"""
    tell application "Terminal"
        do script "{sys.executable} {launch_script}"
    end tell
    """

    # Save the AppleScript
    username = getpass.getuser()
    script_dir = f"/Users/{username}/Library/Scripts"
    os.makedirs(script_dir, exist_ok=True)

    script_path = os.path.join(script_dir, f"{SHORTCUT_NAME}.scpt")

    with open(script_path, "w") as f:
        f.write(applescript)

    print(f"AppleScript created at {script_path}")

    # Instructions for setting up the keyboard shortcut
    print("\nTo set up the keyboard shortcut:")
    print("1. Open System Settings > Keyboard > Keyboard Shortcuts > Services")
    print("2. Find the script under 'General' or 'Scripts'")
    print("3. Click 'Add Shortcut' and press the Globe/Fn key twice")
    print("4. Close System Settings")


def install_vosk_model(install_dir):
    """Install the Vosk model for offline speech recognition."""
    print("Installing Vosk model...")

    # Run the setup_vosk_model.py script
    setup_script = os.path.join(install_dir, "setup_vosk_model.py")
    if os.path.exists(setup_script):
        subprocess.run([sys.executable, setup_script, "--model", "small"], check=True)
        print("Vosk model installed successfully.")
    else:
        print("Warning: setup_vosk_model.py not found. Skipping Vosk model installation.")


def install_requirements(install_dir):
    """Install the required Python packages."""
    print("Installing requirements...")

    requirements_file = os.path.join(install_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        subprocess.run(["uv", "pip", "install", "-r", requirements_file], check=True)
        print("Requirements installed successfully.")
    else:
        print("Warning: requirements.txt not found. Skipping package installation.")


def main():
    """Main function to install the Always-On AI Assistant."""
    print("=" * 80)
    print("Always-On AI Assistant Installer for macOS")
    print("=" * 80)

    # Parse arguments
    args = parse_arguments()

    # Check dependencies
    check_dependencies()

    # Get the current directory (source directory)
    source_dir = os.path.dirname(os.path.abspath(__file__))

    # Create the installation directory
    install_dir = create_installation_directory(args.install_dir)

    # Copy files
    copy_files(source_dir, install_dir)

    # Create .env file
    create_env_file(install_dir, args)

    # Install requirements
    install_requirements(install_dir)

    # Install Vosk model
    install_vosk_model(install_dir)

    # Create launch script
    launch_script = create_launch_script(install_dir, args)

    # Create launch agent
    create_launch_agent(install_dir, launch_script)

    # Create keyboard shortcut
    create_keyboard_shortcut(launch_script)

    print("\n" + "=" * 80)
    print("Installation completed successfully!")
    print("=" * 80)
    print(f"The Always-On AI Assistant has been installed to: {install_dir}")
    print(f"It will start automatically when you log in.")
    print(f"You can also trigger it by pressing the Globe/Fn key twice (after setting up the shortcut).")
    print(f"Wake word: '{args.wake_word}'")
    print(f"Voice profile: {args.voice_profile}")
    print(f"LLM model: {args.model}")
    print("\nEnjoy your Always-On AI Assistant!")


if __name__ == "__main__":
    main()