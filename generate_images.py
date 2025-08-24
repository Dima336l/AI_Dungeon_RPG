import json
import time
import shutil
import os
import random
import hashlib
from urllib import request

# Workflow JSON for RPG asset generation
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
TARGET_DIR = r"C:\Users\nirca\repos\rpg_dungeon_ai\static\images"

def queue_prompt(workflow):
    """Queue a prompt to ComfyUI and return the result"""
    payload = {"prompt": workflow}
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        "http://127.0.0.1:8188/prompt",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        response = request.urlopen(req, timeout=10)
        result = response.read().decode()
        return json.loads(result)
    except Exception as e:
        print(f"Error queuing prompt: {e}")
        return None

def check_comfyui_status():
    """Check if ComfyUI is running and accessible"""
    try:
        # Try the queue endpoint first (more reliable)
        req = request.Request("http://127.0.0.1:8188/queue")
        response = request.urlopen(req, timeout=5)
        print("ComfyUI is running and accessible")
        return True
    except Exception as e:
        print(f"ComfyUI connection failed: {e}")
        # Try alternative endpoint
        try:
            req = request.Request("http://127.0.0.1:8188/")
            response = request.urlopen(req, timeout=5)
            print("ComfyUI is running (found via root endpoint)")
            return True
        except Exception as e2:
            print(f"ComfyUI root endpoint also failed: {e2}")
            return False

def wait_for_completion(prompt_id, max_wait_time=60):
    """Wait for the generation to complete by checking the history"""
    if not prompt_id:
        return False
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        try:
            req = request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
            response = request.urlopen(req, timeout=5)
            history = json.loads(response.read().decode())
            
            if prompt_id in history:
                return True
                
        except Exception:
            pass
        
        time.sleep(2)
    
    return False

def move_generated_files(prefix, target_filename):
    """Move generated files from ComfyUI output to target directory with specific name"""
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    
    # Find the most recent file with the prefix
    matching_files = []
    for filename in os.listdir(COMFYUI_OUTPUT_DIR):
        if filename.startswith(prefix) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(COMFYUI_OUTPUT_DIR, filename)
            matching_files.append((filepath, os.path.getmtime(filepath)))
    
    if matching_files:
        # Get the most recent file
        most_recent_file = max(matching_files, key=lambda x: x[1])[0]
        dst = os.path.join(TARGET_DIR, target_filename)
        shutil.move(most_recent_file, dst)
        return True
    
    return False

def sanitize_filename(text, max_length=50):
    """Create a safe filename from text"""
    # Create a hash of the text for uniqueness
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    
    # Clean the text for filename
    clean_text = ''.join(c for c in text if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_text = clean_text.replace(' ', '_')[:max_length-9]  # Reserve space for hash
    
    return f"{clean_text}_{text_hash}.png"

def generate_image_from_text(scene_description):
    """
    Generate an image from scene description text.
    Returns the relative URL path to the generated image.
    """
    print(f"Generating image for: {scene_description[:50]}...")
    
    # Check if ComfyUI is running
    if not check_comfyui_status():
        print("ComfyUI is not running. Skipping image generation.")
        return None
    
    # Create filename from scene description
    image_filename = sanitize_filename(scene_description)
    image_path = os.path.join(TARGET_DIR, image_filename)
    
    # Check if image already exists (caching)
    if os.path.exists(image_path):
        print(f"Using cached image: {image_filename}")
        return f"/static/images/{image_filename}"
    
    try:
        # Prepare the workflow
        prompt = json.loads(prompt_text)
        
        # Set the scene description as the positive prompt
        prompt["15"]["inputs"]["text"] = f"""
RPG dungeon scene, atmospheric, detailed, cinematic lighting, {scene_description}
"""
        
        # Negative prompt to avoid unwanted elements
        prompt["16"]["inputs"]["text"] = """
blurry, low quality, text, watermark, bad anatomy, modern objects, contemporary items
"""
        
        # Random seed for variety
        prompt["7"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)
        
        # Unique filename prefix for this generation
        filename_prefix = f"scene_{int(time.time())}_{random.randint(1000, 9999)}"
        prompt["17"]["inputs"]["filename_prefix"] = filename_prefix
        
        # Queue the prompt
        result = queue_prompt(prompt)
        
        if result and "prompt_id" in result:
            prompt_id = result["prompt_id"]
            print(f"Image generation queued with ID: {prompt_id}")
            
            # Wait for completion
            if wait_for_completion(prompt_id):
                time.sleep(1)  # Small delay to ensure file is written
                
                # Move the generated file to our target location
                if move_generated_files(filename_prefix, image_filename):
                    print(f"Image generated successfully: {image_filename}")
                    return f"/static/images/{image_filename}"
                else:
                    print("Failed to find generated image file")
                    return None
            else:
                print("Image generation timed out")
                return None
        else:
            print("Failed to queue image generation")
            return None
            
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def test_generation():
    """Test function to verify image generation works"""
    print("=== ComfyUI Connection Test ===")
    
    # First, test the connection manually
    print("Testing ComfyUI endpoints...")
    
    # Test different endpoints to see which ones work
    endpoints_to_test = [
        "http://127.0.0.1:8188/",
        "http://127.0.0.1:8188/queue", 
        "http://127.0.0.1:8188/system_stats",
        "http://127.0.0.1:8188/history"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            req = request.Request(endpoint)
            response = request.urlopen(req, timeout=5)
            print(f"✓ {endpoint} - Status: {response.getcode()}")
        except Exception as e:
            print(f"✗ {endpoint} - Error: {e}")
    
    print("\n=== Running check_comfyui_status() ===")
    status = check_comfyui_status()
    print(f"ComfyUI Status: {status}")
    
    if not status:
        print("Cannot proceed with image generation test - ComfyUI not accessible")
        return
    
    print("\n=== Testing Image Generation ===")
    test_scene = "dark dungeon corridor with torch lighting and stone walls"
    result = generate_image_from_text(test_scene)
    if result:
        print(f"Test successful! Image saved to: {result}")
    else:
        print("Test failed!")
