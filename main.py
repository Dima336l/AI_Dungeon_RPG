from flask import Flask, render_template, request, session, jsonify
import webbrowser
import threading
import os
import re
import ollama
from game.player import Player
from generate_images import generate_image_from_text

TARGET_DIR = r"C:\Users\nirca\repos\rpg_dungeon_ai\static\images"

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for sessions

MAX_HISTORY = 6

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

def strip_markdown_bold(text):
    # Remove markdown bold **text**
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

def extract_options(ai_text):
    # Extract numbered options like:
    # 1. Option text
    # 2) Option text
    # 3- Option text
    options = {}
    pattern = re.compile(r'^\s*(\d+)[\.\)\-]\s*(.*)$')
    for line in ai_text.splitlines():
        match = pattern.match(line)
        if match:
            num = int(match.group(1))
            text = match.group(2).strip()
            options[num] = text
    return options

def remove_options_text(text):
    # Remove lines starting with numbered options, so scene text is clean
    return "\n".join(
        line for line in text.splitlines() if not re.match(r'^\s*\d+[\.\)\-]', line)
    ).strip()

def generate_response(history):
    # Call ollama chat with message history, return assistant reply content
    response = ollama.chat(model='llama3:latest', messages=history)
    return response['message']['content']

def sanitize_filename(s, max_length=50):
    s = re.sub(r'[<>:"/\\|?*]', '', s)
    s = s.strip().replace(' ', '_')
    return s[:max_length]

# Helper function to generate or fetch cached scene image
def get_scene_image(scene_text):
    scene_hash = sanitize_filename(scene_text)
    cached_image_path = os.path.join(TARGET_DIR, f"{scene_hash}.png")
    if not os.path.exists(cached_image_path):
        # Generate new image if not cached
        return generate_image_from_text(scene_text)
    else:
        return f"/static/images/{scene_hash}.png"

@app.route("/", methods=["GET"])
def index():
    # Initialize session on first visit
    if 'player' not in session:
        session['player'] = Player().__dict__  # Minimal player info
        session['history'] = []
        dungeon_intro = {
            'role': 'system',
            'content': (
                "You are a dungeon master guiding the player through a dark dungeon. "
                "Always give 2 or 3 clear numbered options for the player to choose from. "
                "Keep your responses short, punchy, and conversational. "
                "Describe scenes briefly with vivid but minimal detail."
            )
        }
        initial_prompt = (
            "You're standing at the entrance of a dark dungeon. Say something short and natural, "
            "then give 3 simple numbered options for the player."
        )
        session['history'] = [dungeon_intro, {'role': 'user', 'content': initial_prompt}]
        ai_intro_response = generate_response(session['history'])
        session['history'].append({'role': 'assistant', 'content': ai_intro_response})
        session['player_status'] = "Health: 100/100 | Inventory: Nothing"

    # GET request - render initial or current scene and options
    last_ai_msg = session['history'][-1]['content']
    scene_text = strip_markdown_bold(remove_options_text(last_ai_msg))
    options = extract_options(last_ai_msg)
    scene_image_url = get_scene_image(scene_text)

    return render_template(
        "game.html",
        scene=scene_text,
        options=options,
        player_status=session['player_status'],
        scene_image=scene_image_url
    )

@app.route("/make_choice", methods=["POST"])
def make_choice():
    # Handle AJAX choice requests
    data = request.get_json()
    choice_num = data.get('choice')
    
    if not choice_num or not str(choice_num).isdigit():
        return jsonify({
            "scene": "Invalid choice!",
            "options": {},
            "player_status": session.get('player_status', ''),
            "scene_image": None
        })

    choice_num = int(choice_num)
    last_ai_msg = session['history'][-1]['content']
    options = extract_options(last_ai_msg)
    player_choice_text = options.get(choice_num)

    if player_choice_text:
        # Append player's choice to history
        session['history'].append({'role': 'user', 'content': player_choice_text})

        # Generate AI response with recent history window
        ai_response = generate_response(session['history'][-(MAX_HISTORY+2):])
        session['history'].append({'role': 'assistant', 'content': ai_response})

        # Clean scene text and options
        scene_text = strip_markdown_bold(remove_options_text(ai_response))
        options = extract_options(ai_response)

        # Generate the scene image **after the AI response**
        scene_image_url = generate_image_from_text(scene_text)

        return jsonify({
            "scene": scene_text,
            "options": options,
            "player_status": session.get('player_status', ''),
            "scene_image": scene_image_url
        })
    else:
        return jsonify({
            "scene": "Invalid choice!",
            "options": {},
            "player_status": session.get('player_status', ''),
            "scene_image": None
        })

if __name__ == "__main__":
    app.run(debug=True)