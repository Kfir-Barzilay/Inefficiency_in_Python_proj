import subprocess
import re
from collections import defaultdict

def get_perf_stats_with_libraries(path_to_bm):
    """
    Runs perf stat and perf record+script to collect:
      - CPU/cache/memory/scheduler events
      - Breakdown of time spent in shared libraries (.so)
    
    Returns:
      A dictionary of performance counters and per-library time estimates.
    """

    # Event groups
    event_groups = {
        "CPU": ["cycles", "instructions", "branches", "branch-misses"],
        "Cache": ["cache-references", "cache-misses",
                  "L1-dcache-loads", "L1-dcache-load-misses",
                  "LLC-loads", "LLC-load-misses"],
        "Memory": ["dTLB-loads", "dTLB-load-misses", "page-faults"],
        "Scheduler": ["task-clock", "context-switches", "cpu-migrations"],
        "ITLB": ["iTLB-loads", "iTLB-load-misses"],
        "Libraries": {}  # Will fill dynamically
    }

    all_events = [e for group in event_groups.values() if isinstance(group, list) for e in group]
    perf_event_str = ",".join(all_events)

    ## === 1. Run `perf stat` to get standard events ===
    stat_cmd = ["sudo", "perf", "stat", "-e", perf_event_str, "python3", path_to_bm]
    proc = subprocess.Popen(stat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _, stderr = proc.communicate()

    results = {group: {e: None for e in events} for group, events in event_groups.items() if isinstance(events, list)}

    # Parse perf stat output
    for line in stderr.splitlines():
        line = line.strip()
        for event in all_events:
            if event in line:
                match = re.search(r'([\d,\.]+)\s+' + re.escape(event), line)
                if match:
                    value = match.group(1).replace(',', '')
                    try:
                        value = int(value)
                    except ValueError:
                        value = float(value)
                    for group, events in event_groups.items():
                        if isinstance(events, list) and event in events:
                            results[group][event] = value
                            break

    ## === 2. Run `perf record -g` + `perf script` to collect samples ===
    subprocess.run(["sudo", "perf", "record", "-g", "--", "python3", path_to_bm], check=True)
    script_output = subprocess.check_output(["sudo", "perf", "script"], text=True)

    # Sample count per library
    lib_sample_count = defaultdict(int)

    for line in script_output.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Example line: "    python3  23456 [000] 123.456789: cycles: ..."
        #                "        7fff7d3e8a90 libc.so.6"
        match = re.search(r'\s+([^\s]+\.so[^\s]*)', line)
        if match:
            lib = match.group(1)
            lib_sample_count[lib] += 1
        elif "[unknown]" in line:
            lib_sample_count["[unknown]"] += 1

    # Normalize or sort (optional)
    total_samples = sum(lib_sample_count.values())
    lib_time_percent = {
        lib: (count / total_samples * 100.0) for lib, count in lib_sample_count.items()
    }

    results["Libraries"] = dict(sorted(lib_time_percent.items(), key=lambda x: -x[1]))

    return results

if _name_ == "_main_":
    benchmark_script = "pyperformance/benchmarks/bm_nbody/run_benchmark.py"  # Replace with your benchmark script path
    perf_results = get_perf_stats(benchmark_script)
    for group, metrics in perf_results.items():
        print(f"{group} events:")
        for event, value in metrics.items():
            print(f"  {event}: {value}")