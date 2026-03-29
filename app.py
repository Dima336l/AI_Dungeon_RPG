from flask import Flask, render_template, request, session, jsonify, redirect, url_for, Response
import webbrowser
import threading
import os
import re
import json
import uuid
from datetime import datetime, timezone
import ollama
from game.player import Player
from generate_images import generate_image_from_text, sanitize_filename as image_png_filename

TARGET_DIR = r"C:\Users\nirca\repos\rpg_dungeon_ai\static\images"

# Start-place options: id, label, image path (under static/images), and initial prompt for the story
START_OPTIONS = [
    {
        "id": "village",
        "label": "Village",
        "image": "images/Start/Village.webp",
        "initial_prompt": (
            "Once upon a time, in a peaceful village by a sunny forest, a young hero sets out on a gentle adventure. "
            "Describe this opening scene in a warm, storybook way using only simple words that a young child can understand. Then give 3 numbered options for what the hero can do next."
        ),
    },
    {
        "id": "forest",
        "label": "Forest",
        "image": "images/Start/Forest.jpg",
        "initial_prompt": (
            "Once upon a time, at the edge of a big friendly forest full of tall trees and soft light, a young hero is ready for an adventure. "
            "Describe this opening scene in a warm, storybook way using only simple words that a young child can understand. Then give 3 numbered options for what the hero can do next."
        ),
    },
    {
        "id": "castle",
        "label": "Castle",
        "image": "images/Start/Castle.avif",
        "initial_prompt": (
            "Once upon a time, in front of a kind castle with towers and a sunny courtyard, a young hero is about to begin an adventure. "
            "Describe this opening scene in a warm, storybook way using only simple words that a young child can understand. Then give 3 numbered options for what the hero can do next."
        ),
    },
    {
        "id": "seaside",
        "label": "Seaside",
        "image": "images/Start/Seaside.jpg",
        "initial_prompt": (
            "Once upon a time, in a little town by the sea with sand and gentle waves, a young hero is ready for an adventure. "
            "Describe this opening scene in a warm, storybook way using only simple words that a young child can understand. Then give 3 numbered options for what the hero can do next."
        ),
    },
]
START_IDS = {o["id"] for o in START_OPTIONS}

# Character options: id, label, image path (under static/images)
CHARACTER_OPTIONS = [
    {"id": "boy", "label": "Boy", "image": "images/Start/boy.png"},
    {"id": "girl", "label": "Girl", "image": "images/Start/girl.png"},
]
CHARACTER_IDS = {o["id"] for o in CHARACTER_OPTIONS}

# Companion options: id, label, image path (under static/images)
COMPANION_OPTIONS = [
    {"id": "dog", "label": "Dog", "image": "images/Start/dog.png"},
    {"id": "cat", "label": "Cat", "image": "images/Start/cat.png"},
]
COMPANION_IDS = {o["id"] for o in COMPANION_OPTIONS}

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for sessions

SOUNDTRACK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "soundtrack")
SOUNDTRACK_EXTS = frozenset({".mp3", ".ogg", ".wav", ".m4a", ".opus", ".webm"})


def soundtrack_static_relpath():
    """Relative path under static/ for the first usable file in static/soundtrack (preferred names first)."""
    if not os.path.isdir(SOUNDTRACK_DIR):
        return None
    preferred = (
        "soundtrack.mp3",
        "music.mp3",
        "background.mp3",
        "theme.mp3",
        "soundtrack.ogg",
        "music.ogg",
        "background.ogg",
    )
    for name in preferred:
        if os.path.isfile(os.path.join(SOUNDTRACK_DIR, name)):
            return f"soundtrack/{name}"
    found = []
    for entry in sorted(os.listdir(SOUNDTRACK_DIR)):
        ext = os.path.splitext(entry.lower())[1]
        if ext in SOUNDTRACK_EXTS:
            found.append(entry)
    if not found:
        return None
    return f"soundtrack/{found[0]}"


@app.context_processor
def inject_soundtrack_url():
    rel = soundtrack_static_relpath()
    return {"soundtrack_music_url": url_for("static", filename=rel) if rel else None}


