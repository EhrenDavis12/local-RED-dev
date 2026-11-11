#!/usr/bin/env bash
# One-time setup for the local game-asset pipeline on an Apple Silicon Mac.
# Installs: Homebrew deps, ComfyUI (native, Metal GPU), ComfyUI-Manager,
# the Animagine XL 4.0 checkpoint, and the pipeline's own Python environment.
# Safe to re-run: every step skips work that is already done.
set -euo pipefail

AI_HOME="${AI_HOME:-$HOME/AI}"
COMFY_DIR="$AI_HOME/ComfyUI"
PIPE_DIR="$(cd "$(dirname "$0")" && pwd)"

say() { printf "\n\033[1;36m==> %s\033[0m\n" "$*"; }

[[ "$(uname -m)" == "arm64" ]] || { echo "This script is for Apple Silicon (arm64) Macs."; exit 1; }

say "1/6 Homebrew packages (python 3.11, ffmpeg, git)"
if ! command -v brew >/dev/null; then
  echo "Homebrew not found. Install it first: https://brew.sh  then re-run this script."
  exit 1
fi
brew install python@3.11 ffmpeg git
PY="$(brew --prefix python@3.11)/bin/python3.11"

say "2/6 ComfyUI in $COMFY_DIR"
mkdir -p "$AI_HOME"
[[ -d "$COMFY_DIR" ]] || git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFY_DIR"
cd "$COMFY_DIR"
[[ -d venv ]] || "$PY" -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install torch torchvision torchaudio   # macOS wheels include Metal (MPS) support
./venv/bin/pip install -r requirements.txt

say "3/6 ComfyUI-Manager (installs extra nodes from inside ComfyUI)"
[[ -d custom_nodes/ComfyUI-Manager ]] || \
  git clone https://github.com/ltdrdata/ComfyUI-Manager.git custom_nodes/ComfyUI-Manager

say "4/6 Animagine XL 4.0 checkpoint (~7 GB, license: CreativeML Open RAIL++-M, commercial use OK)"
CKPT="models/checkpoints/animagine-xl-4.0-opt.safetensors"
if [[ ! -f "$CKPT" ]]; then
  curl -L --fail -o "$CKPT.part" \
    "https://huggingface.co/cagliostrolab/animagine-xl-4.0/resolve/main/animagine-xl-4.0-opt.safetensors?download=true"
  mv "$CKPT.part" "$CKPT"
fi
mkdir -p models/loras   # put your chibi style LoRA (.safetensors) here

say "5/6 Pipeline Python environment (background removal, sprite sheets)"
cd "$PIPE_DIR"
[[ -d .venv ]] || "$PY" -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

say "6/6 Start script"
cat > "$PIPE_DIR/start_comfyui.sh" <<EOF
#!/usr/bin/env bash
# Starts ComfyUI on http://127.0.0.1:8188 (UI + API). Leave this terminal open.
cd "$COMFY_DIR"
export PYTORCH_ENABLE_MPS_FALLBACK=1
exec ./venv/bin/python main.py --listen 127.0.0.1 --port 8188
EOF
chmod +x "$PIPE_DIR/start_comfyui.sh"

say "Done."
echo "Next: ./start_comfyui.sh   (in one terminal)"
echo "Then: ./.venv/bin/python generate_assets.py --check"
