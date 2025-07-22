#!/usr/bin/env python3
import sys
import dis
import types

def analyze_script_loads(script_path):
    """
    Traces the execution of a Python script and counts the occurrences
    of different 'LOAD_*' bytecode instructions.

    Args:
        script_path (str): The path to the Python script to analyze.

    Returns:
        dict: A dictionary where keys are 'LOAD_*' opcode names and
              values are their execution counts.
    """
    # Dictionary to store the counts of each LOAD instruction
    load_counts = {}

    # The tracer function that gets called for each event during execution
    def tracer(frame, event, arg):
        # We are interested in the 'opcode' event, which fires for each instruction
        if event == 'opcode':
            # Get the code object and the offset of the current instruction
            code_obj = frame.f_code
            offset = frame.f_lasti

            # Get the instruction details from the code object and offset
            instruction = dis.Instruction.from_bytes(code_obj.co_code, offset)
            
            # Check if the instruction is a LOAD operation
            if instruction.opname.startswith('LOAD_'):
                # Increment the counter for this specific LOAD opcode
                load_counts[instruction.opname] = load_counts.get(instruction.opname, 0) + 1
        
        # To trace into function calls, we must return the tracer itself
        # and enable opcode tracing on the new frame.
        if event == 'call':
            frame.f_trace_opcodes = True
            return tracer
            
        return tracer

    try:
        # Read the source code of the target script
        with open(script_path, 'r') as f:
            source_code = f.read()
        
        # Compile the source code into a code object
        # This is necessary for exec() and for our analysis
        compiled_code = compile(source_code, script_path, 'exec')

        # Set the tracer function to start monitoring execution
        sys.settrace(tracer)

        # Create a dictionary to serve as the global namespace for the script
        # This ensures the script runs in its own isolated environment
        script_globals = {
            "__name__": "__main__",
        }

        # Execute the compiled code. The tracer will be called for each opcode.
        exec(compiled_code, script_globals)

    finally:
        # It's crucial to turn off the tracer when we're done
        sys.settrace(None)

    return load_counts

def main():
    """
    Main function to run the bytecode analyzer from the command line.
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_script.py>")
        print("\nExample: python3 bytecode_load_analyzer.py sample_script.py")
        sys.exit(1)

    target_script = sys.argv[1]

    print(f"[*] Analyzing '{target_script}' for LOAD operations...")
    
    try:
        load_statistics = analyze_script_loads(target_script)

        print("\n--- Dynamic LOAD Operation Counts ---")
        if not load_statistics:
            print("No LOAD operations were detected.")
        else:
            # Sort the results for consistent output
            sorted_loads = sorted(load_statistics.items(), key=lambda item: item[1], reverse=True)
            for opname, count in sorted_loads:
                print(f"{opname:<20} | {count} times")
        print("------------------------------------")

    except FileNotFoundError:
        print(f"[!] Error: The file '{target_script}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
