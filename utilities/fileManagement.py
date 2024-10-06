"""
Codes for managing the path and directories of this project.
"""
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

def find_project_root(starting_dir=curr_dir, project_name = 'algo'):
    """
    Recursively search for the project root.
     
    Done by looking for a directory named 
    `project_name`.
    
    Args:
    - starting_dir (str): The starting directory (e.g., current file's directory).
    - project_name (str): The name of the project directory to search for.
    
    Returns:
    - str: The path to the project root.
    
    WARNING: this is intended to work on windows, as windows directories are
    case insensitive and will always return lower case.
    """

    # Traverse upward through parent directories
    for parent_dir in starting_dir.split(os.sep):
        if os.path.basename(starting_dir) == project_name:
            return starting_dir
        new_dir = os.path.dirname(starting_dir)
        if new_dir == starting_dir:  # Root directory check
            break
        starting_dir = new_dir

    raise FileNotFoundError(f"Project root '{project_name}' not found starting from {starting_dir}")