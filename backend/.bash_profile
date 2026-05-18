#!/bin/bash
# Auto-activate venv when entering backend directory
if [[ "$PWD" == *"/backend" ]] && [[ -f "venv/Scripts/activate" ]]; then
    source venv/Scripts/activate
    echo "✓ Virtual environment activated"
fi
