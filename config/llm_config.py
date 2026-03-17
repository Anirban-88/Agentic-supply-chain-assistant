# config/llm_config.py

import torch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get device from environment or auto-detect
device_env = os.getenv('DEVICE', 'auto').lower()

if device_env == 'auto':
    if torch.cuda.is_available():
        device = 'cuda'
    elif torch.backends.mps.is_available():
        device = 'mps'
    else:
        device = 'cpu'
else:
    device = device_env

# Llama Model Configuration
LLAMA_CONFIG = {
    'model_name': os.getenv('LLAMA_MODEL', 'meta-llama/Llama-3.2-1B-Instruct'),
    'device': device,
    'max_length': 512,
    'temperature': 0.1,  # Lower = more deterministic
    'top_p': 0.9,
    'do_sample': True,
    'num_return_sequences': 1,
}

# Alternative: Use local model path if downloaded
# LLAMA_CONFIG['model_name'] = './models/llama-3.2-1B-instruct'

print(f"🔧 LLM will run on: {LLAMA_CONFIG['device']}")
if LLAMA_CONFIG['device'] == 'cpu':
    print("⚠️  Running on CPU. Inference will be slower. Consider using GPU for faster performance.")
elif LLAMA_CONFIG['device'] == 'mps':
    print("🚀 Running on Apple Silicon GPU (MPS) - Accelerated inference enabled!")
elif LLAMA_CONFIG['device'] == 'cuda':
    print("🚀 Running on NVIDIA GPU (CUDA) - Accelerated inference enabled!")