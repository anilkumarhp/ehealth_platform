#!/bin/sh

# Wait for Ollama to be ready
echo "Waiting for Ollama service to be ready..."
until curl -s http://llm-service:11434/api/health >/dev/null; do
  echo "Waiting for Ollama service..."
  sleep 5
done

echo "Ollama service is ready!"

# Pull the model
echo "Pulling the phi3:mini model..."
curl -X POST http://llm-service:11434/api/pull -d '{"name": "phi3:mini"}'

echo "Model initialization complete!"