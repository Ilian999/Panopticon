import os
import json
import openai
import tiktoken
import numpy as np
from typing import List, Dict

EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_FILE = "capabilities/utilities/code_embeddings.json"
import ast
import re
import os
import json

LOG_FILE = "ragcreationerror.log"
def log_embedding_input(code: str, log_file="embedding_inputs.log"):
    """
    Appends the code snippet to a log file for debugging purposes.
    """
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(code + "\n\n")

def log_error(self, message):
        """Append error messages to the log file."""
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")
def parse_file(filepath):
    """
    Parse a file using the ast module (for functions and classes)
    and regex (for dictionaries).

    Returns a dict with keys: "functions", "classes", "dictionaries".

    Parameters:
        filepath (str): The path to the Python file to be parsed.

    Returns:
        dict: A dictionary containing parsed components of the file.

    searchterms_2 = ["parse", "file", "AST", "regex", "components"]
    """
    parsed = {
        "functions": [],      # List of dicts: { "head": ..., "doc": ... }
        "classes": [],        # List of dicts: { "head": ..., "doc": ..., "methods": [ { "head":..., "doc":... } ] }
        "dictionaries": []    # List of dicts: { "name":..., "head":..., "doc":..., "body": ... }
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        # Use ast to parse functions and classes
        try:
            tree = ast.parse(source)
        except Exception as e:
            log_error(f"AST parse error in {filepath}: {e}")
            tree = None

        # Get source lines for retrieving the signature line
        lines = source.splitlines()
        if tree:
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    # Top-level function
                    head = lines[node.lineno - 1].strip() if node.lineno - 1 < len(lines) else f"def {node.name}(...)"
                    doc = ast.get_docstring(node)
                    parsed["functions"].append({"head": head, "doc": doc or ""})
                    # Log the function code for embeddings LOGGING
                    # log_embedding_input(head + " " + (doc or ""))

                elif isinstance(node, ast.ClassDef):
                    # Class definition
                    class_head = lines[node.lineno - 1].strip() if node.lineno - 1 < len(lines) else f"class {node.name}(...)"
                    class_doc = ast.get_docstring(node)
                    class_entry = {"head": class_head, "doc": class_doc or "", "methods": []}
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Only include methods directly under the class (skip nested functions)
                            method_head = lines[item.lineno - 1].strip() if item.lineno - 1 < len(lines) else f"def {item.name}(...)"
                            method_doc = ast.get_docstring(item)
                            class_entry["methods"].append({"head": method_head, "doc": method_doc or ""})
                            # Log the method code for embeddings LOGGING
                            # log_embedding_input(method_head + " " + (method_doc or ""))
                    parsed["classes"].append(class_entry)

        # Use regex for dictionaries.
        # Only match dictionary variable names that are all caps.
        # Also capture the entire dictionary body.
        dict_pattern = re.compile(
            r'''
            (?:(?P<doc>""".*?""")\s*\n)?  # Optional docstring
            (?P<var>[A-Z_]+)\s*=\s*       # Variable name
            (?P<body>\{(?:[^{}]*|\{[^{}]*\})*\})  # Dictionary body, allowing nested dictionaries
            ''',
            re.DOTALL | re.MULTILINE | re.VERBOSE
        )
        for match in dict_pattern.finditer(source):
            var_name = match.group("var")
            doc = match.group("doc")
            head_line = match.group(0).splitlines()[0].strip()
            body = match.group("body").strip()
            if not doc:
                doc = ""
            else:
                doc = doc.strip('"""').strip()
            parsed["dictionaries"].append({
                "name": var_name,
                "doc": doc,
                "body": body
            })
            # Log the dictionary code for embeddings LOGGING
            # log_embedding_input(head_line + " " + doc + " " + body)

    except Exception as e:
        log_error(f"Error processing file {filepath}: {e}")

    return parsed



def get_embedding(text: str, model="text-embedding-ada-002"):
    """
    Generates a text embedding using OpenAI's text-embedding-ada-002.
    """
    response = openai.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return response.data[0].embedding

def generate_and_store_embeddings(path="capabilities", excluded_files=None, excluded_dirs=None, excluded_extensions=None, debug=False):
    """
    Generates embeddings for all non-excluded Python files and stores them.
    
    Optionally logs code chunks for debugging if debug is set to True.
    
    Parameters:
        path (str): The directory path to search for files.
        excluded_files (list, optional): List of filenames to exclude.
        excluded_dirs (list, optional): List of directories to exclude.
        excluded_extensions (list, optional): List of file extensions to exclude.
        debug (bool, optional): If True, logs code chunks to a debug file.
    
    Returns:
        None

    searchterms_6 = ["embeddings", "debug", "logging", "parse", "code"]
    """
    if excluded_files is None:
        excluded_files = []
    if excluded_dirs is None:
        excluded_dirs = ["chats", "__pycache__", "utilities"]
    if excluded_extensions is None:
        excluded_extensions = [".txt"]

    all_embeddings = []

    # Walk through directory and process files
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]  # Exclude directories

        for file in files:
            if file not in excluded_files and not any(file.endswith(ext) for ext in excluded_extensions):
                file_path = os.path.join(root, file)
                
                # Parse the file to extract code components (functions, classes, dictionaries)
                components = parse_file(file_path)

                # Optionally log chunks for debugging before generating embeddings
                if debug:
                    with open("chunks_for_debugging.log", "a", encoding="utf-8") as debug_file:
                        for component_type in components:
                            for component in components[component_type]:
                                code = component.get("head", "") + " " + component.get("doc", "")
                                debug_file.write(code + "\n\n")

                # For each component, generate the embedding
                for component_type in components:
                    for component in components[component_type]:
                        code = component.get("head", "") + " " + component.get("doc", "")
                        
                        # Generate the embedding
                        embedding = get_embedding(code)
                        component["embedding"] = embedding
                        all_embeddings.append(component)
                        
    # Ensure the parent directory exists
    embedding_dir = os.path.dirname(EMBEDDING_FILE)
    if not os.path.exists(embedding_dir):
        os.makedirs(embedding_dir, exist_ok=True)
    with open(EMBEDDING_FILE, "w", encoding="utf-8") as f:
        json.dump(all_embeddings, f, indent=4)

    print(f"Embeddings stored in {EMBEDDING_FILE}")


