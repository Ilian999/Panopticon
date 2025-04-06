

from capabilities.CapRetrieval import parse_file


def generate_and_store_structure(path="capabilities", excluded_files=None, excluded_dirs=None, excluded_extensions=None, output_file="layered_structure.json"):
    """
    Generates a layered dictionary representing the code components (functions, classes, dictionaries)
    from all non-excluded Python files and stores the result in a JSON file.

    The resulting structure is as follows:
    {
        filename: {
            "path": filepath,
            "components": {
                comp_name: {
                    "comp_head": <header string>,
                    "comment": <docstring or comment>,
                    "code": <combined header and comment>,
                    // For classes, an additional "methods" key is added:
                    "methods": {
                        method_name: {
                            "comp_head": <method header>,
                            "comment": <method docstring>,
                            "code": <combined header and docstring>
                        },
                        ...
                    }
                },
                ...
            }
        },
        ...
    }

    Parameters:
        path (str): The directory path to search for files.
        excluded_files (list, optional): List of filenames to exclude.
        excluded_dirs (list, optional): List of directories to exclude.
        excluded_extensions (list, optional): List of file extensions to exclude.
        output_file (str, optional): The path to the JSON file where the structure will be stored.

    Returns:
        dict: A dictionary containing the layered structure of components.

    searchterms_6 = ["layered", "structure", "components", "parse", "code", "JSON"]
    """
    import os, json, re, ast

    # Use default exclusions if not provided
    if excluded_files is None:
        excluded_files = []
    if excluded_dirs is None:
        excluded_dirs = ["chats", "__pycache__", "utilities"]
    if excluded_extensions is None:
        excluded_extensions = [".txt"]

    # Helper functions to extract component names from header lines
    def extract_function_name(head):
        # Expecting header like "def function_name(...):"
        try:
            return head.split()[1].split("(")[0]
        except IndexError:
            return head

    def extract_class_name(head):
        # Expecting header like "class ClassName(...):"
        try:
            return head.split()[1].split("(")[0]
        except IndexError:
            return head

    layered_structure = {}

    # Walk through directory and process files
    for root, dirs, files in os.walk(path):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            if file not in excluded_files and not any(file.endswith(ext) for ext in excluded_extensions):
                file_path = os.path.join(root, file)
                # Parse the file to extract code components
                components = parse_file(file_path)

                file_entry = {
                    "path": file_path,
                    "components": {}
                }

                # Process functions
                for func in components.get("functions", []):
                    head = func.get("head", "")
                    comment = func.get("doc", "")
                    code = head + "\n" + comment
                    func_name = extract_function_name(head)
                    file_entry["components"][func_name] = {
                        "comp_head": head,
                        "comment": comment,
                        "code": code
                    }

                # Process dictionaries
                for d in components.get("dictionaries", []):
                    # For dictionaries, we already have a "name" field.
                    head = ""  # No specific header format provided beyond the assignment line.
                    # We can reconstruct the head from the dictionary code snippet if needed.
                    comment = d.get("doc", "")
                    code = d.get("body", "")
                    dict_name = d.get("name", "UNKNOWN")
                    file_entry["components"][dict_name] = {
                        "comp_head": head,
                        "comment": comment,
                        "code": code
                    }

                # Process classes and their methods
                for cls in components.get("classes", []):
                    head = cls.get("head", "")
                    comment = cls.get("doc", "")
                    code = head + "\n" + comment
                    class_name = extract_class_name(head)
                    # Start with the class entry
                    class_entry = {
                        "comp_head": head,
                        "comment": comment,
                        "code": code,
                        "methods": {}
                    }
                    # Process each method inside the class
                    for method in cls.get("methods", []):
                        m_head = method.get("head", "")
                        m_comment = method.get("doc", "")
                        m_code = m_head + "\n" + m_comment
                        method_name = extract_function_name(m_head)
                        class_entry["methods"][method_name] = {
                            "comp_head": m_head,
                            "comment": m_comment,
                            "code": m_code
                        }
                    file_entry["components"][class_name] = class_entry

                # Add the file entry into the layered structure, using the filename as key.
                layered_structure[file] = file_entry

    # Store the layered structure to a JSON file
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(layered_structure, f, indent=4)

    print(f"Layered structure stored in {output_file}")
    return layered_structure


import os
import json

# Path to the generated layered structure JSON file
STRUCTURE_FILE = "layered_structure.json"

def load_structure():
    """
    Loads the layered structure from the JSON file.
    
    Returns:
        dict: The layered structure dictionary.
    """
    if not os.path.exists(STRUCTURE_FILE):
        raise FileNotFoundError(f"Structure file {STRUCTURE_FILE} not found.")
    with open(STRUCTURE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def func_list(filepath):
    """
    Returns a list of functions (by their function heads) present in the given file.
    
    The function searches the layered structure for an entry corresponding to the file.
    It then filters the components whose header begins with 'def ' (indicating a function).
    
    Parameters:
        filepath (str): The full path or filename of the file.
        
    Returns:
        list: A list of function header strings.
    """
    structure = load_structure()
    functions = []
    # We compare using the basename of the filepath
    target_file = os.path.basename(filepath)
    
    for fname, entry in structure.items():
        if fname == target_file or entry.get("path") == filepath:
            for comp_name, comp in entry.get("components", {}).items():
                # Top-level functions are identified by a comp_head starting with 'def'
                if comp.get("comp_head", "").strip().startswith("def "):
                    functions.append(comp["comp_head"])
                # Also include methods inside classes
                if "methods" in comp:
                    for method_name, method in comp["methods"].items():
                        if method.get("comp_head", "").strip().startswith("def "):
                            functions.append(method["comp_head"])
            break
    return functions

def get_comp_desc(function_name):
    """
    Returns a component description (header and comment) for a given component name.
    
    The function searches through the layered structure across all files. It also checks
    within class methods if needed.
    
    Parameters:
        function_name (str): The name of the component (function, class, or dictionary).
        
    Returns:
        dict or None: A dictionary with keys "comp_head" and "comment" if found, or None if not.
    """
    structure = load_structure()
    
    for entry in structure.values():
        components = entry.get("components", {})
        for comp_key, comp in components.items():
            if comp_key == function_name:
                return {"comp_head": comp.get("comp_head", ""), "comment": comp.get("comment", "")}
            # If this is a class, check its methods too.
            if "methods" in comp:
                for method_key, method in comp["methods"].items():
                    if method_key == function_name:
                        return {"comp_head": method.get("comp_head", ""), "comment": method.get("comment", "")}
    return None

def get_comp_code(function_name):
    """
    Returns the complete code of the component (including its header and comment) 
    for a given component name.
    
    The function searches through the layered structure across all files. It also checks
    within class methods if needed.
    
    Parameters:
        function_name (str): The name of the component (function, class, or dictionary).
        
    Returns:
        str or None: The complete code string if found, or None if not.
    """
    structure = load_structure()
    
    for entry in structure.values():
        components = entry.get("components", {})
        for comp_key, comp in components.items():
            if comp_key == function_name:
                return comp.get("code", "")
            # Check within class methods
            if "methods" in comp:
                for method_key, method in comp["methods"].items():
                    if method_key == function_name:
                        return method.get("code", "")
    return None
