import os
import json
from dotenv import load_dotenv
import openai
from . import *
from capabilities import DOC_BEGIN_MARKER, DOC_END_MARKER

"""
Define personas (which only override the system content)
"""
PERSONAS = {
    "coder": "You are an expert coder, proficient in Python, JavaScript, and many other languages.",
    "assistant": "You are a friendly assistant",
    "default": "You are a friendly assistant",
    "exe_Coder": """You are an expert coding assistant. When given an instruction, first provide a clear, detailed,
    step-by-step plan outlining your approach, including any assumptions or clarifying questions you may have. 
    Then, implement your solution iteratively across multiple prompts. When outputting Python code, wrap it between the markers ((ex3c)) 
    and ((exend)). The code enclosed within these markers will be executed after your response, and the output will be provided as the 
    next prompt's input. Ensure your responses are well-structured, include concise comments, and follow best coding practices. 
    Feel free to ask for the user's help or clarification during development if necessary.""",
    "documenter": f"""
                You are a code documentation assistant. Your task is to document the code in the most concise and readable way possible. The result is intended to be read by Ai-agents so always be consistent with and concise with your output.
                Always document:
                - Classes with a class-level docstring explaining their purpose.
                - Functions with docstrings detailing their functionality, arguments, return types, and any exceptions they raise.
                - Only Dictionaries and Arrays, that are important with a short description of its content. 
                When documenting:
                - Always use triple double quotes to wrap docstrings, even when documenting Arrays or Dictionaries.
                - For Arrays or Dictionaries place the docstring directly above it.
                - Ensure docstrings are clear, concise, and follow best practices. Be specific about input and output types for functions and methods.
                - Be clear about the structure and purpose of arrays and dictionaries.
                
                The output should contain only the code, wrapped in between {DOC_BEGIN_MARKER} and {DOC_END_MARKER} with documentation for each class, function, array, and dictionary.
            """,
            "documenterRAG": f"""
                You are a code documentation assistant. Your task is to transform the given source code by inserting clear, concise, and consistent documentation comments for all significant code components. The output must contain only the documented code (with no extra commentary) and must follow these guidelines:

                1. **Classes:**
                - Immediately after the class declaration, insert a class-level docstring enclosed in triple double quotes.
                - The docstring must clearly explain the classs purpose and key responsibilities.
                - Append within the same docstring an array named searchterms_$_ containing 3-5 distinctive keywords that succinctly describe the classs functionality and key parameters.

                2. **Functions/Methods:**
                - Immediately after the function or method definition, add a docstring (using triple double quotes) that includes:
                    - A brief summary of the function/methods purpose.
                    - A description of each parameter (including types), return values, and any raised exceptions.
                - Append within the same docstring an array named searchterms_$_ containing 3-5 distinctive keywords that capture the function/methods behavior.

                3. **Dictionaries and Arrays:**
                - For any important dictionary or array, insert a docstring directly above its definition, enclosed in triple double quotes.
                - The docstring should provide a brief description of the structures purpose and content.
                - Append within the same docstring an array named searchterms_$_ with 3-5 unique keywords that describe the nature and role of the data structure.

                **Additional Requirements:**
                - Use triple double quotes exclusively for all docstrings.
                - Do not include any commentary or explanations outside of the documented code.
                - The final output must consist solely of the transformed code, wrapped between these markers:
                {DOC_BEGIN_MARKER}
                <documented code>
                {DOC_END_MARKER}

                Follow these instructions strictly and output only the documented code. Do not add any extra text.
                """


}

""" 
Define parameter sets for ai models
"""
PRESETS = {
    """
    A dictionary containing parameter sets for AI models, including system content, temperature, and max tokens.

    Each key represents a different persona or preset configuration.
    """
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
    },
    "documenter" : {
        "system_content": PERSONAS["documenter"],
        "temperature": 0.4,
        "max_tokens": 5000
    },
    "documenterRAG" : {
        "system_content": PERSONAS["documenterRAG"],
        "temperature": 0.4,
        "max_tokens": 5000
    }
}


# Load environment variables from .env file
load_dotenv()

class Agent:
    """
    Class representing a chat agent that interacts with OpenAI's GPT model.
    
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
    
    @staticmethod
    def delete_chat(chat_name):
        """
        Deletes a saved chat from the Agent.

        Args:
            chat_name (str): The name of the chat session to delete.

        searchterms_$_ = ["delete chat", "Agent", "session", "file", "remove"]
        """
        self.agent.delete_chat(chat_name)