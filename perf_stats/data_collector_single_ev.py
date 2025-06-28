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
    record_cmd = ["perf", "record","-F 999","--call-graph=fp", "-g", "--", "python3", path_to_bm]
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
    Run 'perf stat' for each event separately on a Python script and collect performance counters.
    """
    event_groups = {
        "CPU": ["cycles", "instructions", "branches", "branch-misses"],
        "Cache": [
            "cache-references", "cache-misses",
            "L1-dcache-loads", "L1-dcache-load-misses",
            "LLC-loads", "LLC-load-misses"
        ],
        "Memory": ["dTLB-loads", "dTLB-load-misses", "page-faults"],
        "Scheduler": ["task-clock", "context-switches", "cpu-migrations"],
        "ITLB": ["iTLB-loads", "iTLB-load-misses", "iTLB-misses"],
        "ICache": ["L1-icache-load-misses"],
        "Libraries": []
    }

    # Prepare result dict
    results = {group: {event: None for event in events}
               for group, events in event_groups.items()}

    # For each event, call perf stat separately
    for group, events in event_groups.items():
        for event in events:
            cmd = [
                "sudo", "perf", "stat",
                "-e", event,
                "python3", path_to_bm
            ]
            print(f"\n=== Running perf for '{event}' ===")
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            _, stderr = proc.communicate()

            # Parse the stderr for this single event
            regex = re.compile(r'([\d,\.]+)\s+' + re.escape(event))
            for line in stderr.splitlines():
                m = regex.search(line)
                if m:
                    value_str = m.group(1).replace(',', '')
                    try:
                        value = int(value_str)
                    except ValueError:
                        value = float(value_str)
                    results[group][event] = value
                    print(f"  {event}: {value}")
                    break
            else:
                print(f"  ⚠️ Could not find '{event}' in perf output.")

    return results


# Example usage:
if __name__ == "__main__":
    if(len(sys.argv) == 1):
        str = "bm_nbody"
    else:
        str = sys.argv[1]
    benchmark_script = "../pyperformance/benchmarks/" + str + "/run_benchmark.py"
    perf_results = get_perf_stats(benchmark_script)
    for group, metrics in perf_results.items():
        print(f"{group} events:")
        for event, value in metrics.items():
            print(f"  {event}: {value}")

    percentages = analyze_library_time(benchmark_script)
    for lib, percent in percentages.items():
        print(f"{lib}: {percent:.2f}%")
    