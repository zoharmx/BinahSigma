#!/bin/bash
set -e

echo "========================================="
echo "RENDER BUILD SCRIPT - FORCING UPDATES"
echo "========================================="

# Force upgrade pip first
pip install --upgrade pip

# Force install latest google-generativeai
echo "Installing google-generativeai (FORCED UPGRADE)..."
pip install --upgrade --force-reinstall google-generativeai

# Install all other requirements
echo "Installing requirements.txt..."
pip install --upgrade -r requirements.txt

# Verify versions
echo "========================================="
echo "INSTALLED VERSIONS:"
pip show google-generativeai | grep Version
pip show mistralai | grep Version
pip show openai | grep Version
echo "========================================="

echo "Build complete!"