MAX_HISTORY = 6

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

# === Text Utilities ===
def strip_markdown_bold(text):
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

def remove_options_text(text):
    """Remove numbered options lines from AI output"""
    return "\n".join(
        line for line in text.splitlines() 
        if not re.match(r'^\s*\d+[\.\)\-]', line)
    ).strip()

def extract_options(ai_text):
    """Extract numbered options from AI output"""
    options = {}
    pattern = re.compile(r'^\s*(\d+)[\.\)\-]\s*(.*)$')
    for line in ai_text.splitlines():
        match = pattern.match(line)
        if match:
            num = int(match.group(1))
            text = match.group(2).strip()
            text = strip_markdown_bold(text)
            options[num] = text
    return options


def extract_chapter_title(ai_text):
    """Last non-empty line must be 'Chapter: <short name>' (see system prompt)."""
    if not ai_text:
        return None
    for line in reversed(ai_text.strip().splitlines()):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^Chapter:\s*(.+)$", line, re.IGNORECASE)
        if m:
            title = m.group(1).strip().rstrip(".").strip()
            return (title[:100] if title else None)
    return None


def _strip_trailing_chapter_lines(text):
    lines = text.strip().splitlines()
    while lines and re.match(r"^\s*Chapter:\s*.+$", lines[-1], re.IGNORECASE):
        lines.pop()
    return "\n".join(lines).strip()


def clean_scene_text(text):
    """Remove unwanted 'Scene:' prefixes, options, chapter metadata, and extra whitespace"""
    if not text:
        return ""
    text = strip_markdown_bold(remove_options_text(text))
    text = _strip_trailing_chapter_lines(text)
    text = re.sub(r'^\s*scene\s*[:\-]\s*', '', text, flags=re.IGNORECASE)
    return text.strip()

# === Ollama AI response ===
def generate_response(history):
    response = ollama.chat(model='llama3:latest', messages=history)
    return response['message']['content']

# === Image Utilities ===
# On-disk PNG names must match generate_images.sanitize_filename (MD5 suffix), not a plain truncated string.

def _first_sentences(text, max_chars=380):
    """Take the first 1–2 sentences of scene text for a focused image prompt."""
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    chunk = text[: max_chars + 1]
    last_period = chunk.rfind(". ")
    last_exclamation = chunk.rfind("! ")
    last_question = chunk.rfind("? ")
    cut = max(last_period, last_exclamation, last_question)
    if cut > max_chars // 2:
        return text[: cut + 1].strip()
    # Fallback: cut at last space to avoid mid-word
    last_space = chunk.rfind(" ")
    if last_space > max_chars // 2:
        return text[:last_space].strip()
    return text[:max_chars].strip()


def enhance_image_prompt(scene_text):
    """Build an image prompt that prioritizes the specific story content, then adds style."""
    if not (scene_text and scene_text.strip()):
        return "children's storybook illustration, peaceful village scene, soft colors, kid-friendly"
    # Use the beginning of the scene so the image reflects THIS story moment
    story_lead = _first_sentences(scene_text, max_chars=380)
    # Short style suffix so the model illustrates the story first
    style = "children's storybook illustration, soft colors, warm lighting, kid-friendly fable"
    return f"{story_lead}. {style}"

def get_scene_image(scene_text):
    enhanced_prompt = enhance_image_prompt(scene_text)
    fname = image_png_filename(enhanced_prompt)
    cached_image_path = os.path.join(TARGET_DIR, fname)
    if not os.path.exists(cached_image_path):
        return generate_image_from_text(enhanced_prompt)
    else:
        return f"/static/images/{fname}"

pending_images = {}

EVAL_EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_exports")

# Conversation history is stored server-side: cookie size (~4KB) truncates long games otherwise.
SERVER_HISTORY_LOCK = threading.Lock()
SERVER_HISTORIES: dict[str, list] = {}


def _release_server_history():
    key = session.get("_history_key")
    if key:
        with SERVER_HISTORY_LOCK:
            SERVER_HISTORIES.pop(key, None)


