import signal
import sys
import os
import io

from capabilities.constants import CAPABILITIES
from . import * 
import contextlib
from capabilities.CapRetrieval import search_code
from capabilities.Agent import CreateAgent

def create_exit_signal_handler(current_chat):
    """
    Creates a signal handler function that saves the current chat and exits the program gracefully.

    Parameters:
    current_chat: The current chat session object.

    Returns:
    function: A signal handler function.
    """
    def handle_exit_signal(signum, frame):
        try:
            if current_chat:
                print("\nSaving chat before exiting...")
                current_chat.save_chat()
        except Exception as e:
            print(f"Error saving chat: {e}")
        print("Goodbye!")
        sys.exit(0)
    
    return handle_exit_signal

def select_chat(query_chat=False):
    """
    Prompts the user to select a chat option: create a new chat, load an existing chat, delete a chat, or exit.

    Parameters:
    query_chat (bool): Flag to indicate if this is a query chat.

    Returns:
    current_chat: The selected or created chat session.
    """
    chat_sessions = {}

    while True:
        try:
            print("\n1. New Chat\n2. Load Existing Chat\n3. Delete Chat\n4. Exit")
            choice = input("Select an option: ").strip()

            if choice == "1":
                chat_name = input("Enter a name for the new chat: ").strip()
                chat_sessions[chat_name] = CreateAgent(chat_name=chat_name)
                return chat_sessions[chat_name]

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
                    return chat_sessions[chat_choice]
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
            print("Exiting...")
            sys.exit(0)

def chat_loop(current_chat, process_response=None):
    """
    Handles a user chat loop, processing user input and assistant responses.
    The function supports either a single processing function or a list of functions.

    Parameters:
    current_chat: The current chat session object.
    process_response (function or list of functions): A function or a list of functions that process the assistant's response.

    Returns:
    None
    """
    signal.signal(signal.SIGINT, create_exit_signal_handler(current_chat))  # Register signal handler
    signal.signal(signal.SIGTERM, create_exit_signal_handler(current_chat))  # Register signal handler

    while True:
        try:
            user_input = input(f"{current_chat.agent.chat_name} - User: ")
            if user_input.lower() in ["exit", "quit"]:
                current_chat.save_chat()
                print("Exiting chat session.")
                break

            assistant_reply = current_chat.send_message(user_input)
            print("Assistant:", assistant_reply)

            if process_response:
                if isinstance(process_response, list):
                    for func in process_response:
                        func(current_chat, assistant_reply)
                else:
                    process_response(current_chat, assistant_reply)

        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)

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

def process_query_response(current_chat, query_agent, assistant_reply, debug=False):
    """
    Processes the assistant's response in a query session, executing searches and forwarding results.

    Parameters:
    current_chat: The current chat session object.
    query_agent: The agent handling queries.
    assistant_reply (str): The assistant's response.
    debug (bool): If True, display the query agent's reply.

    Returns:
    None or CAPABILITIES dictionary if <capabilities_summary> is detected.
    """
    # Return CAPABILITIES directly if <capabilities_summary> is detected
    while "((q3rys))" in assistant_reply and "((q3ryend))" in assistant_reply:
            query_block = assistant_reply.split("((q3rys))")[1].split("((q3ryend))")[0].strip()
            queries = query_block.split("(-div-)")

            results = []
            for query in queries:
                if "<capabilities_summary>" in query:
                    results.append(CAPABILITIES)
                search_results = search_code(query.strip(), top_k=3)
                results.append(search_results)

            formatted_results = "\n".join(str(result) for result in results)
            queryAgent_reply = query_agent.send_message(f"Search results: {formatted_results}")

            # Print the queryAgent_reply if debug is enabled
            if debug:
                print("Query Agent Reply:", queryAgent_reply)

            print("Passing query result as next prompt...")
            assistant_reply = current_chat.send_message(f"Query result: {queryAgent_reply}")
            print("Assistant:", assistant_reply)

def simple_chat(preset_agent=None):
    """
    Starts a simple chat session, either with a preset agent or by selecting a new/existing chat.

    Parameters:
    preset_agent: An optional agent to start the chat session with.

    Returns:
    None
    """
    current_chat = preset_agent if preset_agent else select_chat()
    chat_loop(current_chat)

def exe_chat(preset_agent=None):
    """
    Starts a coding chat session, either with a preset agent or by selecting a new/existing chat.

    Parameters:
    preset_agent: An optional agent to start the chat session with.

    Returns:
    None
    """
    current_chat = preset_agent if preset_agent else select_chat()
    chat_loop(current_chat, process_coding_response)

def query_chat(preset_agent=None):
    """
    Starts a query chat session, either with a preset agent or by selecting a new/existing chat.

    Parameters:
    preset_agent: An optional agent to start the chat session with.

    Returns:
    None
    """
    current_chat = preset_agent if preset_agent else select_chat(query_chat=True)
    query_agent = CreateAgent(preset="capQuery")
    chat_loop(current_chat, lambda chat, reply: process_query_response(chat, query_agent, reply))

def code_and_query_chat(preset_agent=None):
    """
    Starts a chat session, either with a preset agent or by selecting a new/existing chat.
    The Agent is capable of querying capabilites and the project as well as executing code

    Parameters:
    preset_agent: An optional agent to start the chat session with.

    Returns:
    None
    """
    current_chat = preset_agent if preset_agent else select_chat(query_chat=True)
    query_agent = CreateAgent(preset="capQuery")
    chat_loop(current_chat, [process_coding_response, lambda chat, reply: process_query_response(chat, query_agent, reply)])
