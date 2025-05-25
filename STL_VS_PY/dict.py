import time

N = 1_000_000
d = {}

# Insert
start = time.perf_counter()
for i in range(N):
    d[i] = i
print("Python dict insert time:", time.perf_counter() - start)

# Lookup
start = time.perf_counter()
for i in range(N):
    _ = d[i]
print("Python dict lookup time:", time.perf_counter() - start)
