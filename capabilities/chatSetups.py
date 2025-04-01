import signal
import sys
import os
import io
import contextlib

from capabilities.CapRetrieval import search_code
from . import *
from capabilities.Agent import CreateAgent
from capabilities.interaction import *

# Function to handle termination signals
def handle_exit_signal(signum, frame):
    """
    Handles termination signals to save the current chat and exit the program gracefully.

    Parameters:
    signum (int): The signal number.
    frame (signal frame): The current stack frame.

    Returns:
    None

    Raises:
    Exception: If an error occurs during chat saving.

    searchterms_1 = ["termination", "signal", "exit", "chat", "save"]
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
def selectchat(query_chat = False):
    """
    Prompts the user to select a chat option: create a new chat, load an existing chat, delete a chat, or exit.

    Parameters:
    None

    Returns:
    current_chat: The selected or created chat session.

    Raises:
    KeyboardInterrupt: If the user interrupts the selection process.

    searchterms_2 = ["chat", "selection", "new", "load", "delete"]
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

import io
import contextlib

def chat_loop(current_chat, process_response):
    """
    Handles a user chat loop, processing user input and assistant responses.

    Parameters:
    current_chat: The current chat session object.
    process_response (function): A function that processes the assistant's response.

    Returns:
    None
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

            process_response(current_chat, assistant_reply)

        except KeyboardInterrupt:
            handle_exit_signal(None, None)  # Handle Ctrl+C


def process_chat_response(current_chat, assistant_reply):
    """
    Processes the assistant's response in a standard chat session.

    Parameters:
    current_chat: The current chat session object.
    assistant_reply (str): The assistant's response.

    Returns:
    None
    """
    pass  # No additional processing needed for regular chat


def process_coding_response(current_chat, assistant_reply):
    """
    Processes the assistant's response in a coding session, executing detected code blocks.

    Parameters:
    current_chat: The current chat session object.
    assistant_reply (str): The assistant's response.

    Returns:
    None
    """
    while "((ex3c))" in assistant_reply and "((exend))" in assistant_reply:
        code_block = assistant_reply.split("((ex3c))")[1].split("((exend))")[0].strip()
        print("Detected code block. Executing code...")

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

        print("Passing execution result as next prompt...")
        assistant_reply = current_chat.send_message(f"Execution result: {code_output}")
        print("Assistant:", assistant_reply)


def simpleloop(current_chat):
    """
    Initiates a standard chat loop.

    Parameters:
    current_chat: The current chat session object.
    
    Returns:
    None
    """
    chat_loop(current_chat, process_chat_response)


def coding_loop(current_chat):
    """
    Initiates a coding session loop.

    Parameters:
    current_chat: The current chat session object.

    Returns:
    None
    """
    chat_loop(current_chat, process_coding_response)

# Main simple_chat function
def simple_chat(preset_agent=None):
    """
    Starts a simple chat session, either with a preset agent or by selecting a new/existing chat.

    Parameters:
    preset_agent: An optional agent to start the chat session with.

    Returns:
    None

    searchterms_5 = ["simple", "chat", "session", "preset", "select"]
    """
    global current_chat
    if preset_agent:
        current_chat = preset_agent  # Use the passed agent
        print(f"Chat session started with preset: {current_chat.persona}")
    else:
        current_chat = selectchat()  # Select chat (new or existing)
    
    simpleloop(current_chat)  # Start the chat loop

'''
def main():
    filename = "test_file"
    file_format = ".txt"

    # Call the create_file_with_format function directly
    result = create_file_with_format(filename, file_format)
    print(result)
    '''

def exe_chat(preset_agent=None):
    """
    Starts a coding chat session, either with a preset agent or by selecting a new/existing chat.

    Parameters:
    preset_agent: An optional agent to start the chat session with.

    Returns:
    None

    searchterms_6 = ["coding", "chat", "session", "preset", "select"]
    """
    global current_chat
    if preset_agent:
        current_chat = preset_agent  # Use the passed agent
        print(f"Chat session started with preset: {current_chat.agent.chat_name}")
    else:
        current_chat = selectchat()  # Select chat (new or existing)
    
    coding_loop(current_chat)  # Start the chat loop



def query_chat(preset_agent=None):
    """
    Starts a query chat session, either with a preset agent or by selecting a new/existing chat.

    Parameters:
    preset_agent: An optional agent to start the chat session with.

    Returns:
    None

    searchterms_7 = ["query", "chat", "session", "information retrieval", "preset", "select"]
    """
    global current_chat, query_agent

    if preset_agent:
        current_chat = preset_agent  # Use the passed agent
        # chat_name = current_chat.agent.chat_name
        # query_agent = CreateAgent(chat_name=f"{chat_name}_query", preset="capQuery") if chat_name else CreateAgent(preset="capQuery")
        query_agent = CreateAgent(preset="capQuery") 
        print(f"Query chat session started with preset: {current_chat.persona}")
    else:
        current_chat = selectchat(query_chat=True)  # Select chat (new or existing)

    query_loop(current_chat, query_agent)  # Start the query loop


def process_query_response(current_chat, query_agent, assistant_reply):
    """
    Processes the assistant's response in a query session, executing searches and forwarding results.

    Parameters:
    current_chat: The current chat session object.
    query_agent: The agent handling queries.
    assistant_reply (str): The assistant's response.

    Returns:
    None
    """
    while "((q3rys))" in assistant_reply and "((q3ryend))" in assistant_reply:
        # Extract queries inside the wrapper
        query_block = assistant_reply.split("((q3rys))")[1].split("((q3ryend))")[0].strip()
        queries = query_block.split("(-div-)")  # Split multiple queries

        results = []
        for query in queries:
            search_results = search_code(query.strip(), top_k=3)
            results.append(search_results)

        # Pass search results as input to the query agent
        formatted_results = "\n".join(str(result) for result in results)
        queryAgent_reply = query_agent.send_message(f"Search results: {formatted_results}")
        print("Passing query result as next prompt...")
        # print(queryAgent_reply)
        assistant_reply = current_chat.send_message(f"Query result: {queryAgent_reply}")
        print("Assistant:", assistant_reply)


def query_loop(current_chat, query_agent):
    """
    Handles the user input loop for querying information.

    Parameters:
    current_chat: The current chat session object.
    query_agent: The agent handling queries.

    Returns:
    None
    """
    while True:
        try:
            user_input = input(f"{current_chat.agent.chat_name} - User: ")
            if user_input.lower() in ["exit", "quit"]:
                current_chat.save_chat()
                print("Exiting query session.")
                break

            assistant_reply = current_chat.send_message(user_input)
            print("Assistant:", assistant_reply)

            process_query_response(current_chat, query_agent, assistant_reply)

        except KeyboardInterrupt:
            handle_exit_signal(None, None)  # Handle Ctrl+C
