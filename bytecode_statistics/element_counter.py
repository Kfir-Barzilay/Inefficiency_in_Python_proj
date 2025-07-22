import sys
import os
import types
from collections import defaultdict

def find_all_constants(code_obj, counts, source_name):
    """
    Recursively finds all constants in a code object and its children (e.g., functions).

    Args:
        code_obj (CodeType): The code object to analyze.
        counts (defaultdict): A dictionary to store the counts of each type.
        source_name (str): The name of the source (module or function name).
    """
    # Iterate through constants in the current code object
    for const in code_obj.co_consts:
        # Get the type name and increment its count
        type_name = type(const).__name__
        counts[type_name] += 1
        # The debug print now shows where the constant was found
        print(f"DEBUG: Found constant of type '{type_name}' in '{source_name}'")

        # If the constant is another code object (e.g., a function), recurse into it
        if isinstance(const, types.CodeType):
            # The new source_name is the name of the function/code object
            find_all_constants(const, counts, const.co_name)


def element_counter(script_path):
    """
    Analyzes a Python script to count the types of all constants, including
    those inside functions and classes.
    """
    print(f"--- Starting Analysis of {script_path} ---")

    if not os.path.exists(script_path):
        print(f"Error: The file '{script_path}' does not exist.")
        return

    print(f"Found '{script_path}'. Reading the script content.")
    with open(script_path, 'r') as f:
        script_content = f.read()

    print("Compiling the script into a code object.")
    try:
        # The top-level code object is for the whole module
        code_obj = compile(script_content, script_path, 'exec')
    except SyntaxError as e:
        print(f"Error compiling {script_path}: {e}")
        return

    type_counts = defaultdict(int)

    print("\n--- Finding all constants recursively ---")
    # Start the recursive search from the top-level module
    find_all_constants(code_obj, type_counts, source_name="<module>")

    print("\n--- Running the script to see its output (for context) ---")
    try:
        # Use a dictionary to capture the script's global variables
        script_globals = {}
        exec(code_obj, script_globals)
        print("Script executed successfully.")
    except Exception as e:
        print(f"An error occurred during script execution: {e}")

    print("\n--- Final Static Type Counts (Recursive) ---")
    if not type_counts:
        print("No constants were found.")
    else:
        # Sort by type name for a consistent, readable output
        for type_name, count in sorted(type_counts.items()):
            print(f"Type: {type_name}, Count: {count}")

    print("\n--- End of Analysis ---")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python element_counter.py <script_to_analyze.py>")
    else:
        script_to_analyze = sys.argv[1]
        element_counter(script_to_analyze)
