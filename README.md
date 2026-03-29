# 🏰 RPG Dungeon AI — Local Deployment & Demo

## Requirements
- Windows 10/11, Python 3.10+, RTX 5090 recommended
- Virtual environment (venv)
- Ngrok account for public access

## 1️⃣ Clone & Setup
```bash
git clone https://github.com/yourusername/rpg_dungeon_ai.git
cd C:\Users\nirca\repos\rpg_dungeon_ai
python -m venv ai_dungeon_env
ai_dungeon_env\Scripts\activate
pip install -r requirements.txt
```

## 2️⃣ Start ComfyUI (Image Generation)
```bash
cd C:\Users\nirca\repos\ComfyUI-master
python main.py
```
Keep this running; ComfyUI listens at http://127.0.0.1:8188

## 3️⃣ Start Ollama (Text Generation)
```bash
cd C:\Users\nirca\repos\rpg_dungeon_ai
ollama serve
```
Keep this running; Flask depends on it.

## 4️⃣ Run Flask Game Server
```bash
cd C:\Users\nirca\repos\rpg_dungeon_ai
ai_dungeon_env\Scripts\activate
set FLASK_APP=main.py
flask run --host=0.0.0.0 --port=5000
```
Access locally: http://127.0.0.1:5000

## 5️⃣ Expose via Ngrok
```bash
ngrok config add-authtoken YOUR_NGROK_TOKEN
ngrok http 5000
```
Share the public URL from ngrok to let others play.

## ⚠️ Notes
- Start in this order: ComfyUI → Ollama → Flask → ngrok
- Keep your PC running during demo
- Free ngrok URLs change each session
- Generated images are cached in `static/images` to speed up repeated scenes
 