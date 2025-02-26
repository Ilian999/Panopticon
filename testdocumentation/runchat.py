import signal
import sys
import os
import io
import contextlib
from . import *
from capabilities.Agent import CreateAgent
from capabilities.interaction import *

# Function to handle termination signals
def handle_exit_signal(signum, frame):
    """
    Handles termination signals (SIGINT and SIGTERM).
    
    This function attempts to save the current chat session if it exists
    before exiting the program.

    Parameters:
        signum (int): The signal number.
        frame (signal frame): The current stack frame.

    Returns:
        None

    Raises:
        Exception: If an error occurs during chat saving.
    
    searchterms_1 = ["signal", "exit", "chat", "termination", "save"]
    """
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
def selectchat():
    """
    Allows the user to select a chat session to create, load, delete, or exit.

    This function presents a menu to the user and manages the selection
    process for chat sessions.

    Returns:
        CreateAgent: The current chat session.

    Raises:
        KeyboardInterrupt: If the user interrupts the selection process.
    
    searchterms_2 = ["chat", "selection", "create", "load", "delete"]
    """
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
    """
    Manages the chat loop for user interaction after a chat session is selected.

    This function continues to prompt the user for input and responds
    with the assistant's replies until the user decides to exit.

    Parameters:
        current_chat (CreateAgent): The current chat session.

    Returns:
        None

    Raises:
        KeyboardInterrupt: If the user interrupts the chat session.
    
    searchterms_3 = ["chat", "loop", "user interaction", "assistant", "exit"]
    """
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
    """
    Manages the coding loop for user interaction that involves code execution.

    This function continues to prompt the user for input and executes code
    blocks found in the assistant's replies until the user decides to exit.

    Parameters:
        current_chat (CreateAgent): The current chat session.

    Returns:
        None

    Raises:
        KeyboardInterrupt: If the user interrupts the coding session.
    
    searchterms_4 = ["coding", "loop", "execution", "user interaction", "assistant"]
    """
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
    """
    Initiates a simple chat session with the option to use a preset agent.

    This function sets up the current chat session either by using a provided
    agent or by selecting a new or existing chat session.

    Parameters:
        preset_agent (CreateAgent, optional): An optional preset chat agent.

    Returns:
        None
    
    searchterms_5 = ["chat", "session", "preset", "initiate", "user interaction"]
    """
    global current_chat
    if preset_agent:
        current_chat = preset_agent  # Use the passed agent
        print(f"Chat session started with preset: {current_chat.agent.persona}")
    else:
        current_chat = selectchat()  # Select chat (new or existing)
    
    simpleloop(current_chat)  # Start the chat loop

def exe_chat(preset_agent=None):
    """
    Initiates a chat session focused on executing code with the option to use a preset agent.

    This function sets up the current chat session either by using a provided
    agent or by selecting a new or existing chat session.

    Parameters:
        preset_agent (CreateAgent, optional): An optional preset chat agent.

    Returns:
        None
    
    searchterms_6 = ["chat", "execution", "code", "preset", "initiate"]
    """
    global current_chat
    if preset_agent:
        current_chat = preset_agent  # Use the passed agent
        print(f"Chat session started with preset: {current_chat.agent.chat_name}")
    else:
        current_chat = selectchat()  # Select chat (new or existing)
    
    coding_loop(current_chat)  # Start the chat loop

def main():
    """
    Main entry point of the application.

    This function initializes a file creation process and demonstrates
    the use of the create_file_with_format function.

    Returns:
        None
    
    searchterms_7 = ["main", "entry point", "file", "creation", "demonstration"]
    """
    filename = "test_file"
    file_format = ".txt"

    # Call the create_file_with_format function directly
    result = create_file_with_format(filename, file_format)
    print(result)