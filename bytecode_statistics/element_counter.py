#!/usr/bin/env python3
"""
element_counter.py

Dynamically trace a Python script to count the number of times each constant type
is loaded onto the Python VM stack (via LOAD_CONST) and print a histogram.

Usage:
    python3 element_counter.py benchmark.py
"""
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
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    # Compile the target script
    top_co = compile(src, path, 'exec')

    # Precompute mapping of LOAD_CONST offsets to constant values for each code object
    const_map = {}
    for co in collect_code_objects(top_co):
        const_map[co] = {
            instr.offset: instr.argval
            for instr in dis.get_instructions(co)
            if instr.opname == 'LOAD_CONST'
        }

    # Histogram for types
    hist = Counter()

    # Tracer function to count dynamic LOAD_CONST events
    def tracer(frame, event, arg):
        if event == 'call':
            # Enable opcode-level tracing for this frame
            frame.f_trace_opcodes = True
            return tracer
        if event == 'opcode':
            co = frame.f_code
            off = frame.f_lasti
            # Get opcode numeric and name
            op = co.co_code[off]
            opname = dis.opname[op]
            if opname == 'LOAD_CONST':
                # Lookup the constant value loaded at this offset
                val = const_map.get(co, {}).get(off)
                typ = type(val).__name__ if val is not None else 'Unknown'
                hist[typ] += 1
        return tracer

    # Install tracer and execute the code
    sys.settrace(tracer)
    try:
        exec(top_co, {'__name__': '__main__'})
    finally:
        sys.settrace(None)

    # Print the histogram sorted by count
    for typ, cnt in hist.most_common():
        print(f"pyobject {typ} - {cnt}")


if __name__ == '__main__':
    main()
