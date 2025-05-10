import subprocess
import re

NUM_RUNS = 100
average_times = []

# Regex to extract the average insertion time
pattern = re.compile(r"Average time per random insertion:\s+([\d.]+)\s+ns")

for i in range(NUM_RUNS):
    result = subprocess.run(["python", "Dict_test\\random_insert.py"], capture_output=True, text=True)

    match = pattern.search(result.stdout)
    if match:
        avg_time = float(match.group(1))
        average_times.append(avg_time)
    else:
        print(f"Run {i+1} failed to parse output:\n{result.stdout}")
        continue

# Compute final average
if average_times:
    overall_avg = sum(average_times) / len(average_times)
    print(f"\nRan {len(average_times)} successful runs")
    print(f"Overall average insertion time: {overall_avg:.2f} ns")
else:
    print("No valid results found.")
