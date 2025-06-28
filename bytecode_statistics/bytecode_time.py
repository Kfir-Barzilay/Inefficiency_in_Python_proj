import timeit
import dis
import matplotlib.pyplot as plt

# === Functions with minimal bytecodes ===

def test_LOAD_FAST(x):
    return x

def test_BINARY_OP(x, y):
    return x + y  # Will use BINARY_OP (opcode with arg)

def test_LOAD_CONST():
    return 42

def test_STORE_FAST(x):
    y = x  # Store into local

def test_BINARY_SUBSCR(d, key):
    return d[key]

def test_STORE_SUBSCR(d, key, val):
    d[key] = val

# === Confirm the bytecodes ===

print("Verifying bytecode instructions used...\n")

print("-- LOAD_FAST --")
dis.dis(test_LOAD_FAST)
print("-- BINARY_OP --")
dis.dis(test_BINARY_OP)
print("-- LOAD_CONST --")
dis.dis(test_LOAD_CONST)
print("-- STORE_FAST --")
dis.dis(test_STORE_FAST)
print("-- BINARY_SUBSCR --")
dis.dis(test_BINARY_SUBSCR)
print("-- STORE_SUBSCR --")
dis.dis(test_STORE_SUBSCR)

# === Benchmark list ===

benchmarks = [
    ("LOAD_FAST", "test_LOAD_FAST(x)", {}),
    ("BINARY_OP", "test_BINARY_OP(x, y)", {}),
    ("LOAD_CONST", "test_LOAD_CONST()", {}),
    ("STORE_FAST", "test_STORE_FAST(x)", {}),
    ("BINARY_SUBSCR", "test_BINARY_SUBSCR(d, key)", {'d': {'a': 1}, 'key': 'a'}),
    ("STORE_SUBSCR", "test_STORE_SUBSCR(d, key, val)", {'d': {}, 'key': 'a', 'val': 1}),
]

# === Measure each ===

print("\nRunning benchmarks...\n")
results = []
common_globals = globals().copy()
x, y = 1, 2

for name, stmt, local_setup in benchmarks:
    # Merge globals + setup
    setup = {'x': x, 'y': y, **local_setup}
    t = timeit.timeit(stmt=stmt, globals={**common_globals, **setup}, number=100000)
    avg_time = t * 1e6 / 100000  # µs
    print(f"{name:<15}: {avg_time:.3f} µs")
    results.append((name, avg_time))

# === Plotting ===

names = [name for name, _ in results]
times = [time for _, time in results]

plt.figure(figsize=(10, 5))
bars = plt.bar(names, times, color='mediumslateblue')
plt.xticks(rotation=45)
plt.ylabel("Time per execution (µs)")
plt.title("Precise Microbenchmark of Python Bytecode Instructions")

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f"{yval:.2f}", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.show()
