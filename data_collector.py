import subprocess
import re
import sys
from collections import defaultdict

def analyze_library_time(path_to_bm):
    """
    Analyze the percentage of time spent in each library by recording
    call stacks with perf, then parsing the results from 'perf script'.

    This function runs the benchmark Python script (located at path_to_bm)
    under 'perf record' with call graph sampling (-g). It then runs 'perf script'
    to produce human-readable stack traces, and aggregates the samples that
    reference shared libraries (typically files ending with .so). The result is a 
    dictionary mapping library names to the percentage of samples attributed to each.
    
    Args:
      path_to_bm (str): Path to the Python benchmark script.
      
    Returns:
      dict: A dictionary where keys are library names (e.g., "libc.so.6") and 
            values are the percentage of samples (approximate time) spent in that library.
    
    Example output:
      {
          "libc.so.6": 32.1,
          "libpython3.10.so": 28.5,
          "[unknown]": 5.6,
          ...
      }
    """
    # 1. Record the execution with call graph (-g)
    record_cmd = ["perf", "record","--call-graph=dwarf", "-g", "--", "python3", path_to_bm]
    subprocess.run(record_cmd, check=True)
    
    # 2. Use perf script to convert the binary recording into text
    script_cmd = ["perf", "script"]
    script_output = subprocess.check_output(script_cmd, text=True)
    
    # 3. Parse the output to count samples per library.
    # We assume that library names contain ".so". We also capture "[unknown]" for unresolved symbols.
    lib_sample_count = defaultdict(int)
    total_samples = 0

    for line in script_output.splitlines():
        line = line.strip()
        # Skip empty lines or comment lines
        if not line or line.startswith("#"):
            continue
        
        # Look for shared library symbols (e.g., libc.so.6+0x12345)
        match = re.search(r'([^\s]+\.so[^\s]*)', line)
        if match:
            lib = match.group(1)
            # Remove offset (everything after a '+') for a cleaner library name
            lib = lib.split('+')[0]
            lib_sample_count[lib] += 1
            total_samples += 1
        elif "[unknown]" in line:
            lib_sample_count["[unknown]"] += 1
            total_samples += 1

    # 4. Calculate percentages if there were any samples.
    lib_time_percent = {}
    if total_samples > 0:
        for lib, count in lib_sample_count.items():
            lib_time_percent[lib] = (count / total_samples) * 100.0

    return lib_time_percent

def get_perf_stats(path_to_bm):
    """
    Run 'perf stat' on a Python script located at path_to_bm and collect
    performance counters for multiple event groups.
    
    Event groups and their counters:
    
      - CPU events:           cycles, instructions, branches, branch-misses
      - Cache events:         cache-references, cache-misses,
                              L1-dcache-loads, L1-dcache-load-misses,
                              LLC-loads, LLC-load-misses
      - Memory events:        dTLB-loads, dTLB-load-misses, page-faults
      - Scheduler events:     task-clock, context-switches, cpu-migrations
      - ITLB events:          iTLB-loads, iTLB-load-misses
      - Libraries breakdown:  (placeholder for future events; add as needed)
    
    Returns:
      A dictionary where each key is an event group and each value is a dictionary
      mapping event names to their collected counter value.
    """
    # Define event groups and their respective events.
    event_groups = {
        "CPU": ["cycles", "instructions", "branches", "branch-misses"],
        "Cache": ["cache-references", "cache-misses",
                  "L1-dcache-loads", "L1-dcache-load-misses",
                  "LLC-loads", "LLC-load-misses"],
        "Memory": ["dTLB-loads", "dTLB-load-misses", "page-faults"],
        "Scheduler": ["task-clock", "context-switches", "cpu-migrations"],
        "ITLB": ["iTLB-loads", "iTLB-load-misses"],
        "Libraries": []  # Placeholder: add library-specific events as needed
    }
    
    # Flatten all events into a single list for the perf stat command.
    all_events = []
    for events in event_groups.values():
        all_events.extend(events)
    
    if not all_events:
        raise ValueError("No events specified to monitor.")
    
    # Build the comma-separated event string.
    perf_events = ",".join(all_events)
    
    # Build the perf command.
    command = [
        "sudo", "perf", "stat",
        "-e", perf_events,
        "python3", path_to_bm
    ]
    
    # Run the command, capturing stdout and stderr.
    # (Note: perf typically writes its output to stderr.)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    # Initialize the results dictionary with None for each event.
    results = {group: {event: None for event in events} for group, events in event_groups.items()}
    
    # Regex pattern to match a number (with commas or decimals) followed by the event name.
    pattern = r'([\d,\.]+)\s+({})'
    
    # For each event, search through stderr to extract the numeric counter.
    for group, events in event_groups.items():
        for event in events:
            regex = re.compile(pattern.format(re.escape(event)))
            for line in stderr.splitlines():
                line = line.strip()
                if event in line:
                    match = regex.search(line)
                    if match:
                        value_str = match.group(1).replace(',', '')
                        try:
                            value = int(value_str)
                        except ValueError:
                            try:
                                value = float(value_str)
                            except ValueError:
                                value = None
                        results[group][event] = value
                        break  # Found the event; no need to check further lines.
    
    return results

# Example usage:
if __name__ == "__main__":
    if(len(sys.argv) == 1):
        str = "bm_nbody"
    else:
        str = sys.argv[1]
    benchmark_script = "pyperformance/benchmarks/" + str + "/run_benchmark.py"
    perf_results = get_perf_stats(benchmark_script)
    for group, metrics in perf_results.items():
        print(f"{group} events:")
        for event, value in metrics.items():
            print(f"  {event}: {value}")

    percentages = analyze_library_time(benchmark_script)
    for lib, percent in percentages.items():
        print(f"{lib}: {percent:.2f}%")
    