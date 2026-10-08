# AURA — Advanced Unified Response & Automation Assistant

AURA is a desktop-based AI voice assistant built with Python that combines conversational AI, real-time web search, voice interaction, desktop automation, image generation, and a graphical user interface into a single intelligent assistant.

The system is designed to understand natural-language commands, determine the appropriate action, execute the task, and provide the response through both the graphical interface and voice output.

---

## 🚀 Features

### 🤖 AI Conversational Assistant
- Natural-language conversations powered by Groq.
- Maintains conversation history using JSON-based chat logs.
- Supports contextual responses and configurable assistant/user names.
- Uses LLM-based response generation for general queries.

### 🌐 Real-Time Web Search
- Performs Google-based web searches for up-to-date information.
- Combines search results with LLM-generated responses.
- Provides real-time information including current date and time.
- Uses Groq for generating responses from retrieved information.

### 🎙️ Voice Interaction
- Converts spoken commands into text.
- Uses browser-based speech recognition through Selenium.
- Supports configurable input language.
- Automatically formats recognized queries before processing.

### 🔊 Text-to-Speech
- Converts AI responses into spoken audio using Edge TTS.
- Supports configurable assistant voices.
- Uses pygame for audio playback.
- Handles long responses by shortening spoken output while keeping the complete response in the chat interface.

### ⚙️ Desktop Automation
AURA can execute desktop actions based on natural-language commands, including:

- Open applications
- Close applications
- Play YouTube content
- Search Google
- Search YouTube
- Generate content
- Control system volume
- Mute and unmute the system

The automation layer translates classified commands into executable actions and processes them asynchronously.

### 🎨 AI Image Generation
- Generates images from natural-language prompts.
- Uses Hugging Face's Stable Diffusion XL model.
- Generates multiple image variations for a prompt.
- Saves generated images locally.
- Automatically opens generated images for viewing.

### 📝 AI Content Generation
- Generates text content using the Groq API.
- Saves generated content as text files.
- Automatically opens generated content using the system text editor.

### 🧠 Intelligent Query Classification
A dedicated decision-making model categorizes user queries before execution.

Supported categories include:

- `general`
- `realtime`
- `open`
- `close`
- `play`
- `generate image`
- `system`
- `content`
- `google search`
- `youtube search`
- `reminder`
- `exit`

The classification layer uses Cohere to determine which subsystem should process the user's request.

### 🖥️ Graphical User Interface
The desktop interface is built using PyQt5 and includes:

- Full-screen assistant interface
- Animated assistant graphics
- Chat interface
- Microphone control
- Assistant status display
- Home and chat screens
- Window controls
- Voice interaction status

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      User Input     │
                    │  Voice / GUI Input  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Speech Recognition │
                    │      Module         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Decision Making    │
                    │      Model          │
                    │      Cohere         │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │   General   │  │  Real-Time  │  │ Automation  │
       │   Chatbot   │  │   Search    │  │   Engine    │
       └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
              │                │                │
              │                │                ├── Applications
              │                │                ├── YouTube
              │                │                ├── Google
              │                │                └── System Controls
              │                │
              │                ▼
              │         ┌─────────────┐
              │         │   Google    │
              │         │   Search    │
              │         └─────────────┘
              │
              └────────────────┬────────────────┐
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Response Engine   │
                    │       Groq LLM      │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
          ┌───────────────┐         ┌──────────────┐
          │  PyQt5 GUI    │         │    Edge TTS  │
          │  Chat Output  │         │ Voice Output │
          └───────────────┘         └──────────────┘
