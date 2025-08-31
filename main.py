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
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

def extract_options(ai_text):
    options = {}
    pattern = re.compile(r'^\s*(\d+)[\.\)\-]\s*(.*)$')
    for line in ai_text.splitlines():
        match = pattern.match(line)
        if match:
            num = int(match.group(1))
            text = match.group(2).strip()
            # Remove markdown bold (**option**)
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            options[num] = text
    return options


def remove_options_text(text):
    return "\n".join(
        line for line in text.splitlines() if not re.match(r'^\s*\d+[\.\)\-]', line)
    ).strip()

def generate_response(history):
    response = ollama.chat(model='llama3:latest', messages=history)
    return response['message']['content']

def sanitize_filename(s, max_length=50):
    s = re.sub(r'[<>:"/\\|?*]', '', s)
    s = s.strip().replace(' ', '_')
    return s[:max_length]

def get_scene_image(scene_text):
    enhanced_prompt = enhance_image_prompt(scene_text)
    scene_hash = sanitize_filename(enhanced_prompt)
    cached_image_path = os.path.join(TARGET_DIR, f"{scene_hash}.png")
    if not os.path.exists(cached_image_path):
        return generate_image_from_text(enhanced_prompt)
    else:
        return f"/static/images/{scene_hash}.png"

pending_images = {}

def enhance_image_prompt(scene_text):
    """Enhance the scene text with MMO fantasy style"""
    scene_lower = scene_text.lower()
    
    base_style = "fantasy MMO concept art, vibrant colors, atmospheric lighting, detailed digital painting, cinematic composition"
    
    if any(word in scene_lower for word in ['town', 'village', 'square', 'market']):
        atmosphere = "bustling streets, NPCs, medieval architecture, MMO town hub"
    elif any(word in scene_lower for word in ['field', 'plains', 'forest', 'meadow']):
        atmosphere = "open world environment, lush landscapes, colorful sky, MMORPG field area"
    elif any(word in scene_lower for word in ['dungeon', 'cave', 'crypt']):
        atmosphere = "dark fantasy interior, glowing crystals, MMO dungeon atmosphere"
    elif any(word in scene_lower for word in ['boss', 'raid', 'dragon', 'monster']):
        atmosphere = "epic battle scene, large scale raid boss, dramatic lighting, MMO raid"
    elif any(word in scene_lower for word in ['castle', 'fortress', 'keep']):
        atmosphere = "grand fortress, guild banners, fantasy castle hub"
    elif any(word in scene_lower for word in ['magic', 'spell', 'arcane']):
        atmosphere = "mystical energy, glowing runes, anime-style magic effects"
    else:
        atmosphere = "general MMORPG fantasy atmosphere, vibrant and lively"
    
    return f"{scene_text}, {base_style}, {atmosphere}, professional fantasy MMO art"

def generate_image_async(scene_text, scene_id):
    try:
        enhanced_prompt = enhance_image_prompt(scene_text)
        image_url = generate_image_from_text(enhanced_prompt)
        pending_images[scene_id] = image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        pending_images[scene_id] = None

@app.route("/", methods=["GET"])
def index():
    # Always start fresh for now
    session.clear()

    if 'player' not in session:
        session['player'] = Player().__dict__
        session['history'] = []
        mmo_intro = {
            'role': 'system',
            'content': (
                "You are the AI Game Master of a massive multiplayer online RPG. "
                "Keep responses short and snappy — like NPC dialogue or quick scene descriptions in an MMO. "
                "Do not write long paragraphs. Use 2-4 sentences maximum. "
                "Always give 2 or 3 clear numbered options for the player to choose from. "
                "Keep the style immersive and game-like, as if the player is seeing a live MMO feed. "
                "Occasionally hint at quests, loot, skills, or social interactions to reinforce the MMO feel."
            )
        }
        initial_prompt = (
            "You log into the world of Elaria, a vast fantasy MMO. "
            "You're standing in the lively starter town square, surrounded by adventurers preparing for quests. "
            "Say something short and immersive, then give 3 numbered options for what the player can do next."
        )
        session['history'] = [mmo_intro, {'role': 'user', 'content': initial_prompt}]
        ai_intro_response = generate_response(session['history'])
        session['history'].append({'role': 'assistant', 'content': ai_intro_response})
        session['player_status'] = "HP: 100/100 | MP: 50/50 | Lvl: 1 | Gear: Basic Sword"


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
    data = request.get_json()
    choice_num = data.get('choice')
    free_text = data.get('free_text', "").strip()

    last_ai_msg = session['history'][-1]['content']
    options = extract_options(last_ai_msg)

    # Case 1: User typed something free
    if free_text:
        session['history'].append({'role': 'user', 'content': free_text})
        ai_response = generate_response(session['history'][-(MAX_HISTORY+2):])
        session['history'].append({'role': 'assistant', 'content': ai_response})

    # Case 2: User clicked a numbered option
    elif choice_num and str(choice_num).isdigit():
        choice_num = int(choice_num)
        player_choice_text = options.get(choice_num)

        if player_choice_text:
            session['history'].append({'role': 'user', 'content': player_choice_text})
            ai_response = generate_response(session['history'][-(MAX_HISTORY+2):])
            session['history'].append({'role': 'assistant', 'content': ai_response})
        else:
            return jsonify({
                "scene": "Invalid choice!",
                "options": {},
                "player_status": session.get('player_status', ''),
                "scene_id": None
            })
    else:
        return jsonify({
            "scene": "Invalid input!",
            "options": {},
            "player_status": session.get('player_status', ''),
            "scene_id": None
        })

    # Process response
    scene_text = strip_markdown_bold(remove_options_text(ai_response))
    options = extract_options(ai_response)
    scene_id = f"scene_{len(session['history'])}"

    thread = threading.Thread(target=generate_image_async, args=(scene_text, scene_id))
    thread.daemon = True
    thread.start()

    return jsonify({
        "scene": scene_text,
        "options": options,
        "player_status": session.get('player_status', ''),
        "scene_id": scene_id
    })


@app.route("/get_image/<scene_id>", methods=["GET"])
def get_image(scene_id):
    if scene_id in pending_images:
        return jsonify({"image_url": pending_images[scene_id], "ready": True})
    else:
        return jsonify({"image_url": None, "ready": False})

if __name__ == "__main__":
    app.run(debug=True)
