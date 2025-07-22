import sys
import os
import types
from collections import defaultdict

# --- Static Analysis Part ---

def find_all_constants_recursively(code_obj, counts, source_name):
    """
    Recursively finds all constants in a code object and its children.
    This provides the static analysis portion of the results.
    """
    # Iterate through constants in the current code object
    for const in code_obj.co_consts:
        type_name = type(const).__name__
        counts[type_name] += 1
        # If the constant is another code object (e.g., a function), recurse into it
        if isinstance(const, types.CodeType):
            find_all_constants_recursively(const, counts, const.co_name)

# --- Dynamic Analysis Part ---

# Global state for the tracer to store its findings
dynamic_type_counts = defaultdict(int)
seen_object_ids = set()
# Global list to hold the source code lines of the script being analyzed
g_script_lines = []

def dynamic_tracer(frame, event, arg):
    """
    A trace function to be used with sys.settrace.
    It inspects local variables on each line execution to find the types of
    objects created at runtime and prints the source line.
    """
    # We are interested in the 'line' event, which fires before a line is executed.
    if event == 'line':
        lineno = frame.f_lineno
        # Get the current line of code from the global list
        line_content = g_script_lines[lineno - 1].strip() if 0 < lineno <= len(g_script_lines) else "[source not available]"
        
        # Check all variables in the current local scope
        for var_name, var_value in frame.f_locals.items():
            obj_id = id(var_value)
            # Check if we have already counted this specific object instance.
            # This prevents counting the same object on every single line.
            if obj_id not in seen_object_ids:
                type_name = type(var_value).__name__
                dynamic_type_counts[type_name] += 1
                seen_object_ids.add(obj_id)
                # Print the line of code and the type of the new object found
                print(f"the current line is: {line_content} type {type_name} was inserted")
    # Return the tracer function to continue tracing
    return dynamic_tracer


def element_counter(script_path):
    """
    Analyzes a Python script using both static and dynamic analysis to count
    the types of all constants and runtime objects.
    """
    print(f"--- Starting Analysis of {script_path} ---")

    if not os.path.exists(script_path):
        print(f"Error: The file '{script_path}' does not exist.")
        return

    print(f"Found '{script_path}'. Reading the script content.")
    global g_script_lines
    with open(script_path, 'r') as f:
        script_content = f.read()
        # Store script lines globally for the tracer to access
        g_script_lines = script_content.splitlines()

    print("Compiling the script into a code object.")
    try:
        code_obj = compile(script_content, script_path, 'exec')
    except SyntaxError as e:
        print(f"Error compiling {script_path}: {e}")
        return

    # 1. --- Static Analysis ---
    static_type_counts = defaultdict(int)
    print("\n--- Phase 1: Static Analysis (Finding Constants) ---")
    find_all_constants_recursively(code_obj, static_type_counts, "<module>")
    print("Static analysis complete.")

    # 2. --- Dynamic Analysis ---
    print("\n--- Phase 2: Dynamic Analysis (Tracing Execution) ---")
    print("Running script with tracer to find runtime objects...")
    # Reset global state for the tracer before each run
    global dynamic_type_counts, seen_object_ids
    dynamic_type_counts = defaultdict(int)
    seen_object_ids = set()
    
    # Set the trace function
    sys.settrace(dynamic_tracer)
    try:
        # Use a dictionary to capture the script's global variables
        script_globals = {}
        exec(code_obj, script_globals)
    except Exception as e:
        print(f"An error occurred during script execution: {e}")
    finally:
        # Crucially, turn the tracer off to stop tracing our own script
        sys.settrace(None)
    print("Dynamic analysis complete.")

    # 3. --- Combine and Report Results ---
    print("\n--- Final Combined Type Counts ---")

    # Combine counts from both static and dynamic analysis
    final_counts = static_type_counts.copy()
    for type_name, count in dynamic_type_counts.items():
        # Add dynamic counts to the static ones
        final_counts[type_name] += count

    if not final_counts:
        print("No constants or runtime objects were found.")
    else:
        print("Combined results from static constants and dynamic runtime objects:")
        for type_name, count in sorted(final_counts.items()):
            print(f"Type: {type_name}, Count: {count}")

    print("\n--- End of Analysis ---")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python element_counter.py <script_to_analyze.py>")
    else:
        script_to_analyze = sys.argv[1]
        element_counter(script_to_analyze)
