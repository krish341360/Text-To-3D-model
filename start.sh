#!/bin/sh

# Start Ollama in the background, binding to all interfaces
OLLAMA_HOST=0.0.0.0:11434 ollama serve &

# Wait for Ollama to initialize and download the model
sleep 5
ollama pull mistral

# Start your Openfabric Python app (replace with your actual command)
python3 ignite.py &

# Optionally: If your entrypoint is different, use that instead
# python3 main.py
python3 gradio_app.py