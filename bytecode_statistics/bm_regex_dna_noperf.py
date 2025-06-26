#!/usr/bin/env python3
"""
Standalone version of the regex-dna benchmark from
The Computer Language Benchmarks Game.
"""

import bisect
import re
import time

DEFAULT_INIT_LEN = 100_000
DEFAULT_RNG_SEED = 42

ALU = (
    'GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG'
    'GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA'
    'CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT'
    'ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA'
    'GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG'
    'AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC'
    'AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA'
)

IUB = list(zip('acgtBDHKMNRSVWY', [0.27, 0.12, 0.12, 0.27] + [0.02] * 11))

HOMOSAPIENS = [
    ('a', 0.3029549426680),
    ('c', 0.1979883004921),
    ('g', 0.1975473066391),
    ('t', 0.3015094502008),
]


def make_cumulative(table):
    probs, chars = [], []
    total = 0.0
    for char, p in table:
        total += p
        probs.append(total)
        chars.append(ord(char))
    return probs, chars


def repeat_fasta(src, n, nprint):
    width = 60
    line_len = len(src)
    extended = (src * ((n // line_len) + 2))[:n]
    for i in range(0, n, width):
        nprint(extended[i:i + width].encode('ascii') + b'\n')


def random_fasta(table, n, seed, nprint):
    width = 60
    probs, chars = make_cumulative(table)
    line = bytearray(width + 1)
    im = 139968.0
    seed = float(seed)

    full_lines = n // width
    leftover = n % width
    bb = bisect.bisect

    for _ in range(full_lines):
        for i in range(width):
            seed = (seed * 3877.0 + 29573.0) % im
            line[i] = chars[bb(probs, seed / im)]
        line[60] = 10
        nprint(line)

    if leftover:
        for i in range(leftover):
            seed = (seed * 3877.0 + 29573.0) % im
            line[i] = chars[bb(probs, seed / im)]
        nprint(line[:leftover] + b'\n')

    return seed


def init_benchmarks(n, rng_seed):
    output = bytearray()
    out = output.extend

    out(b'>ONE Homo sapiens alu\n')
    repeat_fasta(ALU, n * 2, out)

    out(b'>TWO IUB ambiguity codes\n')
    seed = random_fasta(IUB, n * 3, rng_seed, out)

    out(b'>THREE Homo sapiens frequency\n')
    random_fasta(HOMOSAPIENS, n * 5, seed, out)

    return bytes(output)


VARIANTS = (
    b'agggtaaa|tttaccct',
    b'[cgt]gggtaaa|tttaccc[acg]',
    b'a[act]ggtaaa|tttacc[agt]t',
    b'ag[act]gtaaa|tttac[agt]ct',
    b'agg[act]taaa|ttta[agt]cct',
    b'aggg[acg]aaa|ttt[cgt]ccct',
    b'agggt[cgt]aa|tt[acg]accct',
    b'agggta[cgt]a|t[acg]taccct',
    b'agggtaa[cgt]|[acg]ttaccct',
)

SUBST = (
    (b'B', b'(c|g|t)'), (b'D', b'(a|g|t)'), (b'H', b'(a|c|t)'),
    (b'K', b'(g|t)'), (b'M', b'(a|c)'), (b'N', b'(a|c|g|t)'),
    (b'R', b'(a|g)'), (b'S', b'(c|g)'), (b'V', b'(a|c|g)'),
    (b'W', b'(a|t)'), (b'Y', b'(c|t)'),
)


def run_benchmarks(seq):
    initial_len = len(seq)
    seq = re.sub(b'>.*\n|\n', b'', seq)
    cleaned_len = len(seq)

    results = [len(re.findall(pat, seq)) for pat in VARIANTS]

    for f, r in SUBST:
        seq = re.sub(f, r, seq)

    return results, initial_len, cleaned_len, len(seq)


def main():
    fasta_length = DEFAULT_INIT_LEN
    rng_seed = DEFAULT_RNG_SEED

    print(f"Generating FASTA input with length {fasta_length}...")
    seq = init_benchmarks(fasta_length, rng_seed)

    print("Running regex DNA benchmark...")
    start = time.perf_counter()
    results, ilen, clen, final_len = run_benchmarks(seq)
    duration = time.perf_counter() - start

    print(f"\nResults:")
    for i, count in enumerate(results, 1):
        print(f"  Pattern {i}: {count} matches")

    print(f"\nInitial FASTA length : {ilen}")
    print(f"Stripped input length: {clen}")
    print(f"Final expanded length: {final_len}")
    print(f"Elapsed time         : {duration:.6f} seconds")


if __name__ == "__main__":
    main()