def _game_history() -> list:
    """Mutable chat history for this browser session; not stored in the signed cookie."""
    if "_history_key" not in session:
        session["_history_key"] = str(uuid.uuid4())
        session.modified = True
    key = session["_history_key"]
    with SERVER_HISTORY_LOCK:
        if key not in SERVER_HISTORIES:
            legacy = session.pop("history", None)
            if isinstance(legacy, list) and legacy:
                SERVER_HISTORIES[key] = legacy
                session.modified = True
            else:
                SERVER_HISTORIES[key] = []
        return SERVER_HISTORIES[key]


def _build_session_export_payload():
    """
    Rebuild evaluation payload from session: each assistant turn becomes a scene with text,
    options, prior player action, and on-disk image path (from cached hash filename).
    """
    history = _game_history()
    if len(history) < 3:
        return None

    setup = session.get("setup") or {}
    turns = []
    turn_num = 0

    for idx, msg in enumerate(history):
        if msg.get("role") != "assistant":
            continue
        assistant_content = msg["content"]
        scene_text = clean_scene_text(assistant_content)
        options = extract_options(assistant_content)
        enhanced = enhance_image_prompt(scene_text)
        fname = image_png_filename(enhanced)
        fpath = os.path.join(TARGET_DIR, fname)
        image_rel = f"/static/images/{fname}" if os.path.exists(fpath) else None

        turn_num += 1
        turn = {
            "number": turn_num,
            "scene_text": scene_text,
            "options_offered": options,
            "image_relative_url": image_rel,
            "image_filename": fname,
            "image_on_disk": bool(image_rel),
            "image_generation_prompt_used": enhanced,
        }
        if idx >= 1 and history[idx - 1].get("role") == "user":
            if idx <= 2:
                turn["player_action"] = None
                turn["note"] = "Opening scene after setup (initial user message was combined start/character/companion prompt)"
            else:
                turn["player_action"] = history[idx - 1].get("content", "")
        else:
            turn["player_action"] = None

        turns.append(turn)

    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "game": "fables",
        "setup": {
            "start_place": setup.get("start"),
            "character": setup.get("character"),
            "companion": setup.get("companion"),
        },
        "turn_count": len(turns),
        "turns": turns,
    }


def generate_image_async(scene_text, scene_id):
    try:
        enhanced_prompt = enhance_image_prompt(scene_text)
        image_url = generate_image_from_text(enhanced_prompt)
        pending_images[scene_id] = image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        pending_images[scene_id] = None

# === Routes ===
@app.route("/restart", methods=["GET"])
def restart():
    """Clear session and redirect to start a new game."""
    _release_server_history()
    session.clear()
    return redirect("/", code=302)

def _get_fables_system_prompt():
    return (
        "You are a gentle Storyteller for a children's fables game. Write for young kids (around 5–9 years). "
        "Use SIMPLE, kid-friendly words only. Avoid hard words like: piqued, rustic, mingling, clutches, curiosity, ancient, bustling, tinkle, gaze, slung, and similar. "
        "Use words kids know: happy, big, little, soft, nice, pretty, sunny, cozy, friendly, hold, carry, look, hear, smell, run, walk, and short sentences. "
        "Write friendly, wholesome scene descriptions that are at least 600-700 characters long. "
        "Use a warm, storybook tone. Describe the environment, sounds, and what you see in a way that is vivid but never scary or violent. "
        "Start each scene with clear, concrete details that can be illustrated: who is there (characters, animals), what they are doing, and the specific place (e.g. a little house, a bridge over a stream, a market stall). "
        "Use 4-6 sentences. After the scene description, always give 2 or 3 clear numbered options for the young player to choose from. "
        "Keep the style like a spoken bedtime story—magical, kind, and full of wonder, but with easy words. "
        "Never prefix your responses with 'Scene:'. "
        "Include friendly animals, gentle magic, kind characters, and simple lessons when it fits. "
        "The scene description should be substantial enough to take about 25-30 seconds to read aloud. "
        "After your numbered choices, put one final line by itself (nothing after it) in this exact form: Chapter: <short title> "
        "where <short title> is 3–7 simple words naming this scene as a chapter (e.g. Chapter: The sunny meadow path). "
        "Use 'Chapter:' at the start of that line only."
    )


