import os
from capabilities import DOC_BEGIN_MARKER, DOC_END_MARKER
import capabilities.Agent as agent
from concurrent.futures import ThreadPoolExecutor
import re

def document_file(file_path: str):
    """
    This function processes a single Python file to generate and add documentation using an agent.
    The documentation will be wrapped between BEGIN_$nti and END_$kso.

    Parameters:
    - file_path (str): The path to the Python file to be documented.

    Returns:
    None

    Raises:
    Exception: If there is an error during the documentation process.

    searchterms_$_: ["documentation", "file processing", "agent"]
    """
    try:
        # Load the agent
        agent_instance = agent.CreateAgent(preset="documenterRAG")

        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Send the file content to the agent for documentation
        message = f"Document the following code, as per your instructions.\n\n{file_content}"
        documented_content = agent_instance.send_message(message=message)
        escaped_begin = re.escape(DOC_BEGIN_MARKER)
        escaped_end = re.escape(DOC_END_MARKER)

        # Extract the actual code between the markers
        match = re.search(rf'{escaped_begin}(.*?){escaped_end}', documented_content, re.DOTALL)
        if match:
            extracted_code = match.group(1).strip()
        else:
            extracted_code = documented_content.strip()

        # Write the extracted code back into the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(extracted_code)

        print(f"File documented successfully: {file_path}")

    except Exception as e:
        print(f"Error documenting file {file_path}: {e}")

def document_files_in_directory(directory, excluded_files: list, excluded_dirs: list, excluded_extensions: list):
    """
    This function processes all files in a directory (except excluded ones) in parallel.
    Each file is documented by a separate agent.

    Parameters:
    - directory (str): The path to the directory to process.
    - excluded_files (list): List of specific files to exclude from processing.
    - excluded_dirs (list): List of subdirectories to exclude from processing.
    - excluded_extensions (list): List of file extensions to exclude from processing.

    Returns:
    None

    searchterms_$_: ["directory processing", "parallel execution", "file exclusion"]
    """
    # List to hold files to be documented
    files_to_document = []

    # Walk through the directory to find files and directories
    for root, dirs, files in os.walk(directory):
        # Skip directories that are in the excluded_dirs list
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        # Process each file in the current directory
        for file in files:
            # Exclude files based on file name or file extension
            if file not in excluded_files and not any(file.endswith(ext) for ext in excluded_extensions):
                file_path = os.path.join(root, file)
                files_to_document.append(file_path)

    # Create a ThreadPoolExecutor to process files in parallel
    with ThreadPoolExecutor() as executor:
        # Submit each file to the executor for processing
        executor.map(document_file, files_to_document)

def process_directory(path = "capabilities", excluded_files: list = None, excluded_dirs: list = None, excluded_extensions: list = None):
    """
    Main function to process a directory with exclusion lists for files and extensions.

    Parameters:
    - path (str): The path to the directory containing Python files.
    - excluded_files (list): List of specific filenames to exclude from processing.
    - excluded_dirs (list): List of subdirectories to exclude from processing.
    - excluded_extensions (list): List of file extensions to exclude from processing.

    Returns:
    None

    searchterms_$_: ["directory processing", "exclusions", "file documentation"]
    """
    if excluded_files is None:
        excluded_files = []
    if excluded_dirs is None:
        excluded_dirs = ["chats","__pycache__"]
    if excluded_extensions is None:
        excluded_extensions = [".txt"]

    document_files_in_directory(path, excluded_files, excluded_dirs, excluded_extensions)

# Example usage
if __name__ == "__main__":
    # Specify the directory where your Python files are located
    directory = 'path_to_your_directory'
    
    # Specify files, directories, and extensions to exclude
    excluded_files = ['exclude_this_file.py', 'another_file_to_exclude.py']
    excluded_dirs = ['exclude_this_directory', 'another_directory_to_exclude']
    excluded_extensions = ['.txt', '.md']  # Exclude these file types

    # Process the directory with the exclusions
    process_directory(directory, excluded_files, excluded_dirs, excluded_extensions)