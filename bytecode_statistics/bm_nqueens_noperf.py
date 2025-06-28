"""Simple, brute-force N-Queens solver."""

import time

__author__ = "collinwinter@google.com (Collin Winter)"

# Pure-Python implementation of itertools.permutations().
def permutations(iterable, r=None):
    pool = tuple(iterable)
    n = len(pool)
    if r is None:
        r = n
    indices = list(range(n))
    cycles = list(range(n - r + 1, n + 1))[::-1]
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i + 1:] + indices[i:i + 1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return


def n_queens(queen_count):
    """Brute-force N-Queens solver yielding all valid solutions."""
    cols = range(queen_count)
    for vec in permutations(cols):
        if (queen_count == len(set(vec[i] + i for i in cols))
                        == len(set(vec[i] - i for i in cols))):
            yield vec


def bench_n_queens(queen_count):
    return list(n_queens(queen_count))


if __name__ == "__main__":
    queen_count = 8

    print(f"Solving {queen_count}-Queens problem...")
    start = time.perf_counter()
    solutions = bench_n_queens(queen_count)
    duration = time.perf_counter() - start

    print(f"Found {len(solutions)} solutions")
    print(f"Elapsed time: {duration:.6f} seconds")
