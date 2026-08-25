#!/bin/bash
echo "Downloading required local LLM models via Ollama..."
ollama pull deepseek-r1:7b
ollama pull deepseek-r1:1.5b
ollama pull qwen2.5-coder:7b
ollama pull hermes3:8b
ollama pull nomic-embed-text
echo "All models downloaded successfully!"