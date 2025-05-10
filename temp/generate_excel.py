import sys
import re
from openpyxl import Workbook

def parse_file(filename):
    with open(filename, "r") as f:
        return f.readlines()

def extract_metrics(lines):
    metrics = []

    patterns = {
        "General": [("nbody (Mean)", r"nbody: Mean \+- std dev: (\d+) ms")],
        "CPU events": [
            ("cycles", r"cycles:\s+(\d+)"),
            ("instructions", r"instructions:\s+(\d+)"),
            ("branches", r"branches:\s+(\d+)"),
            ("branch-misses", r"branch-misses:\s+(\d+)"),
        ],
        "Cache events": [
            ("cache-references", r"cache-references:\s+(\d+)"),
            ("cache-misses", r"cache-misses:\s+(\d+)"),
            ("L1-dcache-loads", r"L1-dcache-loads:\s+(\d+)"),
            ("L1-dcache-load-misses", r"L1-dcache-load-misses:\s+(\d+)"),
            ("LLC-loads", r"LLC-loads:\s+(\d+)"),
            ("LLC-load-misses", r"LLC-load-misses:\s+(\d+)"),
        ],
        "Memory events": [
            ("dTLB-loads", r"dTLB-loads:\s+(\d+)"),
            ("dTLB-load-misses", r"dTLB-load-misses:\s+(\d+)"),
            ("page-faults", r"page-faults:\s+(\d+)"),
        ],
        "Scheduler events": [
            ("task-clock", r"task-clock:\s+(\S+)"),
            ("context-switches", r"context-switches:\s+(\d+)"),
            ("cpu-migrations", r"cpu-migrations:\s+(\d+)"),
        ],
        "ITLB events": [
            ("iTLB-loads", r"iTLB-loads:\s+(\d+)"),
            ("iTLB-load-misses", r"iTLB-load-misses:\s+(\d+)"),
        ]
    }

    for category, entries in patterns.items():
        for metric, regex in entries:
            for line in lines:
                match = re.search(regex, line)
                if match:
                    metrics.append((category, metric, match.group(1)))
                    break

    # Library statistics
    lib_section = False
    for line in lines:
        if line.strip().startswith("Libraries events:"):
            lib_section = True
            continue
        if lib_section:
            if not line.strip():
                break
            lib_match = re.match(r"\((.*?)\):\s+([\d.]+)%", line.strip())
            if lib_match:
                path, percent = lib_match.groups()
                if path == "[unknown]":
                    label = "unknown"
                else:
                    label = path.split("/")[-1]
                metrics.append(("Library usage", label, percent + "%"))

    return metrics

def write_to_excel(metrics, output_filename):
    wb = Workbook()
    ws = wb.active
    ws.title = "Metrics"
    ws.append(["Category", "Metric", "Value"])
    for category, metric, value in metrics:
        ws.append([category, metric, value])
    wb.save(output_filename)
    print(f"Excel file created: {output_filename}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_excel.py <input_file.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.rsplit('.', 1)[0] + "_metrics.xlsx"

    lines = parse_file(input_file)
    metrics = extract_metrics(lines)
    write_to_excel(metrics, output_file)

if __name__ == "__main__":
    main()
