#!/bin/bash
# Simple script to run tests in Docker container

# Run pytest directly
cd /app
python -m pytest tests/ -v