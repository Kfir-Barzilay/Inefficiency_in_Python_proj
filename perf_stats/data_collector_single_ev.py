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
