if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    import os
    
    # Find the grandparent directory path (two levels up from the current script)
    curr_dir = os.path.dirname(os.path.abspath(__file__)).lower()
    def find_project_root(starting_dir=curr_dir, project_name = 'algo'):
        try:
            # Traverse upward through parent directories
            for parent_dir in starting_dir.split(os.sep):
                if os.path.basename(starting_dir) == project_name:
                    return starting_dir
                new_dir = os.path.dirname(starting_dir)
                if new_dir == starting_dir:  # Root directory check
                    break
                starting_dir = new_dir

            raise FileNotFoundError(f"Project root '{project_name}' not found starting from {starting_dir}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        return None
    
    root_dir = find_project_root(project_name = 'algo')
    if not root_dir:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, root_dir)