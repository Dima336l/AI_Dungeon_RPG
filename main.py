import ollama
import re
from game.player import Player



MAX_HISTORY = 6


def strip_markdown_bold(text):
    # Removes **bold** markers
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

def generate_response(history):
    response = ollama.chat(model='llama3:latest', messages=history)
    return response['message']['content']

def extract_options(ai_text):
    """
    Extract options from the AI's response.
    Looks for lines starting with number + '.', ')', or '-'
    Returns a dict mapping option number (int) to option text.
    """
    options = {}
    pattern = re.compile(r'^\s*(\d+)[\.\)\-]\s*(.*)$')
    for line in ai_text.splitlines():
        match = pattern.match(line)
        if match:
            num = int(match.group(1))
            text = match.group(2).strip()
            options[num] = text
    return options

def main():
    player = Player()
    print("Welcome to your AI Dungeon! Type 'exit' to quit or 'reset' to start a new game.\n")

    dungeon_intro = {
        'role': 'system',
        'content': (
            "You are a dungeon master guiding the player through a dark dungeon. "
            "Always give 2 or 3 clear numbered options for the player to choose from. "
            "Keep your responses short, punchy, and conversational. "
            "Describe scenes briefly with vivid but minimal detail."
        )
    }

    conversation_history = [dungeon_intro]

    initial_prompt = (
        "You're standing at the entrance of a dark dungeon. "
        "Say something short and natural, then give 3 simple numbered options for the player."
    )

    conversation_history.append({'role': 'user', 'content': initial_prompt})

    # Add player status as a system message in history
    player_status = {'role': 'system', 'content': f"Player status: {player.get_status()}"}
    conversation_history.append(player_status)

    ai_intro_response = generate_response(conversation_history)
    conversation_history.append({'role': 'assistant', 'content': ai_intro_response})

    print(f"AI Dungeon: {strip_markdown_bold(ai_intro_response)}\n")
    print(f"Your status: {player.get_status()}\n")

    while True:
        user_input = input("> You (choose option number): ").strip().lower()

        if user_input in ['exit', 'quit', 'leave']:
            print("You decide to leave the dungeon. Game over. Goodbye!")
            break

        if user_input in ['reset', 'new game']:
            player = Player()  # Reset player state
            conversation_history = [dungeon_intro]
            conversation_history.append({'role': 'user', 'content': initial_prompt})
            player_status = {'role': 'system', 'content': f"Player status: {player.get_status()}"}
            conversation_history.append(player_status)
            ai_intro_response = generate_response(conversation_history)
            conversation_history.append({'role': 'assistant', 'content': ai_intro_response})
            print("Game has been reset. You're back at the dungeon entrance.\n")
            print(f"AI Dungeon: {strip_markdown_bold(ai_intro_response)}\n")
            print(f"Your status: {player.get_status()}\n")
            continue

        if user_input.isdigit():
            choice_number = int(user_input)
            last_ai_msg = conversation_history[-1]['content']
            options = extract_options(last_ai_msg)

            if choice_number not in options:
                print(f"Invalid choice! Please select a number from the options: {sorted(options.keys())}")
                continue

            player_choice_text = options[choice_number]

            # Update player state based on choice text (example logic)
            # You can expand this with your own rules or AI-assisted parsing
            if "pick up key" in player_choice_text.lower():
                if not player.has_item("rusty key"):
                    player.add_item("rusty key")
                    print("You picked up a rusty key!\n")

            conversation_history.append({'role': 'user', 'content': player_choice_text})

            # Add player status before calling AI to provide context
            player_status = {'role': 'system', 'content': f"Player status: {player.get_status()}"}
            trimmed_history = [dungeon_intro, player_status] + conversation_history[-MAX_HISTORY:]

            ai_response = generate_response(trimmed_history)
            conversation_history.append({'role': 'assistant', 'content': ai_response})

            print(f"AI Dungeon: {strip_markdown_bold(ai_response)}\n")
            print(f"Your status: {player.get_status()}\n")

        else:
            print("Please enter a valid option number or 'exit', 'reset'.")

if __name__ == "__main__":
    main()
