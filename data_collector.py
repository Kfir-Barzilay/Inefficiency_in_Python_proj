

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
        "sudo","perf", "stat",
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


def get_Cache_perf(path_to_bm):
    """
    Run 'perf stat' on a Python script located at path_to_bm
    and parse the counters for cache performance:
    
    - cache-references: Number of cache accesses (L1, L2, L3)
    - cache-misses: Number of cache misses
    - L1-dcache-loads: Number of L1 data cache loads
    - L1-dcache-load-misses: Number of L1 data cache load misses
    - LLC-loads: Number of last-level cache (L3) loads
    - LLC-load-misses: Number of L3 cache misses

    Returns a dictionary with the parsed counters.
    """
    
    # Define the perf events to track cache performance
    perf_events = "cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses"
    
    # Build the perf command:
    command = [
        "sudo", "perf", "stat",
        "-e", perf_events,
        "python3", path_to_bm
    ]
    
    # Run the command, capturing stdout and stderr.
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    # Prepare a dictionary for storing the parsed results
    results = {
        "cache-references": None,
        "cache-misses": None,
        "L1-dcache-loads": None,
        "L1-dcache-load-misses": None,
        "LLC-loads": None,
        "LLC-load-misses": None
    }
    
    # Parse the output from stderr (perf prints statistics there)
    for line in stderr.splitlines():
        line = line.strip()
        
        for counter in results.keys():
            if counter in line:
                # A regex to capture a number (with commas) in the line:
                match = re.search(r'(\d[\d,\.]*)\s+' + counter, line)
                if match:
                    value_str = match.group(1).replace(',', '')
                    try:
                        value = int(value_str)
                    except ValueError:
                        value = float(value_str)  # If needed
                    results[counter] = value
    
    return results


def get_Memory_perf(path_to_bm):
    """
    Run 'perf stat' on a Python script located at path_to_bm
    and parse the counters for memory performance:

    - dTLB-loads: Number of data Translation Lookaside Buffer (TLB) loads
    - dTLB-load-misses: Number of TLB load misses
    - context-switches: Number of context switches (task switching)
    - page-faults: Number of page faults

    Returns a dictionary with the parsed counters.
    """
    
    # Define the perf events for memory performance
    perf_events = "dTLB-loads,dTLB-load-misses,context-switches,page-faults"
    
    # Build the perf command:
    command = [
        "sudo", "perf", "stat",
        "-e", perf_events,
        "python3", path_to_bm
    ]
    
    # Run the command, capturing stdout and stderr.
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    # Prepare a dictionary for storing the parsed results
    results = {
        "dTLB-loads": None,
        "dTLB-load-misses": None,
        "context-switches": None,
        "page-faults": None
    }
    
    # Parse the output from stderr (perf prints statistics there)
    for line in stderr.splitlines():
        line = line.strip()
        
        for counter in results.keys():
            if counter in line:
                # A regex to capture a number (with commas) in the line:
                match = re.search(r'(\d[\d,\.]*)\s+' + counter, line)
                if match:
                    value_str = match.group(1).replace(',', '')
                    try:
                        value = int(value_str)
                    except ValueError:
                        value = float(value_str)  # If needed
                    results[counter] = value
    
    return results


def get_Scheduler_perf(path_to_bm):
    """
    Run 'perf stat' on a Python script located at path_to_bm
    and parse the counters for scheduler and system call performance:

    - task-clock: Total time the CPU spent on a task
    - context-switches: Number of times the CPU switched processes
    - cpu-migrations: Number of times a process moved between CPU cores
    - syscalls: Number of system calls executed

    Returns a dictionary with the parsed counters.
    """
    
    # Define the perf events for scheduler and system call performance
    perf_events = "task-clock,context-switches,cpu-migrations,syscalls"
    
    # Build the perf command:
    command = [
        "sudo", "perf", "stat",
        "-e", perf_events,
        "python3", path_to_bm
    ]
    
    # Run the command, capturing stdout and stderr.
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    # Prepare a dictionary for storing the parsed results
    results = {
        "task-clock": None,
        "context-switches": None,
        "cpu-migrations": None,
        "syscalls": None
    }
    
    # Parse the output from stderr (perf prints statistics there)
    for line in stderr.splitlines():
        line = line.strip()
        
        for counter in results.keys():
            if counter in line:
                # A regex to capture a number (with commas) in the line:
                match = re.search(r'(\d[\d,\.]*)\s+' + counter, line)
                if match:
                    value_str = match.group(1).replace(',', '')
                    try:
                        value = int(value_str)
                    except ValueError:
                        value = float(value_str)  # If needed
                    results[counter] = value
    
    return results

# Example usage:
if __name__ == "__main__":
    path_to_script = "/pyperformance/benchmarks/bm_nbody/run_benchmark.py"
    print("CPU stats:", get_CPU_perf(path_to_script))
    print("Cache stats:" ,get_Cache_perf(path_to_script))
    print("Memory stats:", get_Memory_perf(path_to_script))
    print(" stats:",get_Scheduler_perf(path_to_script))