def load_embeddings():
    """
    Loads stored code embeddings from the JSON file.
    
    Returns a list of dictionaries, each containing:
    - `path`: The file where the code is located.
    - `code`: The documented code.
    - `searchterms`: The extracted keywords.
    - `embedding`: The vector representation of the code.
    """
    try:
        with open(EMBEDDING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Embedding file not found: {EMBEDDING_FILE}")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON file.")
        return []

def get_query_embedding(query: str) -> np.ndarray:
    """
    Generates an embedding for the given query using OpenAI's embedding model.
    
    Returns a NumPy array representing the embedding.
    """
    response = openai.embeddings.create(input=[query], model=EMBEDDING_MODEL)
    return response.data[0].embedding

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Computes the cosine similarity between two vectors.
    
    Returns a similarity score between -1 and 1.
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def search_code(query: str, top_k: int = 3):
    """
    Searches for the most relevant code components based on the query.
    
    - Converts the query to an embedding.
    - Computes cosine similarity with stored embeddings.
    - Returns the top_k most relevant code components.
    
    Parameters:
    - query: The user's search query.
    - top_k: Number of top matches to return.
    
    Returns a list of dictionaries containing:
    - `path`: The file where the code is found.
    - `code`: The documented code.
    """
    embeddings = load_embeddings()
    if not embeddings:
        return "No embeddings found. Run the embedding generation script first."

    query_embedding = get_query_embedding(query)
    results = []

    for entry in embeddings:
        entry_embedding = np.array(entry["embedding"])
        similarity = cosine_similarity(query_embedding, entry_embedding)
        results.append((similarity, entry))

    # Sort by highest similarity and return top_k matches
    results.sort(reverse=True, key=lambda x: x[0])
    top_matches = results[:top_k]
    filtered_matches = [
        {k: v for k, v in entry.items() if k != "embedding"} 
        for _, entry in top_matches  # Unpack tuple: ignore the first element
    ]
    return filtered_matches
