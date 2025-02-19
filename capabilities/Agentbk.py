import os
import json
from dotenv import load_dotenv
import openai
from . import *
# Define personas (which only override the system content)
PERSONAS = {
    "coder": "You are an expert coder, proficient in Python, JavaScript, and many other languages.",
    "assistant": "You are a friendly assistant",
    "default": "You are a friendly assistant",
    "exe_Coder":"""You are an expert coding assistant. When given an instruction, first provide a clear, detailed,
    step-by-step plan outlining your approach, including any assumptions or clarifying questions you may have. 
    Then, implement your solution iteratively across multiple prompts. When outputting Python code, wrap it between the markers ((ex3c)) 
    and ((exend)). The code enclosed within these markers will be executed after your response, and the output will be provided as the 
    next prompt's input. Ensure your responses are well-structured, include concise comments, and follow best coding practices. 
    Feel free to ask for the user's help or clarification during development if necessary."""
}
# Define preset dictionaries for parameter sets
PRESETS = {
    "coder": {
        "system_content":  PERSONAS["coder"],
        "temperature": 0.2,
        "max_tokens": 200
    },
    "assistant": {
        "system_content": PERSONAS["assistant"],
        "temperature": 0.7,
        "max_tokens": 150
    },
    "default": {
        "system_content": PERSONAS["assistant"],
        "temperature": 0.7,
        "max_tokens": 150
    },
    "exe_Coder": {
        "system_content": PERSONAS["exe_Coder"],
        "temperature": 0.45,
        "max_tokens": 5000
    }
}


# Load environment variables from .env file
load_dotenv()

class Agent:
    def __init__(self, system_content, temperature, max_tokens, model="gpt-4o-mini", api_key=None, chat_name=None):

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        openai.api_key = self.api_key
        self.model = model
        self.chat_name = chat_name
        # Store configuration values in the Agent
        self.temperature = temperature
        self.max_tokens = max_tokens
        # Initialize conversation history with the provided system content
        self.system_content = system_content or "You are a helpful assistant."
        self.messages = [{"role": "system", "content": system_content}]
        
        if chat_name:
            self.load_chat(chat_name)
    
    def save_chat(self):
        if self.chat_name:
            chat_path = os.path.join(chatstoragefolder, f"{self.chat_name}.json")
            with open(chat_path, "w") as file:
                json.dump(self.messages, file)
            print(f"Chat saved as '{chat_path}'")

    def load_chat(self, chat_name):
        try:
            chat_path = os.path.join(chatstoragefolder, f"{chat_name}.json")
            with open(chat_path, "r") as file:
                self.messages = json.load(file)
            print(f"Chat loaded from '{chat_path}'")
        except FileNotFoundError:
            print(f"No saved chat found with the name '{chat_name}'.")

        
    def send_message(self, message: str) -> str:
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
        try:
            chat_path = os.path.join(chatstoragefolder, f"{chat_name}.json")
            os.remove(chat_path)
            print(f"Chat '{chat_name}.json' deleted successfully.")
        except FileNotFoundError:
            print(f"No chat file found with the name '{chat_name}'.")

class CreateAgent:
    def __init__(self, model="gpt-4o-mini", api_key=None, chat_name=None,
                 system_content=None, temperature=None, max_tokens=None,
                 preset="default", persona=None):
        # Determine default system content based on preset
        if preset and preset in PRESETS:
            default_system_content = PRESETS[preset].get("system_content", PERSONAS["assistant"])
            temperature = temperature or PRESETS[preset].get("temperature")
            max_tokens = max_tokens or PRESETS[preset].get("max_tokens")
        else:
            default_system_content = PERSONAS["assistant"]

        # Use the provided system_content if given, otherwise use the default from preset
        if system_content is None:
            system_content = default_system_content

        # Only override system_content with persona if the system_content is still at its default value.
        if persona and system_content == default_system_content:
            if persona in PERSONAS:
                system_content = PERSONAS[persona]
            else:
                raise ValueError("Persona not found")

        if not chat_name:
            raise ValueError("No Chatname provided")
        
        # Create an Agent instance with all parameters passed through
        self.agent = Agent(
            model=model,
            api_key=api_key,
            chat_name=chat_name,
            system_content=system_content,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def send_message(self, message: str) -> str:
        # Delegate sending the message to the Agent instance
        return self.agent.send_message(message)
    
    def save_chat(self):
        self.agent.save_chat()
    
    def load_chat(self, chat_name):
        self.agent.load_chat(chat_name)
    
    @staticmethod
    def delete_chat(chat_name):
        Agent.delete_chat(chat_name)
