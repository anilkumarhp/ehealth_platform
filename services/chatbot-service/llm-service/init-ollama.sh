#!/bin/bash

# Wait for Ollama to be ready
echo "Waiting for Ollama service to be ready..."
until curl -s http://llm-service:11434/api/health >/dev/null; do
  sleep 2
done

# Pull the model
echo "Pulling the model..."
curl -X POST http://llm-service:11434/api/pull -d '{"name": "phi3:mini"}'

echo "Model initialization complete!"