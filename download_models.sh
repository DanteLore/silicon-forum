#!/bin/bash
# Downloads debate-capable models for the RX 7800 XT (16GB VRAM).
# All models are 8-14B range and fit comfortably in VRAM at Q4 quantization.
# Each has a distinct rhetorical character suited to different agent personalities.

set -e

echo "Downloading debate models..."

# Current default — solid all-rounder, good at following persona instructions
ollama pull llama3.1:8b

# Analytical and structured, builds arguments methodically — good for academics
ollama pull gemma2:9b

# Microsoft's model — rigorous, prefers logical chains over rhetoric — good for engineers
ollama pull phi4

# Larger Mistral — more nuanced than mistral:7b, better at holding complex positions
ollama pull mistral-nemo:12b

# Stronger DeepSeek distill — same RL chain-of-thought style but more capable at 14B
ollama pull deepseek-r1:14b

# More capable Qwen — benefits from the 18T token training at larger scale
ollama pull qwen2.5:14b

echo ""
echo "All models downloaded. Installed models:"
ollama list
