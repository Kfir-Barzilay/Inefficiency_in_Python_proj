

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
    - syscall:sys_enter: Number of system calls executed

    Returns a dictionary with the parsed counters.
    """
    
    # Define the perf events for scheduler and system call performance
    perf_events = "task-clock,context-switches,cpu-migrations"
    
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
        "cpu-migrations": None
    }
    
    # Parse the output from stderr (perf prints statistics there)
    for line in stderr.splitlines():
        print(line)
        line = line.strip()
        
        # Fix syscalls parsing since it's named differently
        
        counter_name = None
        for counter in results.keys():
            if counter in line:
                counter_name = counter
                break

        if counter_name:
            match = re.search(r'(\d[\d,\.]*)\s+', line)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    value = int(value_str)
                except ValueError:
                    value = float(value_str)  # If needed
                results[counter_name] = value
    
    return results


def get_lib_breakdown(path_to_bm, event="cpu-clock"):
    """
    Run 'perf record' to sample performance while executing 'path_to_bm'.
    Then run 'perf report' to parse the overhead for each library (DSO).

    :param path_to_bm: Path to the Python script to benchmark.
    :param event: Perf sampling event (default: cpu-clock). 
                  Could also be 'cycles', 'instructions', etc.
    :return: A dictionary mapping { library_name: cumulative_overhead_percent }.
    """
    perf_data_file = "perf.data"
    
    # 1. Record the samples
    #    --call-graph can be helpful if you want stack traces, but you can omit it if you only want top-level distribution.
    command_record = [
        "sudo", "perf", "record",
        "-o", perf_data_file,
        "-e", event,
        # Uncomment if you want call-graph info:
        # "--call-graph", "dwarf",
        "python3", path_to_bm
    ]
    print("Recording perf data...")
    subprocess.run(command_record, check=True)
    
    # 2. Report the data in text form
    #    '-n' groups by symbol but won't collapse everything. 
    #    '-g none' avoids grouping by call-graph so that each line is a single symbol or library.
    command_report = [
        "perf", "report",
        "--stdio",
        "-n",
        "-g", "none",
        "-i", perf_data_file
    ]
    print("Generating perf report...")
    process = subprocess.Popen(command_report, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    # 3. Parse the overhead lines
    # Typical lines look like:
    #
    #   Overhead  Shared Object       Symbol
    #   14.20%    libpython3.9.so.1.0 [.] _PyEval_EvalFrameDefault
    #    2.01%    libc-2.31.so        [.] __GI___libc_malloc
    #    1.99%    python3             [.] main
    #
    # We'll capture the "Overhead" and the "Shared Object" columns.
    #
    # You can confirm the column alignment with `perf report --stdio`.
    
    lib_pattern = re.compile(
        r"^\s*([\d\.]+%)\s+([^\s]+)\s+.*$"
    )
    
    library_usage = {}
    
    for line in stdout.splitlines():
        line = line.strip()
        match = lib_pattern.match(line)
        if match:
            overhead_str = match.group(1)   # e.g. "14.20%"
            library_name = match.group(2)  # e.g. "libpython3.9.so.1.0"
            try:
                overhead = float(overhead_str.replace("%", ""))
            except ValueError:
                continue
            
            # Aggregate overhead for each library
            if library_name not in library_usage:
                library_usage[library_name] = 0.0
            library_usage[library_name] += overhead
    
    return library_usage


# Example usage:
if __name__ == "__main__":
    path_to_benchmark = "/pyperformance/benchmarks/bm_nbody/run_benchmark.py"
    print("CPU stats:", get_CPU_perf(path_to_benchmark))
    print("Cache stats:" ,get_Cache_perf(path_to_benchmark))
    print("Memory stats:", get_Memory_perf(path_to_benchmark))
    print("Scheduler stats:",get_Scheduler_perf(path_to_benchmark))

    breakdown = get_lib_breakdown(path_to_benchmark)
    print("\nPer-library overhead breakdown (by sampled cycles):")
    for lib, overhead in breakdown.items():
        print(f"{lib}: {overhead:.2f}%")