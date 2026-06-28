#!/bin/bash
# SAHAYAK-AI Model Pull Script
# Pulls Ollama models for the specified hardware profile

set -euo pipefail

PROFILE="${1:-mid}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "==========================================="
echo "SAHAYAK-AI Model Pull - Profile: $PROFILE"
echo "==========================================="

# Check if Ollama is running
if ! command -v ollama &> /dev/null; then
    echo "ERROR: ollama not found. Please install Ollama first."
    echo "Visit: https://ollama.ai"
    exit 1
fi

# Start Ollama if not running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Pull model based on profile
case "$PROFILE" in
    low)
        echo "Pulling Gemma-2 2B for low-end hardware..."
        ollama pull gemma2:2b
        ;;
    mid)
        echo "Pulling LLaMA-3 8B Q4_K_M for mid-range hardware..."
        ollama pull llama3:8b-q4
        ;;
    high)
        echo "Pulling LLaMA-3 8B for high-end hardware..."
        ollama pull llama3:8b
        ;;
    *)
        echo "ERROR: Unknown profile '$PROFILE'. Use: low, mid, or high"
        exit 1
        ;;
esac

echo ""
echo "Models pulled successfully for profile: $PROFILE"
echo "Available models:"
ollama list
