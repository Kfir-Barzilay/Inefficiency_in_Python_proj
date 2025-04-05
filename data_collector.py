import subprocess
import re

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
    benchmark_script = "pyperformance/benchmarks/bm_nbody/run_benchmark.py"  # Replace with your benchmark script path
    perf_results = get_perf_stats(benchmark_script)
    for group, metrics in perf_results.items():
        print(f"{group} events:")
        for event, value in metrics.items():
            print(f"  {event}: {value}")