import time
import os
start_test_ns = time.perf_counter_ns()

# Set the number of insertions
NUM_INSERTS = 100_000

# Estimate your CPU frequency in GHz (adjust if needed)
CPU_FREQ_GHZ = 3.0  # You can check your actual CPU frequency via `lscpu` or similar

# Dictionary to be tested
d = {}

# Generate keys and values ahead of time to avoid measuring their creation
keys = [f'key{i}' for i in range(NUM_INSERTS)]
values = [i for i in range(NUM_INSERTS)]
insert_time_ns = 0

# Perform insertions
for k, v in zip(keys, values):
    start_ns = time.perf_counter_ns()
    d[k] = v
    end_ns = time.perf_counter_ns()
    insert_time_ns += end_ns - start_ns


# Results
average_time_ns = insert_time_ns / NUM_INSERTS
#average_cycles = average_time_ns * (CPU_FREQ_GHZ * 1e3)  # 1 ns = 1e-9 s → GHz = 1e9 Hz

end_test_ns = time.perf_counter_ns()
total_time_ns = end_test_ns - start_test_ns

print(f"Total time: {total_time_ns / 1e6:.3f} ms")
print(f"Total insertion time: {insert_time_ns / 1e6:.3f} ms")
print(f"Average time per insertion: {average_time_ns:.2f} ns")
#print(f"Approximate CPU cycles per insertion: {average_cycles:.0f} cycles")