@app.route("/", methods=["GET"])
def index():
    start_id = request.args.get("start", "").strip().lower()
    character_id = request.args.get("character", "").strip().lower()
    companion_id = request.args.get("companion", "").strip().lower()

    # No start chosen: show the start-place chooser (no session, no Ollama)
    if not start_id:
        return render_template(
            "game.html",
            choose_start=True,
            choose_character=False,
            choose_companion=False,
            start_options=START_OPTIONS,
            scene="",
            options={},
            scene_image="",
            initial_scene_id="",
            player_status="Story: Chapter 1",
        )

    # Invalid start: redirect so user can pick again
    if start_id not in START_IDS:
        return redirect("/", code=302)

    # Start chosen but no character: show character chooser
    if not character_id:
        return render_template(
            "game.html",
            choose_start=False,
            choose_character=True,
            choose_companion=False,
            start_id=start_id,
            character_options=CHARACTER_OPTIONS,
            start_options=START_OPTIONS,
            scene="",
            options={},
            scene_image="",
            initial_scene_id="",
            player_status="Story: Chapter 1",
        )

    # Invalid character: redirect to character step (keep start)
    if character_id not in CHARACTER_IDS:
        return redirect(url_for("index", start=start_id), code=302)

    # Start and character chosen but no companion: show companion chooser
    if not companion_id:
        return render_template(
            "game.html",
            choose_start=False,
            choose_character=False,
            choose_companion=True,
            start_id=start_id,
            character_id=character_id,
            companion_options=COMPANION_OPTIONS,
            start_options=START_OPTIONS,
            scene="",
            options={},
            scene_image="",
            initial_scene_id="",
            player_status="Story: Chapter 1",
        )

    # Invalid companion: redirect to companion step (keep start and character)
    if companion_id not in COMPANION_IDS:
        return redirect(url_for("index", start=start_id, character=character_id), code=302)

    # Start, character and companion chosen: create or reuse session and generate first scene
    if "player" not in session:
        _release_server_history()
        session.clear()
    if "player" not in session:
        session["player"] = Player().__dict__
        h = _game_history()
        h.clear()

        prompt_for_start = next((o["initial_prompt"] for o in START_OPTIONS if o["id"] == start_id), START_OPTIONS[0]["initial_prompt"])
        character_line = "The young hero is a boy. " if character_id == "boy" else "The young hero is a girl. "
        companion_line = "The hero has a friendly dog as a companion. " if companion_id == "dog" else "The hero has a friendly cat as a companion. "
        user_prompt = character_line + companion_line + prompt_for_start
        fables_intro = {"role": "system", "content": _get_fables_system_prompt()}
        h.append(fables_intro)
        h.append({"role": "user", "content": user_prompt})
        try:
            ai_intro_response = generate_response(h)
        except ConnectionError:
            return render_template("ollama_error.html")
        h.append({"role": "assistant", "content": ai_intro_response})
        session["story_chapter_index"] = 1
        ch1 = extract_chapter_title(ai_intro_response)
        session["player_status"] = (
            f"Story: Chapter 1 — {ch1}" if ch1 else "Story: Chapter 1 — Your tale has begun"
        )
        session["setup"] = {
            "start": start_id,
            "character": character_id,
            "companion": companion_id,
        }
        session.modified = True

    h = _game_history()
    # History lives in RAM; after a server restart the cookie may still have "player" but h is empty.
    if not h:
        session.clear()
        return redirect(
            url_for(
                "index",
                start=start_id,
                character=character_id,
                companion=companion_id,
            ),
            code=302,
        )
    if h[-1].get("role") != "assistant":
        return render_template("ollama_error.html")
    last_ai_msg = h[-1]["content"]
    scene_text = clean_scene_text(last_ai_msg)
    options = extract_options(last_ai_msg)

    enhanced = enhance_image_prompt(scene_text)
    image_fname = image_png_filename(enhanced)
    cached_image_path = os.path.join(TARGET_DIR, image_fname)
    if os.path.exists(cached_image_path):
        scene_image_url = f"/static/images/{image_fname}"
        initial_scene_id = None
    else:
        scene_image_url = ""
        initial_scene_id = "scene_initial"
        thread = threading.Thread(target=generate_image_async, args=(scene_text, initial_scene_id))
        thread.daemon = True
        thread.start()

    return render_template(
        "game.html",
        choose_start=False,
        choose_character=False,
        choose_companion=False,
        scene=scene_text,
        options=options,
        player_status=session["player_status"],
        scene_image=scene_image_url,
        initial_scene_id=initial_scene_id,
    )

