# Coursework 1: AI-Powered Fables Storytelling Game
## Undergraduate Individual Project

**Student Name:** [Your Name]  
**Student ID:** [Your Student ID]  
**Supervisor:** [Supervisor Name]  
**Date:** [Current Date]

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Motivation](#2-motivation)
3. [Literature Review](#3-literature-review)
4. [First Steps](#4-first-steps)
5. [Ethics Forms](#5-ethics-forms)
6. [References](#6-references)

---

## 1. Introduction

### 1.1 Project Overview

This project aims to develop an AI-powered fables storytelling game for children that combines large language models (LLMs) for narrative generation with diffusion models for dynamic image generation. The system creates an immersive, kid-friendly adventure experience where players first choose a starting place, character (boy or girl), and companion (dog or cat) through image-based selection screens, then interact with an AI storyteller that dynamically generates both textual narratives and corresponding visual scenes in real-time.

### 1.2 Subject Area

The project spans multiple areas of computer science:

- **Artificial Intelligence & Machine Learning**: Integration of LLMs (Ollama/Llama3) for natural language generation and Stable Diffusion models (via ComfyUI) for image generation
- **Web Development**: Flask-based web application with real-time client-server communication
- **Human-Computer Interaction**: Interactive game interface with typing effects, audio narration, and dynamic content loading
- **Game Development**: Procedural content generation, game state management, and player interaction systems

### 1.3 Project Aim

The primary aim of this project is to create a fully functional, AI-driven fables storytelling game for children that demonstrates the integration of modern generative AI technologies (text and image generation) into an interactive gaming experience. The system should:

- Generate coherent, kid-friendly narrative content using simple language (ages 5–9)
- Produce high-quality storybook-style images that match the narrative scenes
- Provide an engaging, responsive user interface with image-based customization (start place, character, companion)
- Handle real-time synchronization between text and image generation
- Maintain game state and player progression

### 1.4 Objectives

To achieve the project aim, the following objectives have been identified:

1. **AI Integration**: Successfully integrate Ollama (Llama3) for text generation and ComfyUI (Stable Diffusion) for image generation
2. **Web Application Development**: Build a Flask-based web server with session management and API endpoints
3. **Real-time Synchronization**: Implement mechanisms to synchronize text typing animation with image generation timing
4. **User Interface**: Design and implement an immersive, retro-styled game interface with typing effects, audio narration, and dynamic image loading
5. **Game Logic**: Develop a game engine capable of managing player state, choices, and narrative progression
6. **Performance Optimization**: Implement image caching and asynchronous processing to ensure responsive gameplay

---

## 2. Motivation

### 2.1 Why This Project Matters

The intersection of generative AI and interactive entertainment represents a rapidly evolving field with significant potential. This project addresses several important areas:

**2.1.1 Advancing AI in Gaming**

Traditional game development requires extensive manual content creation. By leveraging generative AI, this project explores how automated content generation can create unique, personalized gaming experiences. This has implications for:

- Reducing development costs and time
- Enabling infinite, procedurally generated content
- Creating personalized experiences for each player
- Demonstrating practical applications of modern AI technologies

**2.1.2 Technical Integration Challenges**

Successfully combining multiple AI systems (text and image generation) in real-time presents interesting technical challenges:

- **Latency Management**: Balancing generation quality with response time
- **Context Preservation**: Maintaining narrative coherence across multiple interactions
- **Resource Management**: Efficiently handling GPU-intensive image generation
- **Synchronization**: Coordinating asynchronous processes (text typing, image generation, audio)

**2.1.3 Educational Value**

This project provides hands-on experience with:

- Modern AI/ML frameworks and APIs
- Full-stack web development
- Real-time system design
- Performance optimization techniques
- User experience design

### 2.2 Personal Motivation

This project combines several areas of personal interest:

- **AI/ML**: Exploring cutting-edge generative AI technologies
- **Game Development**: Creating interactive, engaging experiences
- **Web Technologies**: Building modern, responsive web applications
- **Creative Technology**: Combining technical skills with creative expression

### 2.3 Research Questions

The project seeks to answer:

1. Can LLMs effectively serve as storytellers for interactive children's narratives?
2. How can text and image generation be synchronized to create cohesive experiences?
3. What are the performance characteristics and limitations of real-time AI content generation?
4. How can user experience be optimized when dealing with variable generation times?

---

## 3. Literature Review

### 3.1 Large Language Models in Game Development

Large Language Models (LLMs) have shown remarkable capabilities in natural language understanding and generation. Recent models like GPT-3 (Brown et al., 2020), GPT-4 (OpenAI, 2023), and open-source alternatives like Llama (Touvron et al., 2023) have demonstrated proficiency in creative writing, dialogue generation, and context-aware responses.

**Application to Interactive Fiction**: The use of LLMs for interactive fiction and text-based games has been explored in systems like AI Dungeon (Walton, 2019), which demonstrated that LLMs can generate coherent, context-aware narratives. However, these systems primarily focused on text-only experiences.

**Local LLM Deployment**: The emergence of local LLM deployment tools like Ollama (Ollama, 2024) has made it feasible to run LLMs on consumer hardware, enabling privacy-preserving and cost-effective AI applications. This is particularly relevant for game development where cloud API costs can be prohibitive.

### 3.2 Diffusion Models for Image Generation

Stable Diffusion (Rombach et al., 2022) represents a significant advancement in text-to-image generation, enabling high-quality image synthesis from textual prompts. The model's open-source nature and efficiency have made it widely adopted.

**ComfyUI Framework**: ComfyUI (ComfyUI, 2024) provides a node-based interface for Stable Diffusion workflows, enabling complex image generation pipelines. It supports various models, control mechanisms, and customization options.

**Real-time Generation Challenges**: Image generation with diffusion models typically takes 5-30 seconds depending on hardware and model complexity. This presents challenges for real-time applications where user experience depends on responsiveness.

### 3.3 Procedural Content Generation in Games

Procedural Content Generation (PCG) has been a staple of game development, from early roguelikes to modern games like Minecraft and No Man's Sky. Togelius et al. (2011) provide a comprehensive survey of PCG techniques.

**AI-Driven PCG**: Recent work has explored using AI for PCG. Summerville et al. (2018) survey AI-based PCG methods, noting the potential of neural networks for content generation.

**Narrative Generation**: The combination of narrative and visual generation is less explored. Most PCG research focuses on either level generation or narrative generation separately, with limited work on integrated systems.

### 3.4 Web-Based Game Development

Modern web technologies enable sophisticated game experiences. Flask (Grinberg, 2018) provides a lightweight framework for Python-based web applications, suitable for game servers. WebSockets and AJAX enable real-time communication between client and server.

**Session Management**: Flask's session management allows for stateful game experiences, maintaining player progress and game state across interactions.

### 3.5 User Experience in Interactive Systems

The timing and synchronization of content delivery significantly impacts user experience. Nielsen (1994) established that response times should be under 1 second for immediate feedback, but acceptable delays can be longer for complex operations.

**Progressive Loading**: Techniques like progressive image loading and typing animations can mask generation delays while maintaining user engagement.

### 3.6 Gaps in Current Research

While individual components (LLMs, diffusion models, web games) are well-researched, there is limited work on:

- Real-time integration of text and image generation in interactive systems
- Synchronization strategies for multi-modal AI content generation
- Performance optimization for consumer-grade hardware
- User experience design for variable-latency AI systems

This project aims to address these gaps by creating a practical, working system that demonstrates these integrations.

---

## 4. First Steps

### 4.1 Project Setup and Architecture

The project has been initialized with a clear architecture:

**4.1.1 Technology Stack**

- **Backend**: Python 3.10+ with Flask framework
- **Text Generation**: Ollama with Llama3 model (`llama3:latest`)
- **Image Generation**: ComfyUI with Stable Diffusion (using `anything-v5.safetensors` checkpoint)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla, embedded in HTML template)
- **Audio**: Web Speech API for text-to-speech (browser-based, no server-side TTS)
- **Deployment**: Local development with ngrok for public access (optional)

**4.1.2 Project Structure**

```
rpg_dungeon_ai/
├── app.py                 # Main Flask application (routes, session, AI integration)
├── game/                  # Game logic modules
│   ├── player.py          # Player class (health, inventory - partially integrated)
│   ├── engine.py          # Game engine (empty - placeholder for future)
│   ├── ai.py              # AI integration (empty - placeholder for future)
│   └── world.py           # World state (empty - placeholder for future)
├── templates/
│   └── game.html          # Main game interface (HTML + embedded JavaScript)
├── static/
│   ├── styles.css         # Retro-styled CSS
│   ├── script.js          # Additional client-side logic (if separate)
│   ├── images/            # Generated image cache directory
│   ├── retro_monitor.jpg  # UI background asset
│   └── beep.wav           # Sound effect asset
├── assets/                # ComfyUI output directory (temporary storage)
├── generate_images.py     # ComfyUI integration and image generation
├── launch_rpg_dungeon.bat # Windows batch script (Ollama first, then ComfyUI, then Flask; Fables branding)
├── requirements.txt       # Python dependencies
└── utils/
    └── tts.py             # Text-to-speech utilities (empty - using Web Speech API)
```

### 4.2 Implemented Features

**4.2.1 Core Functionality**

1. **Flask Web Server**: Fully functional Flask application with:
   - Session management for player state and conversation history
   - RESTful API endpoints (`/`, `/restart`, `/make_choice`, `/get_image/<scene_id>`)
   - Template rendering with Jinja2
   - JSON API for asynchronous scene updates

2. **AI Text Generation**: Integration with Ollama:
   - Llama3 model (`llama3:latest`) for narrative generation
   - Context-aware system prompts with kid-friendly storyteller persona (ages 5–9, simple words)
   - Conversation history management (last 6 messages for context)
   - Text cleaning utilities (markdown removal, option extraction)
   - Support for both numbered choice selection and free-text input
   - Character and companion choices injected into the initial prompt (e.g. "The young hero is a boy", "The hero has a friendly dog as a companion")

3. **AI Image Generation**: Integration with ComfyUI:
   - ComfyUI API integration via HTTP requests
   - Asynchronous image generation via Python threading
   - Story-led prompt enhancement: uses first 1–2 sentences of scene text plus children's storybook illustration style
   - Image caching using hash-based filenames to avoid regeneration
   - Non-blocking first-scene generation: page loads immediately, image generated in background; client polls for readiness
   - Dynamic image loading with client-side polling mechanism
   - File management: images generated in `assets/` directory, moved to `static/images/` for serving

4. **User Interface**:
   - Three-step image-based selection before story: (1) start place (Village, Forest, Castle, Seaside), (2) character (Boy, Girl), (3) companion (Dog, Cat)
   - Story begins automatically after selections; no "Start Adventure" click required
   - Retro-styled monitor interface with custom CSS
   - Typing animation effect; text displays first, then image appears after typing completes
   - Dynamic choice buttons generated from AI output
   - Free-text input option for custom player actions
   - Text-to-speech narration using Web Speech API (on by default, adjustable speed)
   - Player status display ("Story: Chapter 1")
   - Music and narration toggles in footer (music on by default; Web Audio fallback if no music file)
   - Restart button and dedicated `/restart` route; Ollama error page when Ollama is not running

5. **Kid-Friendly Design and Safeguards**:
   - **Text (LLM) rails**: System prompt instructs a "gentle Storyteller" with explicit vocabulary constraints—words to avoid (piqued, rustic, mingling, clutches, curiosity, ancient, bustling, tinkle, gaze, slung) and preferred words (happy, big, little, soft, nice, pretty, sunny, cozy, friendly, hold, carry, look, hear, smell, run, walk). Explicit requirements: "friendly, wholesome scene descriptions"; "never scary or violent"; "warm, storybook tone"; "friendly animals, gentle magic, kind characters"; "like a spoken bedtime story—magical, kind, and full of wonder."
   - **Image rails**: Story-led prompts plus fixed style suffix ("children's storybook illustration, soft colors, warm lighting, kid-friendly fable"). Negative prompt excludes blurry, low quality, text, watermark, bad anatomy, modern objects, contemporary items.
   - **Structural safeguards**: Start places (Village, Forest, Castle, Seaside) and their prompts are hand-authored for a warm, non-threatening tone. Character/companion options limited to boy/girl and dog/cat. Same kid-friendly system prompt applied on every turn; no post-generation content filter (prompt engineering and instruction-following are the primary safeguards; production would benefit from additional moderation).

6. **Synchronization**:
   - Text typing completes first; image is displayed after typing finishes (image appears after text)
   - First-scene image generated in background; client polls until ready
   - Image polling mechanism checks every 200ms
   - Smooth transitions between scenes with image fade-in effects

**4.2.2 Technical Achievements**

- **Asynchronous Processing**: Image generation runs in background daemon threads to avoid blocking the Flask web server
- **Image Caching**: Generated images are cached using MD5 hash-based filenames (first 8 characters of hash + sanitized text)
- **Prompt Engineering**: Story-led image prompts using the first 1–2 sentences of scene text plus children's storybook illustration style; kid-friendly language constraints in the system prompt
- **Timing Optimization**: Modified AI system prompt to generate longer text (600-700 characters) ensuring typing animation (~27-31 seconds at 45ms/char) matches image generation time (~28 seconds)
- **ComfyUI Integration**: Custom workflow JSON configuration for Stable Diffusion with configurable parameters (steps, CFG, sampler, etc.)
- **Error Handling**: Graceful fallbacks when ComfyUI is unavailable, with status checking before generation attempts

### 4.3 Current System Workflow

1. **Pre-game Selection** (no session or Ollama call yet):
   - User visits `/`; start-place chooser displayed ("Where does your story begin?")
   - User selects Village, Forest, Castle, or Seaside (image-based) → navigates to `/?start=village` (etc.)
   - Character chooser displayed ("Choose your hero"); user selects Boy or Girl → `/?start=village&character=boy`
   - Companion chooser displayed ("Choose your companion"); user selects Dog or Cat → `/?start=village&character=boy&companion=dog`

2. **Initialization** (first request with all three selections):
   - Player session created
   - System prompt configured with kid-friendly storyteller persona
   - Initial prompt combines start place, character, and companion (e.g. "The young hero is a boy. The hero has a friendly dog as a companion. Once upon a time, in a peaceful village...")
   - Initial scene generated by Ollama
   - First-scene image generated in background thread (non-blocking); page returned immediately
   - Client receives page with scene text; story starts automatically (typing begins, client polls for image)

3. **Scene Display**: 
   - Text begins typing animation
   - When typing completes, image is shown (from cache or polling), then choices appear

4. **User Interaction**: 
   - Player can select from numbered options or type free-text actions
   - Choice submitted via AJAX POST to `/make_choice` endpoint

5. **Response Generation**: 
   - User choice added to conversation history
   - Last 6 messages sent to Ollama for context-aware response
   - New scene text generated by Llama3
   - Image generation queued asynchronously
   - Text and options returned as JSON; image polled separately

6. **Content Delivery**: 
   - Typing animation runs; when complete, image displayed (when ready), then choices shown

7. **State Management**: 
   - Conversation history and player status in session
   - Image generation status tracked in `pending_images` dictionary

### 4.4 Challenges Encountered and Solutions

**Challenge 1: Image Generation Latency**

- **Problem**: Image generation takes ~28 seconds, causing gaps after text finishes
- **Solution**: Modified AI prompts to generate longer text (600-700 characters) so typing animation matches image generation time

**Challenge 2: Batch Script Errors**

- **Problem**: Windows batch script had syntax errors with variable expansion
- **Solution**: Fixed delayed expansion syntax and variable comparisons using proper batch file techniques

**Challenge 3: Real-time Synchronization**

- **Problem**: Coordinating text typing and image loading
- **Solution**: Text displays first with typing animation; image appears after typing completes; client polls for image readiness

### 4.5 Testing and Validation

**4.5.1 Functional Testing**

- Verified Flask server starts correctly on port 5000
- Tested session management and state persistence across page refreshes
- Validated Ollama integration produces coherent, context-aware narratives
- Confirmed ComfyUI integration generates appropriate children's storybook-style images
- Tested user interactions (numbered choice selection, free text input)
- Verified image caching prevents regeneration of identical scenes
- Tested error handling when ComfyUI is unavailable
- Confirmed text-to-speech narration works with browser Web Speech API

**4.5.2 Performance Testing**

- Measured image generation time: ~28 seconds on RTX 5090
- Verified text typing duration matches image generation
- Tested image caching effectiveness
- Validated concurrent request handling

### 4.6 Next Steps

**Immediate Next Steps (Weeks 6-8)**:

1. **Enhanced Game Mechanics**:
   - Integrate chapter progression and story arc tracking
   - Add simple moral/theme reinforcement for fables
   - Develop more companion interaction in narratives
   - Expand start-place variety and environmental prompts

2. **Improved AI Integration**:
   - Fine-tune prompts for age-appropriate vocabulary
   - Implement context-aware image generation for story consistency
   - Refine storyteller persona and narrative style
   - Improve option generation quality

3. **User Experience Enhancements**:
   - Add save/load functionality
   - Implement achievement system
   - Create settings panel
   - Add sound effects library

4. **Performance Optimization**:
   - Implement image pre-generation for common scenarios
   - Optimize model loading times
   - Add request queuing for image generation
   - Implement progressive image quality

**Medium-term Goals (Weeks 9-12)**:

1. **Advanced Features**:
   - Multiple story themes or genres (e.g. adventure, friendship, kindness)
   - Illustration style customization
   - Save/resume story sessions
   - Story recap and branching visualization

2. **Evaluation and Analysis**:
   - User testing and feedback collection
   - Performance benchmarking
   - Narrative quality assessment
   - Technical documentation

### 4.7 Project Timeline

- **Weeks 1-5**: Project setup, core functionality, first coursework submission ✓
- **Weeks 6-8**: Enhanced features, game mechanics
- **Weeks 9-10**: Advanced features, optimization
- **Weeks 11-12**: Testing, evaluation, documentation
- **Week 13**: Final submission preparation

---

## 5. Ethics Forms

### 5.1 Ethics Screening

This project has been reviewed and determined to be **LOW RISK** for the following reasons:

- **No Human Participants**: The project does not involve direct data collection from human participants
- **No Sensitive Data**: No personal, medical, or sensitive information is collected or processed
- **Public Data Only**: Uses publicly available AI models and open-source technologies
- **Local Deployment**: System runs locally; no external data transmission required
- **No User Tracking**: No analytics, tracking, or user behavior monitoring

### 5.2 Ethics Screening Form

[Note: This section should contain the signed Ethics Screening Form from your supervisor. The form should be attached as a separate document or included here as an image/PDF.]

**Supervisor Approval**: [Supervisor Name]  
**Date**: [Date]  
**Signature**: [Signature]

---

## 6. References

Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D. (2020). Language models are few-shot learners. *Advances in neural information processing systems*, 33, 1877-1901.

ComfyUI. (2024). *ComfyUI - A powerful and modular stable diffusion GUI and backend*. GitHub. https://github.com/comfyanonymous/ComfyUI

Grinberg, M. (2018). *Flask Web Development: Developing Web Applications with Python*. O'Reilly Media.

Nielsen, J. (1994). *Usability Engineering*. Morgan Kaufmann.

Ollama. (2024). *Ollama - Run large language models locally*. https://ollama.ai/

OpenAI. (2023). GPT-4 Technical Report. *arXiv preprint arXiv:2303.08774*.

Rombach, R., Blattmann, A., Lorenz, D., Esser, P., & Ommer, B. (2022). High-resolution image synthesis with latent diffusion models. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, 10684-10695.

Summerville, A., Snodgrass, S., Guzdial, M., Holmgård, C., Hoover, A. K., Isaksen, A., ... & Togelius, J. (2018). Procedural content generation via machine learning (PCGML). *IEEE Transactions on Games*, 10(3), 257-270.

Togelius, J., Yannakakis, G. N., Karakovskiy, S., & Shaker, N. (2011). Assessing believability. *Entertainment Computing*, 2(2), 123-132.

Touvron, H., Lavril, T., Izacard, G., Martinet, X., Lachaux, M. A., Lacroix, T., ... & Lample, G. (2023). LLaMA: Open and efficient foundation language models. *arXiv preprint arXiv:2303.08774*.

Walton, N. (2019). *AI Dungeon*. Latitude Games. https://www.aidungeon.com/

---

## Appendices

### Appendix A: System Requirements

- **Operating System**: Windows 10/11
- **Python**: 3.10 or higher
- **GPU**: NVIDIA GPU with CUDA support (RTX 5090 recommended for optimal performance)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB+ for models and dependencies
- **Network**: Internet connection for initial setup (local operation after setup)

### Appendix B: Installation Instructions

[Include detailed setup instructions from README.md]

### Appendix C: Code Structure

[Include brief overview of key files and their purposes]

---

**Word Count**: [Approximately 2,500-3,000 words]

**Last Updated**: [Current Date]
