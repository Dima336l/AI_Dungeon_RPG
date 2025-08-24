import json
import sys
import time
import shutil
import os
import random
from urllib import request

# Workflow JSON adjusted for general RPG asset generation
prompt_text = '''{
  "7": {
    "inputs": {
      "seed": 0,
      "steps": 35,
      "cfg": 8,
      "sampler_name": "euler",
      "scheduler": "simple",
      "denoise": 1,
      "model": ["20", 0],
      "positive": ["15", 0],
      "negative": ["16", 0],
      "latent_image": ["9", 0]
    },
    "class_type": "KSampler",
    "_meta": {"title": "KSampler"}
  },
  "9": {
    "inputs": {
      "width": 1280,
      "height": 1280,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {"title": "Empty Latent Image"}
  },
  "12": {
    "inputs": {
      "samples": ["7", 0],
      "vae": ["20", 2]
    },
    "class_type": "VAEDecode",
    "_meta": {"title": "VAE Decode"}
  },
  "15": {
    "inputs": {
      "text": "",
      "clip": ["20", 1]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {"title": "CLIP Text Encode (Positive Prompt)"}
  },
  "16": {
    "inputs": {
      "text": "",
      "clip": ["20", 1]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {"title": "CLIP Text Encode (Negative Prompt)"}
  },
  "17": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": ["12", 0]
    },
    "class_type": "SaveImage",
    "_meta": {"title": "Save Image"}
  },
  "18": {
    "inputs": {
      "images": ["12", 0]
    },
    "class_type": "PreviewImage",
    "_meta": {"title": "Preview Image"}
  },
  "20": {
    "inputs": {
      "ckpt_name": "anything-v5.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {"title": "Load Checkpoint"}
  }
}'''

COMFYUI_OUTPUT_DIR = r"C:\Users\nirca\repos\ComfyUI-master\output"
TARGET_DIR = r"C:\Users\nirca\repos\rpg_dungeon_ai\assets\images"

def queue_prompt(workflow):
    # ComfyUI API expects this structure
    payload = {"prompt": workflow}  # Changed from "workflow" to "prompt"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        "http://127.0.0.1:8188/prompt",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        response = request.urlopen(req)
        result = response.read().decode()
        print(f"ComfyUI Response: {result}")
        return json.loads(result)
    except Exception as e:
        print(f"Error queuing prompt: {e}")
        return None

def check_comfyui_status():
    """Check if ComfyUI is running and accessible"""
    try:
        req = request.Request("http://127.0.0.1:8188/system_stats")
        response = request.urlopen(req, timeout=5)
        print("ComfyUI is running and accessible")
        return True
    except Exception as e:
        print(f"ComfyUI is not accessible: {e}")
        print("Make sure ComfyUI is running on http://127.0.0.1:8188")
        return False

def wait_for_completion(prompt_id):
    """Wait for the generation to complete by checking the history"""
    if not prompt_id:
        return False
    
    max_wait_time = 300  # 5 minutes max
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            req = request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
            response = request.urlopen(req)
            history = json.loads(response.read().decode())
            
            if prompt_id in history:
                print("Generation completed!")
                return True
                
        except Exception as e:
            print(f"Error checking status: {e}")
        
        print("Waiting for generation to complete...")
        time.sleep(5)
    
    print("Timeout waiting for generation")
    return False

def move_generated_files(prefix):
    """Move generated files from ComfyUI output to target directory"""
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    
    moved_files = []
    for filename in os.listdir(COMFYUI_OUTPUT_DIR):
        if filename.startswith(prefix):
            src = os.path.join(COMFYUI_OUTPUT_DIR, filename)
            dst = os.path.join(TARGET_DIR, filename)
            print(f"Moving {src} -> {dst}")
            shutil.move(src, dst)
            moved_files.append(filename)
    
    if not moved_files:
        print(f"No files found with prefix '{prefix}' in {COMFYUI_OUTPUT_DIR}")
        # List all files to help debug
        print("Available files:")
        for f in os.listdir(COMFYUI_OUTPUT_DIR):
            print(f"  {f}")
    else:
        print(f"Moved {len(moved_files)} files")
    
    return moved_files

def main():
    if len(sys.argv) < 2:
        print('Usage: python get-images.py "describe your asset here"')
        return

    # Check if ComfyUI is running first
    if not check_comfyui_status():
        return

    user_prompt = sys.argv[1]
    prompt = json.loads(prompt_text)

    # General RPG positive prompt
    prompt["15"]["inputs"]["text"] = f"""
RPG asset, high quality, detailed, cinematic lighting, dynamic composition, {user_prompt}
"""

    # Light negative prompt to avoid artifacts
    prompt["16"]["inputs"]["text"] = """
blurry, low quality, text, watermark, bad anatomy, distorted
"""

    # Random seed for variety
    prompt["7"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)

    # Unique filename prefix
    filename_prefix = f"rpg_asset_{int(time.time())}"
    prompt["17"]["inputs"]["filename_prefix"] = filename_prefix

    # Queue the prompt
    print(f"Generating: {user_prompt}")
    result = queue_prompt(prompt)
    
    if result and "prompt_id" in result:
        prompt_id = result["prompt_id"]
        print(f"Prompt queued with ID: {prompt_id}")
        
        # Wait for completion
        if wait_for_completion(prompt_id):
            time.sleep(2)  # Small delay to ensure files are written
            move_generated_files(filename_prefix)
        else:
            print("Generation failed or timed out")
    else:
        print("Failed to queue prompt")

if __name__ == "__main__":
    main()