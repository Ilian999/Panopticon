import signal
import sys
import os
import io
import contextlib
from . import *
from capabilities.Agent import CreateAgent
from capabilities.interaction import *
#from capabilities.interaction import save_script, append_code, create_file_with_format, call_function

# Function to handle termination signals
def handle_exit_signal(signum, frame):
    global current_chat
    try:
        if current_chat:
            print("\nSaving chat before exiting...")
            current_chat.save_chat()
    except Exception as e:
        pass
    print("Goodbye!")
    sys.exit(0)

# Register signal handlers for Ctrl+C and terminal close
signal.signal(signal.SIGINT, handle_exit_signal)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_exit_signal)  # Process termination

# Function to select a chat (new, load, delete, or exit)
# Function to select a chat (new, load, delete, or exit)
def selectchat():
    global current_chat
    chat_sessions = {}

    while True:
        try:
            print("\n1. New Chat\n2. Load Existing Chat\n3. Delete Chat\n4. Exit")
            choice = input("Select an option: ").strip()

            if choice == "1":
                chat_name = input("Enter a name for the new chat: ").strip()
                chat_sessions[chat_name] = CreateAgent(chat_name=chat_name)
                current_chat = chat_sessions[chat_name]
                print(f"New chat created: {chat_name}")
                return current_chat

            elif choice == "2":
                existing_chats = [f.replace(".json", "") for f in os.listdir(chatstoragefolder) if f.endswith(".json")]
                
                if not existing_chats:
                    print("No existing chats to load.")
                    continue

                print("Existing chats:")
                for idx, chat in enumerate(existing_chats, start=1):
                    print(f"{idx}. {chat}")

                chat_choice = input("Enter the chat name to load: ").strip()
                if chat_choice in existing_chats:
                    chat_sessions[chat_choice] = CreateAgent(chat_name=chat_choice)
                    current_chat = chat_sessions[chat_choice]
                    return current_chat
                else:
                    print("Invalid chat name. Try again.")

            elif choice == "3":
                existing_chats = [f.replace(".json", "") for f in os.listdir(chatstoragefolder) if f.endswith(".json")]
                if not existing_chats:
                    print("No chats to delete.")
                    continue

                print("Existing chats:")
                for idx, chat in enumerate(existing_chats, start=1):
                    print(f"{idx}. {chat}")

                chat_choice = input("Enter the chat name to delete: ").strip()
                if chat_choice in existing_chats:
                    CreateAgent.delete_chat(chat_choice)
                else:
                    print("Invalid chat name. Try again.")

            elif choice == "4":
                print("Exiting...")
                sys.exit(0)

            else:
                print("Invalid option. Please try again.")

        except KeyboardInterrupt:
            handle_exit_signal(None, None)  # Handle Ctrl+C during chat selection


# Function for the chatting loop after a chat is selected/created
def simpleloop(current_chat):
    while True:
        try:
            user_input = input(f"{current_chat.agent.chat_name} - User: ")
            if user_input.lower() in ["exit", "quit"]:
                current_chat.save_chat()
                print("Exiting chat session.")
                break
            assistant_reply = current_chat.send_message(user_input)
            print("Assistant:", assistant_reply)
        except KeyboardInterrupt:
            handle_exit_signal(None, None)  # Handle Ctrl+C


def coding_loop(current_chat):
    while True:
        try:
            user_input = input(f"{current_chat.agent.chat_name} - User: ")
            if user_input.lower() in ["exit", "quit"]:
                current_chat.save_chat()
                print("Exiting chat session.")
                break

            assistant_reply = current_chat.send_message(user_input)
            print("Assistant:", assistant_reply)

            # Keep looking for code blocks and executing them until none are found
            while "((ex3c))" in assistant_reply and "((exend))" in assistant_reply:
                # Extract and execute the code block
                code_block = assistant_reply.split("((ex3c))")[1].split("((exend))")[0].strip()
                print("Detected code block. Executing code...")

                # Capture the output of the code execution
                output_capture = io.StringIO()
                try:
                    with contextlib.redirect_stdout(output_capture):
                        exec(code_block, globals())
                    code_output = output_capture.getvalue().strip()
                    print("Execution result:")
                    print(code_output)
                except Exception as e:
                    code_output = f"Error during code execution: {e}"
                    print(code_output)

                # Pass the execution result as the next prompt so the agent can iterate
                print("Passing execution result as next prompt...")
                assistant_reply = current_chat.send_message(f"Execution result: {code_output}")
                print("Assistant:", assistant_reply)

        except KeyboardInterrupt:
            handle_exit_signal(None, None)



# Main simple_chat function
def simple_chat(preset_agent=None):
    global current_chat
    if preset_agent:
        current_chat = preset_agent  # Use the passed agent
        print(f"Chat session started with preset: {current_chat.agent.persona}")
    else:
        current_chat = selectchat()  # Select chat (new or existing)
    
    simpleloop(current_chat)  # Start the chat loop


def exe_chat(preset_agent=None):
    """
    Make sure to provide or load an execoder
    """
    global current_chat
    if preset_agent:
        current_chat = preset_agent  # Use the passed agent
        print(f"Chat session started with preset: {current_chat.agent.chat_name}")
    else:
        current_chat = selectchat()  # Select chat (new or existing)
    
    coding_loop(current_chat)  # Start the chat loop

def main():
    filename = "test_file"
    file_format = ".txt"

    # Call the create_file_with_format function directly
    result = create_file_with_format(filename, file_format)
    print(result)
