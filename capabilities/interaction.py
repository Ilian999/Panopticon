import os

def save_script(filename, content):
    """
    Saves the content to the specified file in the 'capabilities' subfolder.
    :param filename: The name of the script (without .py extension)
    :param content: The content of the script that needs to be saved (as multiline string)
    """
    # Ensure the 'capabilities' directory exists
    if not os.path.exists('capabilities'):
        os.makedirs('capabilities')

    # Define the full path for the new file
    file_path = os.path.join('capabilities', filename)

    try:
        # Write content to the file
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"File '{filename}' saved successfully in 'capabilities' folder.")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

def append_code(filename, content):
    """
    Appends the content to the specified file in the 'capabilities' subfolder.

    :param filename: The name of the file (with .py extension) to append to.
    :param content: The content to append to the file.
    """
    # Define the full path for the file
    file_path = os.path.join('capabilities', filename)

    try:
        # Append content to the file
        with open(file_path, 'a') as file:
            file.write(content)
        return f"Content appended successfully to '{filename}'."
    except FileNotFoundError:
        return f"File '{filename}' does not exist in the 'capabilities' folder."
    except Exception as e:
        return f"An error occurred while appending to the file: {e}"

def create_file_with_format(filename, file_format):
    """
    Creates or saves a new file with the specified format in the 'capabilities' subfolder.

    :param filename: The name of the file (without extension) to create.
    :param file_format: The format of the file (e.g., .txt, .py).
    """
    # Define the full path for the new file
    full_filename = f"{filename}{file_format}"
    file_path = os.path.join('capabilities', full_filename)

    try:
        # Create the new file and write a default message
        with open(file_path, 'w') as file:
            file.write(f"# This is a {file_format} file created by the AI framework.\n")
        return f"File '{full_filename}' created successfully in 'capabilities' folder."
    except Exception as e:
        return f"An error occurred while creating the file: {e}"

def call_function(script_name, function_name):
    """
    Dynamically imports the specified script and call the specified function.
    
    :param script_name: The name of the script to import (without .py extension)
    :param function_name: The name of the function to call
    """
    try:
        # Import the specified script dynamically
        module = __import__(script_name)
        
        # Get the specified function from the module
        func = getattr(module, function_name)
        
        # Call the specified function
        func()
    except ImportError:
        print(f"Error: The script '{{script_name}}.py' could not be found.")
    except AttributeError:
        print(f"Error: The function '{{function_name}}' does not exist in '{{script_name}}.py'.")
    except Exception as e:
        print(f"An error occurred while calling the function: {{e}}")
