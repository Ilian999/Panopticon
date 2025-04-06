import os

def save_script(filename, content):
    """
    Saves the content to the specified file in the 'capabilities' subfolder.
    
    :param filename: The name of the script (without .py extension) (str)
    :param content: The content of the script that needs to be saved (as multiline string) (str)
    :return: None
    :raises Exception: If an error occurs while saving the file.
    
    searchterms_01 = ["save", "script", "file", "capabilities", "content"]
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
    Appends the code to the specified file in the 'capabilities' subfolder.

    :param filename: The name of the file (with .py extension) to append to. (str)
    :param content: The content to append to the file. (str)
    :return: A success or error message (str)
    :raises FileNotFoundError: If the specified file does not exist.
    :raises Exception: If an error occurs while appending to the file.
    
    searchterms_02 = ["append", "code", "file", "capabilities", "content"]
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

    :param filename: The name of the file (without extension) to create. (str)
    :param file_format: The format of the file (e.g., .txt, .py). (str)
    :return: A success message indicating the file was created (str)
    :raises Exception: If an error occurs while creating the file.
    
    searchterms_03 = ["create", "file", "format", "capabilities", "default"]
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

def get_file_structure(directory_path='capabilities'):
    file_structure = []

    try:
        for root, dirs, files in os.walk(directory_path):
            # Exclude __pycache__ from the directories to traverse
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for name in dirs:
                file_structure.append(os.path.join(root, name))
            for name in files:
                file_structure.append(os.path.join(root, name))

    except FileNotFoundError:
        return f"Error: The directory '{directory_path}' does not exist."
    
    return file_structure

