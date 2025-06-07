from flask import Flask, render_template, request, session
import webbrowser
import threading
import os
import re
import ollama
from game.player import Player

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for sessions

MAX_HISTORY = 6

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

def strip_markdown_bold(text):
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

def generate_response(history):
    response = ollama.chat(model='llama3:latest', messages=history)
    return response['message']['content']

def extract_options(ai_text):
    options = {}
    pattern = re.compile(r'^\s*(\d+)[\.\)\-]\s*(.*)$')
    for line in ai_text.splitlines():
        match = pattern.match(line)
        if match:
            num = int(match.group(1))
            text = match.group(2).strip()
            options[num] = text
    return options

@app.route("/", methods=["GET", "POST"])
def index():
    if 'player' not in session:
        session['player'] = Player().__dict__  # Save minimal player data
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
        initial_prompt = "You're standing at the entrance of a dark dungeon. Say something short and natural, then give 3 simple numbered options for the player."
        session['history'] = [dungeon_intro, {'role':'user', 'content':initial_prompt}]
        ai_intro_response = generate_response(session['history'])
        session['history'].append({'role':'assistant','content': ai_intro_response})
        session['player_status'] = f"Health: 100/100 | Inventory: Nothing"
        options = extract_options(ai_intro_response)
        scene_text = strip_markdown_bold(ai_intro_response)

    if request.method == "POST":
        choice_num = int(request.form.get("choice"))
        last_ai_msg = session['history'][-1]['content']
        options = extract_options(last_ai_msg)
        player_choice_text = options.get(choice_num)

        if player_choice_text:
            session['history'].append({'role':'user','content': player_choice_text})
            ai_response = generate_response(session['history'][-(MAX_HISTORY+2):])
            session['history'].append({'role':'assistant','content': ai_response})
            scene_text = strip_markdown_bold(ai_response)
            options = extract_options(ai_response)
        else:
            scene_text = "Invalid choice!"
            options = {}

        return render_template("game.html", scene=scene_text, options=options, player_status=session['player_status'])

    last_ai_msg = session['history'][-1]['content']
    options = extract_options(last_ai_msg)
    scene_text = strip_markdown_bold(last_ai_msg)
    return render_template("game.html", scene=scene_text, options=options, player_status=session['player_status'])

if __name__ == "__main__":
    # Only open browser if running in the reloader process (to avoid errors on Windows)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.5, open_browser).start()

    app.run(debug=True)
