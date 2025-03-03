# Free Resources for Always-On AI Assistant

This document outlines free and open-source resources that can be used to implement the always-on AI assistant without any cost.

## 1. Local LLM Serving

### 1.1. Ollama

* **Description:** Ollama provides a simple way to run open-source large language models locally.
* **Installation:**
  ```bash
  # macOS
  curl -fsSL https://ollama.com/install.sh | sh

  # Linux
  curl -fsSL https://ollama.com/install.sh | sh

  # Windows
  # Download from https://ollama.com/download/windows
  ```
* **Recommended Models:**
  * `mistralai/Mistral-7B-Instruct-v0.1` - Good balance of performance and resource requirements
  * `llama3:8b` - Meta's Llama 3 8B model, good for general-purpose tasks
  * `phi3:mini` - Microsoft's Phi-3 Mini, efficient for code and reasoning tasks
  * `qwen2:7b` - Alibaba's Qwen2 7B model, good for multilingual support
  * `deepseek-coder:6.7b` - Specialized for coding tasks

### 1.2. LM Studio

* **Description:** LM Studio provides a GUI for running and managing local LLMs.
* **Installation:** Download from [https://lmstudio.ai/](https://lmstudio.ai/)
* **Usage:**
  * Provides a user-friendly interface for downloading and running models
  * Exposes an OpenAI-compatible API for easy integration
  * Supports a wide range of models in GGUF format

### 1.3. LocalAI

* **Description:** LocalAI is an open-source project that provides an OpenAI-compatible API for local LLMs.
* **Installation:**
  ```bash
  # Using Docker
  docker run -p 8080:8080 localai/localai
  ```
* **GitHub:** [https://github.com/go-skynet/LocalAI](https://github.com/go-skynet/LocalAI)

## 2. Free API Services

### 2.1. Hugging Face Inference API

* **Description:** Hugging Face provides a free tier for their Inference API.
* **Limits:** 30,000 requests per month for free tier
* **Registration:** [https://huggingface.co/](https://huggingface.co/)
* **Usage:**
  ```python
  import requests

  API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
  headers = {"Authorization": f"Bearer {HF_API_KEY}"}

  def query(payload):
      response = requests.post(API_URL, headers=headers, json=payload)
      return response.json()

  output = query({"inputs": "What is the capital of France?"})
  ```

### 2.2. Together.ai

* **Description:** Together.ai offers a free tier for their API.
* **Limits:** $25 in free credits
* **Registration:** [https://together.ai/](https://together.ai/)
* **Models:** Access to various open-source models including Llama 3, Mistral, and more

### 2.3. Groq

* **Description:** Groq provides extremely fast inference for LLMs with a free tier.
* **Limits:** Limited free tier available
* **Registration:** [https://groq.com/](https://groq.com/)
* **Models:** LLama 3, Mixtral, and other open-source models

### 2.4. OpenRouter

* **Description:** OpenRouter provides access to various LLMs with a free tier.
* **Limits:** $1 in free credits
* **Registration:** [https://openrouter.ai/](https://openrouter.ai/)
* **Models:** Access to various open-source and proprietary models

## 3. Free Speech-to-Text Services

### 3.1. Mozilla DeepSpeech

* **Description:** Open-source speech-to-text engine that can run locally.
* **GitHub:** [https://github.com/mozilla/DeepSpeech](https://github.com/mozilla/DeepSpeech)
* **Installation:**
  ```bash
  pip install deepspeech
  ```

### 3.2. Vosk

* **Description:** Offline speech recognition toolkit that can run locally.
* **GitHub:** [https://github.com/alphacep/vosk-api](https://github.com/alphacep/vosk-api)
* **Installation:**
  ```bash
  pip install vosk
  ```
* **Usage:**
  ```python
  from vosk import Model, KaldiRecognizer
  import pyaudio

  model = Model("model")
  recognizer = KaldiRecognizer(model, 16000)

  # Audio capture and processing code...
  ```

### 3.3. Whisper.cpp

* **Description:** Port of OpenAI's Whisper model to C++, optimized for CPU usage.
* **GitHub:** [https://github.com/ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp)
* **Installation:**
  ```bash
  git clone https://github.com/ggerganov/whisper.cpp.git
  cd whisper.cpp
  make
  ```

## 4. Free Text-to-Speech Services

### 4.1. pyttsx3

* **Description:** Text-to-speech conversion library in Python that works offline.
* **Installation:**
  ```bash
  pip install pyttsx3
  ```
* **Usage:**
  ```python
  import pyttsx3

  engine = pyttsx3.init()
  engine.say("Hello World")
  engine.runAndWait()
  ```

### 4.2. gTTS with Local Playback

* **Description:** Google Text-to-Speech API with local playback.
* **Installation:**
  ```bash
  pip install gTTS playsound
  ```
* **Usage:**
  ```python
  from gtts import gTTS
  import os

  tts = gTTS("Hello World")
  tts.save("hello.mp3")
  os.system("mpg321 hello.mp3")  # or another audio player
  ```

### 4.3. Coqui TTS

* **Description:** Open-source text-to-speech system that can run locally.
* **GitHub:** [https://github.com/coqui-ai/TTS](https://github.com/coqui-ai/TTS)
* **Installation:**
  ```bash
  pip install TTS
  ```

## 5. Free Memory/Storage Solutions

### 5.1. SQLite

* **Description:** Lightweight, file-based database that requires no server.
* **Installation:** Built into Python
* **Usage:**
  ```python
  import sqlite3

  conn = sqlite3.connect("memory.db")
  cursor = conn.cursor()

  # Create table
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS conversations
  (id INTEGER PRIMARY KEY, user_input TEXT, assistant_response TEXT, timestamp TEXT)
  ''')

  # Insert data
  cursor.execute("INSERT INTO conversations VALUES (NULL, ?, ?, datetime('now'))",
                 ("Hello", "Hi there!"))

  conn.commit()
  conn.close()
  ```

### 5.2. JSON File Storage

* **Description:** Simple file-based storage using JSON.
* **Usage:**
  ```python
  import json
  import os

  def save_conversation(user_input, assistant_response):
      if os.path.exists("memory.json"):
          with open("memory.json", "r") as f:
              memory = json.load(f)
      else:
          memory = []

      memory.append({
          "user_input": user_input,
          "assistant_response": assistant_response,
          "timestamp": datetime.now().isoformat()
      })

      with open("memory.json", "w") as f:
          json.dump(memory, f)
  ```

### 5.3. Redis

* **Description:** In-memory data structure store that can be used as a database, cache, and message broker.
* **Installation:**
  ```bash
  # macOS
  brew install redis

  # Ubuntu
  sudo apt-get install redis-server
  ```
* **Usage:**
  ```python
  import redis

  r = redis.Redis(host='localhost', port=6379, db=0)
  r.set('user_input', 'Hello')
  r.set('assistant_response', 'Hi there!')
  ```

## 6. Free Tools and Utilities

### 6.1. Web Search

#### 6.1.1. SearXNG

* **Description:** Free and open-source metasearch engine that can be self-hosted.
* **GitHub:** [https://github.com/searxng/searxng](https://github.com/searxng/searxng)
* **Installation:**
  ```bash
  # Using Docker
  docker run -d -p 8080:8080 searxng/searxng
  ```

#### 6.1.2. DuckDuckGo API

* **Description:** Free API for searching the web.
* **Usage:**
  ```python
  import requests

  def search_duckduckgo(query):
      url = f"https://api.duckduckgo.com/?q={query}&format=json"
      response = requests.get(url)
      return response.json()
  ```

### 6.2. Weather Information

#### 6.2.1. OpenWeatherMap

* **Description:** Weather API with a free tier.
* **Limits:** 1,000 API calls per day
* **Registration:** [https://openweathermap.org/](https://openweathermap.org/)
* **Usage:**
  ```python
  import requests

  API_KEY = "your_api_key"
  city = "London"
  url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"

  response = requests.get(url)
  data = response.json()
  ```

### 6.3. Knowledge Base

#### 6.3.1. Wikipedia API

* **Description:** Free API for accessing Wikipedia content.
* **Usage:**
  ```python
  import wikipediaapi

  wiki = wikipediaapi.Wikipedia('en')
  page = wiki.page('Python_(programming_language)')
  print(page.summary)
  ```

#### 6.3.2. Local Vector Database

* **Description:** FAISS or Chroma for local vector storage and retrieval.
* **Installation:**
  ```bash
  pip install faiss-cpu chromadb
  ```
* **Usage:**
  ```python
  import chromadb

  client = chromadb.Client()
  collection = client.create_collection("knowledge_base")

  # Add documents
  collection.add(
      documents=["Document about AI", "Document about Python"],
      metadatas=[{"source": "book"}, {"source": "article"}],
      ids=["doc1", "doc2"]
  )

  # Query
  results = collection.query(
      query_texts=["Tell me about programming"],
      n_results=2
  )
  ```

## 7. Integration Examples

### 7.1. Local LLM with Query Helper

```python
import sys
sys.path.append('/path/to/servers')
from query_helper import query_model

def process_input(user_input, history):
    # Prepare prompt with history
    prompt = f"Previous conversation:\n{format_history(history)}\n\nUser: {user_input}\nAssistant:"

    # Query local model using query_helper
    response = query_model(
        model_type="ollama",
        model_name="mistralai/Mistral-7B-Instruct-v0.1",
        prompt=prompt,
        base_url="http://localhost:11434"
    )

    return response

def format_history(history):
    formatted = ""
    for entry in history:
        formatted += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n\n"
    return formatted
```

### 7.2. Speech Input with Local STT

```python
import pyaudio
from vosk import Model, KaldiRecognizer

def setup_speech_recognition():
    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    return stream, recognizer

def get_speech_input(stream, recognizer):
    print("Listening...")
    audio_data = b""

    # Collect audio for 5 seconds
    for _ in range(10):
        data = stream.read(4096)
        audio_data += data

        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = result[14:-3]  # Extract text from JSON result
            if text:
                return text

    # Process any remaining audio
    result = recognizer.FinalResult()
    text = result[14:-3]
    return text
```

### 7.3. Complete Integration Example

```python
import os
import json
import sys
from dotenv import load_dotenv
sys.path.append('/path/to/servers')
from query_helper import query_model

# Load configuration
load_dotenv(".env.local")

class TextInputLayer:
    def get_input(self):
        return input("You: ")

class InMemoryMemory:
    def __init__(self):
        self.history = []

    def add_entry(self, user_input, assistant_response):
        self.history.append({
            "user": user_input,
            "assistant": assistant_response
        })

    def get_history(self):
        return self.history

class BasicChainingAgent:
    def __init__(self, memory):
        self.memory = memory
        self.model_type = os.getenv("AGENT_1_TYPE")
        self.model_name = os.getenv("AGENT_1_MODEL")
        self.base_url = os.getenv("AGENT_1_BASE_URL")

    def process(self, user_input):
        # Format history
        history = self.memory.get_history()
        formatted_history = ""
        for entry in history:
            formatted_history += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n\n"

        # Prepare prompt
        prompt = f"Previous conversation:\n{formatted_history}\n\nUser: {user_input}\nAssistant:"

        # Query model
        response = query_model(
            model_type=self.model_type,
            model_name=self.model_name,
            prompt=prompt,
            base_url=self.base_url
        )

        return response

class TextOutputLayer:
    def output(self, text):
        print(f"Assistant: {text}")

def main():
    # Initialize layers
    input_layer = TextInputLayer()
    memory = InMemoryMemory()
    agent = BasicChainingAgent(memory)
    output_layer = TextOutputLayer()

    print("Always-On AI Assistant initialized. Type 'exit' to quit.")

    while True:
        # Get input
        user_input = input_layer.get_input()
        if user_input.lower() == "exit":
            break

        # Process input
        response = agent.process(user_input)

        # Store in memory
        memory.add_entry(user_input, response)

        # Output response
        output_layer.output(response)

if __name__ == "__main__":
    main()
```

This document provides a comprehensive list of free resources and integration examples for implementing the always-on AI assistant without any cost. All components can be run locally or use free API tiers, ensuring the assistant can be built and operated without any financial investment.