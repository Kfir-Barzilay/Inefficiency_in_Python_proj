

import subprocess
import re

def get_CPU_perf(path_to_bm):
    """
    Run 'perf stat' on a Python script located at path_to_bm
    and parse the counters for cycles, instructions, branches,
    and branch-misses.
    Returns a dictionary with the parsed counters.
    """
    # Adjust perf events as needed:
    perf_events = "cycles,instructions,branches,branch-misses"
    
    # Build the perf command:
    command = [
        "perf", "stat",
        "-e", perf_events,
        "python3", path_to_bm
    ]
    
    # Run the command, capturing stdout and stderr.
    # perf usually prints stats to stderr.
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    # Prepare a dictionary for storing the parsed results
    results = {
        "cycles": None,
        "instructions": None,
        "branches": None,
        "branch-misses": None
    }
    
    # We'll look for lines in stderr that match each performance counter
    # Example lines from perf stat might look like:
    #  3,726,183,112      cycles                    # ...
    #  1,846,033,112      instructions              # ...
    #  ...
    # We'll use a regex to extract the numeric values.
    for line in stderr.splitlines():
        # Remove any extra whitespace at the ends
        print(line)
        line = line.strip()
        
        # For each counter in our dictionary, check if it's in the line:
        for counter in results.keys():
            if counter in line:
                # A regex to capture a number (with commas) in the line:
                match = re.search(r'(\d[\d,\.]*)\s+' + counter, line)
                if match:
                    # Remove commas, convert to integer (or float, if you prefer)
                    value_str = match.group(1).replace(',', '')
                    try:
                        value = int(value_str)
                    except ValueError:
                        # Fallback if it’s not an integer
                        value = float(value_str)
                    
                    results[counter] = value
    
    return results

# Example usage:
if __name__ == "__main__":
    path_to_script = "/pyperformance/benchmarks/bm_nbody/run_benchmark.py"
    perf_data = get_CPU_perf(path_to_script)
    print("Perf Data:", perf_data)