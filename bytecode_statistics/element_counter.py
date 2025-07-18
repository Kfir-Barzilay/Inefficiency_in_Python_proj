#!/usr/bin/env python3

#to run : python3 element_counter.py benchmark.py

import sys
import dis
import types
from collections import Counter

def collect_code_objects(co):
    """Recursively yield code objects (including nested ones)."""
    yield co
    for const in co.co_consts:
        if isinstance(const, types.CodeType):
            yield from collect_code_objects(const)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <python_source.py>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, 'r') as f:
        src = f.read()

    # compile the source to a code object
    top_co = compile(src, path, 'exec')

    hist = Counter()
    # walk every code object, disassemble and count LOAD_CONST by type
    for co in collect_code_objects(top_co):
        for instr in dis.get_instructions(co):
            if instr.opname == 'LOAD_CONST':
                val = instr.argval
                hist[type(val).__name__] += 1

    if not hist:
        print("No constants loaded (no LOAD_CONST found).")
        return

    # print histogram sorted by descending count
    for typ, cnt in hist.most_common():
        print(f"pyobject {typ} - {cnt}")

if __name__ == "__main__":
    main()
