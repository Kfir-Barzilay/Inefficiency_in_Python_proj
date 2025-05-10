import time
import random
import string

def generate_random_key(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Setup
NUM_INSERTS = 1000000
CPU_FREQ_GHZ = 3.0

d = {}
insert_time_ns = 0

start_test_ns = time.perf_counter_ns()

# Perform insertions with random keys
for _ in range(NUM_INSERTS):
    key = generate_random_key()
    value = random.randint(0, 1_000_000)

    start_ns = time.perf_counter_ns()
    d[key] = value
    end_ns = time.perf_counter_ns()

    insert_time_ns += end_ns - start_ns

end_test_ns = time.perf_counter_ns()

# Results
average_time_ns = insert_time_ns / NUM_INSERTS
total_time_ns = end_test_ns - start_test_ns

print(f"Total time: {total_time_ns / 1e6:.3f} ms")
print(f"Total insertion time: {insert_time_ns / 1e6:.3f} ms")
print(f"Average time per random insertion: {average_time_ns:.2f} ns")
