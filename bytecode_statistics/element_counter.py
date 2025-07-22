import sys
import os
import dis
from collections import defaultdict

def element_counter(script_path):
    """
    Analyzes a Python script to count the types of elements loaded onto the stack.

    Args:
        script_path (str): The path to the Python script to analyze.
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
        code_obj = compile(script_content, script_path, 'exec')
    except SyntaxError as e:
        print(f"Error compiling {script_path}: {e}")
        return

    print("Disassembling the code to inspect bytecode.")
    instructions = list(dis.get_instructions(code_obj))

    type_counts = defaultdict(int)

    # A simplified simulation of the stack
    stack = []
    
    # Global and local scopes for exec
    global_scope = {}
    local_scope = {}


    print("\n--- Executing and Tracing ---")
    
    # We will execute the code and inspect the constants
    # A full dynamic trace is more complex, so we start by inspecting constants
    # which are loaded onto the stack.

    print("Analyzing constants loaded by 'LOAD_CONST'.")
    for const in code_obj.co_consts:
        if const is not None and not callable(const): # Exclude code objects for functions/classes
            type_name = type(const).__name__
            print(f"Found constant: {const} of type {type_name}")
            type_counts[type_name] += 1

    # To get a more dynamic count, we can override built-ins or trace,
    # but for a start, let's analyze what can be statically determined.
    # A true dynamic analysis requires a more complex setup, often with sys.settrace.
    # This script provides a static analysis of the constants, which is a good starting point.

    print("\n--- Analysis of Global and Local Variable Loads ---")
    # This part is more complex as it requires tracking assignments.
    # We can analyze instructions to see what's being loaded.
    for instruction in instructions:
        # LOAD_CONST is already handled above by iterating through co_consts
        # Let's look at other ways things get on the stack
        if instruction.opname == 'LOAD_CONST':
            # This is just for verbose logging
            print(f"Instruction: {instruction.opname}, Arg: {instruction.argval}")
        elif instruction.opname in ('LOAD_NAME', 'LOAD_GLOBAL'):
            # This is tricky because the type depends on what was assigned to the name.
            # A full dynamic trace would be needed to know the type at this point.
            print(f"Instruction: {instruction.opname}, Name: {instruction.argval} (Type depends on runtime state)")


    print("\n--- Running the script to see output ---")
    try:
        exec(code_obj, global_scope, local_scope)
        print("Script executed successfully.")
    except Exception as e:
        print(f"An error occurred during script execution: {e}")


    print("\n--- Final Type Counts (from co_consts) ---")
    if not type_counts:
        print("No constant types were counted. The script might be loading variables dynamically.")
    else:
        for type_name, count in type_counts.items():
            print(f"Type: {type_name}, Count: {count}")

    print("\n--- End of Analysis ---")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python element_counter.py <script_to_analyze.py>")
    else:
        script_to_analyze = sys.argv[1]
        element_counter(script_to_analyze)
