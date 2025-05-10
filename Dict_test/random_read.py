import time
import random
import string

def generate_random_key(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Setup
NUM_ENTRIES = 1000000
CPU_FREQ_GHZ = 3.0

# Step 1: Create dictionary with random keys
d = {}
keys = []

for _ in range(NUM_ENTRIES):
    key = generate_random_key()
    keys.append(key)
    d[key] = random.randint(0, 1_000_000)

# Step 2: Perform random reads from existing keys
read_time_ns = 0
start_test_ns = time.perf_counter_ns()

for _ in range(NUM_ENTRIES):
    key = random.choice(keys)
    start_ns = time.perf_counter_ns()
    _ = d[key]
    end_ns = time.perf_counter_ns()
    read_time_ns += end_ns - start_ns

end_test_ns = time.perf_counter_ns()

# Results
average_time_ns = read_time_ns / NUM_ENTRIES
total_time_ns = end_test_ns - start_test_ns

print(f"Total test time: {total_time_ns / 1e6:.3f} ms")
print(f"Total read time: {read_time_ns / 1e6:.3f} ms")
print(f"Average time per dictionary read: {average_time_ns:.2f} ns")
