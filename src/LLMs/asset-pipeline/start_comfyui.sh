#!/usr/bin/env bash
# Starts ComfyUI on http://127.0.0.1:8188 (UI + API). Leave this terminal open.
cd "/Users/ehrendavis/AI/ComfyUI"
export PYTORCH_ENABLE_MPS_FALLBACK=1
exec ./venv/bin/python main.py --listen 127.0.0.1 --port 8188