@app.route("/make_choice", methods=["POST"])
def make_choice():
    data = request.get_json()
    choice_num = data.get('choice')
    free_text = data.get('free_text', "").strip()

    h = _game_history()
    if not h or h[-1].get("role") != "assistant":
        return (
            jsonify(
                {
                    "error": "session_lost",
                    "message": "Story session expired (e.g. server restarted). Refresh the page to continue.",
                }
            ),
            410,
        )
    last_ai_msg = h[-1]["content"]
    options = extract_options(last_ai_msg)

    # User typed free text
    if free_text:
        h.append({'role': 'user', 'content': free_text})
        try:
            ai_response = generate_response(h[-(MAX_HISTORY + 2) :])
        except ConnectionError:
            return jsonify({"error": "ollama", "message": "Ollama is not running. Start Ollama or run launch_rpg_dungeon.bat, then retry."}), 503
        h.append({'role': 'assistant', 'content': ai_response})

    # User clicked numbered option
    elif choice_num and str(choice_num).isdigit():
        choice_num = int(choice_num)
        player_choice_text = options.get(choice_num)

        if player_choice_text:
            h.append({'role': 'user', 'content': player_choice_text})
            try:
                ai_response = generate_response(h[-(MAX_HISTORY + 2) :])
            except ConnectionError:
                return jsonify({"error": "ollama", "message": "Ollama is not running. Start Ollama or run launch_rpg_dungeon.bat, then retry."}), 503
            h.append({'role': 'assistant', 'content': ai_response})
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

    nxt = session.get("story_chapter_index", 1) + 1
    session["story_chapter_index"] = nxt
    ch_title = extract_chapter_title(ai_response)
    session["player_status"] = (
        f"Story: Chapter {nxt} — {ch_title}" if ch_title else f"Story: Chapter {nxt}"
    )
    session.modified = True

    scene_text = clean_scene_text(ai_response)
    options = extract_options(ai_response)
    scene_id = f"scene_{len(h)}"

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


@app.route("/export_session", methods=["GET"])
def export_session():
    """
    Export full session for AI/human evaluation: scene text, options, player actions,
    and image paths. Saves a copy under eval_exports/.
    """
    payload = _build_session_export_payload()
    if payload is None:
        return (
            jsonify(
                {
                    "error": "no_session",
                    "message": "No playable session to export. Finish start/character/companion selection and play at least one scene.",
                }
            ),
            400,
        )

    os.makedirs(EVAL_EXPORT_DIR, exist_ok=True)
    safe_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    server_path = os.path.join(EVAL_EXPORT_DIR, f"fables_eval_{safe_ts}.json")
    try:
        payload["saved_to_server_path"] = server_path
        with open(server_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except OSError as e:
        payload["saved_to_server_path"] = None
        payload["save_error"] = str(e)

    body = json.dumps(payload, indent=2, ensure_ascii=False)
    download = request.args.get("download", "").lower() in ("1", "true", "yes")
    if download:
        return Response(
            body,
            mimetype="application/json; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="fables_eval_{safe_ts}.json"',
            },
        )
    return Response(body, mimetype="application/json; charset=utf-8")


if __name__ == "__main__":
    app.run(debug=True)
