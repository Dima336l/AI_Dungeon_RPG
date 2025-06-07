import ollama

MAX_HISTORY = 6  

def generate_response(history):
    response = ollama.chat(model='llama3:latest', messages=history)
    return response['message']['content']

def main():
    print("Welcome to your AI Dungeon! Type 'exit' to quit, or 'reset' to start a new game.\n")

    dungeon_intro = {
        'role': 'system',
        'content': (
            "You are a dungeon master guiding a player through a dark dungeon. "
            "Speak like a casual human storyteller. Keep replies short and natural, like a conversation. "
            "Give 2 or 3 clear, simple options as choices, no lists or fancy formatting. "
            "Make it feel like a real dialogue."
        )
    }

    conversation_history = [dungeon_intro]

    initial_prompt = (
        "You're standing at the entrance of a dark dungeon. "
        "Say something short and natural, then ask what the player wants to do. "
        "Give 2 or 3 simple options as choices, like a friend talking."
    )
    conversation_history.append({'role': 'user', 'content': initial_prompt})

    ai_intro_response = generate_response(conversation_history)
    conversation_history.append({'role': 'assistant', 'content': ai_intro_response})

    print(f"AI Dungeon: {ai_intro_response}\n")

    while True:
        user_input = input("> You: ").strip().lower()

        if user_input in ['exit', 'quit', 'leave']:
            print("You decide to leave the dungeon. Game over. Goodbye!")
            break

        if user_input in ['reset', 'new game']:
            conversation_history = [dungeon_intro]
            conversation_history.append({'role': 'user', 'content': initial_prompt})

            ai_intro_response = generate_response(conversation_history)
            conversation_history.append({'role': 'assistant', 'content': ai_intro_response})

            print("Game has been reset. You're back at the dungeon entrance.\n")
            print(f"AI Dungeon: {ai_intro_response}\n")
            continue

        conversation_history.append({'role': 'user', 'content': user_input})

        trimmed_history = [dungeon_intro] + conversation_history[-MAX_HISTORY:]

        ai_response = generate_response(trimmed_history)

        conversation_history.append({'role': 'assistant', 'content': ai_response})

        print(f"AI Dungeon: {ai_response}\n")

if __name__ == "__main__":
    main()
