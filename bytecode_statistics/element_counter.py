import sys
import os
import types
import time
from collections import defaultdict

# --- Static Analysis Part ---

def find_all_constants_recursively(code_obj, counts, source_name):
    """
    Recursively finds all constants in a code object and its children.
    This provides the static analysis portion of the results.
    """
    for const in code_obj.co_consts:
        type_name = type(const).__name__
        counts[type_name] += 1
        if isinstance(const, types.CodeType):
            find_all_constants_recursively(const, counts, const.co_name)

# --- Dynamic "Real-Time" Analysis Part ---

# Global state for the tracer to store its findings
dynamic_type_counts = defaultdict(int)
seen_object_ids = set()
g_script_lines = []

def print_realtime_summary(current_line):
    """
    Clears the console and prints the current state of the dynamic type counts.
    This creates the "real-time" feel.
    """
    # Clear the console screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("--- Real-Time Dynamic Analysis ---")
    print("Counting objects as they are created...\n")
    
    print("--- Current Dynamic Counts ---")
    if not dynamic_type_counts:
        print("Waiting for first object...")
    else:
        for type_name, count in sorted(dynamic_type_counts.items()):
            print(f"Type: {type_name}, Count: {count}")
    
    print("\n----------------------------------")
    print(f"Last update triggered by line: {current_line}")

def dynamic_tracer(frame, event, arg):
    """
    A trace function that inspects local variables on each line execution
    and updates a real-time summary on the screen.
    """
    if event == 'line':
        lineno = frame.f_lineno
        line_content = g_script_lines[lineno - 1].strip() if 0 < lineno <= len(g_script_lines) else "[source not available]"
        
        # Check for new objects in the local scope
        for var_name, var_value in frame.f_locals.items():
            obj_id = id(var_value)
            if obj_id not in seen_object_ids:
                type_name = type(var_value).__name__
                dynamic_type_counts[type_name] += 1
                seen_object_ids.add(obj_id)
                
                # Update the real-time display
                print_realtime_summary(line_content)
                # Pause slightly so the update is visible
                time.sleep(0.1)
                
    return dynamic_tracer


def element_counter(script_path):
    """
    Analyzes a Python script using static analysis and then a "real-time"
    dynamic analysis to count object types.
    """
    print(f"--- Starting Analysis of {script_path} ---")

    if not os.path.exists(script_path):
        print(f"Error: The file '{script_path}' does not exist.")
        return

    print(f"Found '{script_path}'. Reading the script content.")
    global g_script_lines
    with open(script_path, 'r') as f:
        script_content = f.read()
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
    time.sleep(2) # Pause to allow reading the static results

    # 2. --- Dynamic Analysis ---
    # Reset global state for the tracer before each run
    global dynamic_type_counts, seen_object_ids
    dynamic_type_counts = defaultdict(int)
    seen_object_ids = set()
    
    # Set the trace function
    sys.settrace(dynamic_tracer)
    try:
        # Run initial display
        print_realtime_summary("Starting execution...")
        time.sleep(1)
        # Use a dictionary to capture the script's global variables
        script_globals = {}
        exec(code_obj, script_globals)
    except Exception as e:
        print(f"An error occurred during script execution: {e}")
    finally:
        # Crucially, turn the tracer off
        sys.settrace(None)

    # 3. --- Final Combined Report ---
    print("\n\n--- Dynamic Analysis Complete ---")
    print("\n--- Final Combined Type Counts ---")
    
    final_counts = static_type_counts.copy()
    for type_name, count in dynamic_type_counts.items():
        final_counts[type_name] += count

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
