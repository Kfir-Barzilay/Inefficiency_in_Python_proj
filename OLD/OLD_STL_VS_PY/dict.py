import time

def insert_benchmark(d, N):
    for i in range(N):
        d[i] = i

def lookup_benchmark(d, N):
    for i in range(N):
        _ = d[i]

def main():
    N = 1_000_000
    d = {}

    start = time.time()
    insert_benchmark(d, N)
    mid = time.time()
    lookup_benchmark(d, N)
    end = time.time()

    print(f"Python dict insert time: {mid - start}")
    print(f"Python dict lookup time: {end - mid}")

if __name__ == "__main__":
    main()
