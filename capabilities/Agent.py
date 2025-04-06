import os
import json
from dotenv import load_dotenv
import openai
from . import *
from capabilities.Personasandpresets import PRESETS, PERSONAS

# Load environment variables from .env file
load_dotenv()

class Agent:
    """
    Class representing a chat agent that interacts with OpenAI's GPT model.
    USE CREATE_AGENT TO CREATE AGENTS!!
    
    Attributes:
        api_key (str): OpenAI API key used to authenticate requests.
        model (str): The model used for generating completions (e.g., 'gpt-4o-mini').
        chat_name (str): The name used to identify and save the chat session.
        temperature (float): The temperature setting that controls the randomness of the output.
        max_tokens (int): The maximum number of tokens (words) in the model's output.
        system_content (str): The system-level instruction that sets the context for the conversation.
        messages (list): The list of messages exchanged in the chat session.

    Methods:
        save_chat(): Saves the current chat to a file.
        load_chat(chat_name): Loads a chat from a file.
        send_message(message: str): Sends a message to the GPT model and appends the reply to the conversation history.
        delete_chat(chat_name): Deletes a saved chat file.

    searchterms_$_ = ["chat agent", "OpenAI", "GPT model", "conversation", "messages"]
    """
    
    def __init__(self, system_content, temperature, max_tokens, model="gpt-4o-mini", api_key=None, chat_name=None):
        """
        Initializes an Agent instance with the provided parameters.

        Args:
            system_content (str): Instruction to set the system context for the conversation.
            temperature (float): Temperature for controlling response randomness.
            max_tokens (int): Maximum token limit for the model's response.
            model (str): The model to use for generating completions.
            api_key (str): OpenAI API key.
            chat_name (str): The name to identify the chat session.

        Raises:
            ValueError: If no valid API key is provided.

        searchterms_$_ = ["initialization", "parameters", "Agent", "OpenAI API", "chat session"]
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        openai.api_key = self.api_key
        self.model = model
        self.chat_name = chat_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_content = system_content or "You are a helpful assistant."
        self.messages = [{"role": "system", "content": system_content}]
        
        if chat_name:
            self.load_chat(chat_name)
    
    def save_chat(self):
        """
        Saves the current conversation to a file in the chat storage folder.

        The chat will be saved with the name of the chat session, and the file will be in JSON format.

        searchterms_$_ = ["save chat", "file", "JSON", "chat storage", "session"]
        """
        # Only save if there is a chat_name
        if self.chat_name:
            chat_path = os.path.join(chatstoragefolder, f"{self.chat_name}.json")
            with open(chat_path, "w") as file:
                json.dump(self.messages, file)
            print(f"Chat saved as '{chat_path}'")
        else:
            print("No chat_name provided. Chat will not be saved.")

    def load_chat(self, chat_name):
        """
        Loads a chat from a file.

        Args:
            chat_name (str): The name of the chat session to load.

        If the chat session file does not exist, it will print an error message.

        searchterms_$_ = ["load chat", "file", "error handling", "chat session", "JSON"]
        """
        try:
            chat_path = os.path.join(chatstoragefolder, f"{chat_name}.json")
            with open(chat_path, "r") as file:
                self.messages = json.load(file)
            print(f"Chat loaded from '{chat_path}'")
        except FileNotFoundError:
            print(f"No saved chat found with the name '{chat_name}'.")

    def send_message(self, message: str) -> str:
        """
        Sends a message to the GPT model and appends the reply to the conversation history.

        Args:
            message (str): The user message to send to the GPT model.

        Returns:
            str: The model's response.

        searchterms_$_ = ["send message", "GPT model", "response", "conversation history", "user message"]
        """
        self.messages.append({"role": "user", "content": message})
        response = openai.chat.completions.create(
            model=self.model,
            messages=self.messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        reply = response.choices[0].message.content.strip()
        self.messages.append({"role": "assistant", "content": reply})
        return reply
    
    @staticmethod
    def delete_chat(chat_name):
        """
        Deletes a saved chat file.

        Args:
            chat_name (str): The name of the chat session to delete.

        If the chat file does not exist, it will print an error message.

        searchterms_$_ = ["delete chat", "file", "error handling", "chat session", "remove"]
        """
        try:
            chat_path = os.path.join(chatstoragefolder, f"{chat_name}.json")
            os.remove(chat_path)
            print(f"Chat '{chat_name}.json' deleted successfully.")
        except FileNotFoundError:
            print(f"No chat file found with the name '{chat_name}'.")

class CreateAgent:
    """
    Class responsible for creating an agent with predefined parameters or custom values.
    
    Attributes:
        agent (Agent): The Agent instance that handles the interaction with the GPT model.
    
    Methods:
        send_message(message: str): Sends a message to the Agent instance.
        save_chat(): Saves the current chat of the Agent.
        load_chat(chat_name): Loads a saved chat into the Agent.
        delete_chat(chat_name): Deletes a saved chat from the Agent.

    searchterms_$_ = ["create agent", "agent instance", "parameters", "GPT model", "interaction"]
    """
    
    def __init__(self, model="gpt-4o-mini", api_key=None, chat_name=None,
                 system_content=None, temperature=None, max_tokens=None,
                 preset=None, persona=None):
        """
        Initializes a CreateAgent instance with the provided parameters.

        Args:
            model (str): The model to use for generating completions.
            api_key (str): OpenAI API key.
            chat_name (str): The name to identify the chat session.
            system_content (str): System content to initialize the conversation context.
            temperature (float): The temperature for the model's output randomness.
            max_tokens (int): Maximum number of tokens allowed in the model's output.
            preset (str): Predefined parameter set to use for the agent configuration.
            persona (str): Optional persona to override the default system content.

        Raises:
            ValueError: If no valid chat name is provided.

        searchterms_$_ = ["initialize", "CreateAgent", "parameters", "agent configuration", "preset"]
        """
        if preset and preset in PRESETS:
            default_system_content = PRESETS[preset].get("system_content", PERSONAS["assistant"])
            temperature = temperature or PRESETS[preset].get("temperature")
            max_tokens = max_tokens or PRESETS[preset].get("max_tokens")
        else:
            default_system_content = PERSONAS["assistant"]
            raise ValueError("Preset not found")

        if system_content is None:
            system_content = default_system_content

        if persona and system_content == default_system_content:
            if persona in PERSONAS:
                system_content = PERSONAS[persona]
            else:
                raise ValueError("Persona not found")
        self.persona = persona
        self.agent = Agent(
            model=model,
            api_key=api_key,
            chat_name=chat_name,
            system_content=system_content,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def send_message(self, message: str) -> str:
        """
        Sends a message to the Agent instance.

        Args:
            message (str): The message to send.

        Returns:
            str: The response from the Agent instance.

        searchterms_$_ = ["send message", "Agent", "response", "interaction", "user input"]
        """
        return self.agent.send_message(message)

    def save_chat(self):
        """
        Saves the current chat of the Agent.

        searchterms_$_ = ["save chat", "Agent", "current chat", "file", "session"]
        """
        self.agent.save_chat()

    def load_chat(self, chat_name):
        """
        Loads a saved chat into the Agent.

        Args:
            chat_name (str): The name of the chat session to load.

        searchterms_$_ = ["load chat", "Agent", "session", "file", "retrieve"]
        """
        self.agent.load_chat(chat_name)
    

def delete_chat(chat_name):
    """
    Deletes a saved chat from the Agent.

    Args:
        chat_name (str): The name of the chat session to delete.

    searchterms_$_ = ["delete chat", "Agent", "session", "file", "remove"]
    """
    # Construct the full path to the chat file
    chat_file_path = os.path.join(chatstoragefolder, f"{chat_name}.json")

    try:
        # Check if the file exists
        if os.path.exists(chat_file_path):
            # Delete the file
            os.remove(chat_file_path)
            print(f"Chat '{chat_name}' has been successfully deleted.")
        else:
            print(f"Chat '{chat_name}' does not exist in the storage folder.")
    except Exception as e:
        print(f"An error occurred while trying to delete the chat: {e}")
