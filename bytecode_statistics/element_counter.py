#i want you to write me a python script
#the script will be used ./python3 element_counter.py benchmark.py
#if bench mark is not present print error bm does not exist.
#run the bench mark and dynamiclly count the types of the element that was loaded to the stack!
#i think the element should be insert by pointer. i want you to check the type and present me the types and how many of each type

#!/usr/bin/env python3
# element_counter.py
"""
Usage:
    python3 element_counter.py benchmark.py

Counts (dynamically) the *types* of Python objects that are **pushed onto the
CPython VM stack** by LOAD_* opcodes while running the benchmark.

Requires CPython 3.12+ (uses 'opcode' profiling events). On older versions,
the script exits with an explanatory error.
"""

import sys
import os
import dis
import runpy
import sysconfig
import sys
from collections import Counter

# Opcodes that push something onto the stack (subset we care about)
PUSHING_OPS = {
    "LOAD_CONST",
    "LOAD_FAST",
    "LOAD_GLOBAL",
    "LOAD_DEREF",
    "LOAD_NAME",
    "LOAD_ATTR",   # pushes attribute value
    "LOAD_METHOD", # pushes method object (3.11+)
    "LOAD_CLOSURE"
}

type_counter = Counter()
instr_cache = {}  # code_object -> list(dis.Instruction)

def get_instructions(code):
    ins = instr_cache.get(code)
    if ins is None:
        ins = list(dis.get_instructions(code))
        instr_cache[code] = ins
    return ins

def find_instr_by_offset(code, offset):
    # dis.Instruction.offset is exact in 3.11/3.12
    for ins in get_instructions(code):
        if ins.offset == offset:
            return ins
    return None

def profile_func(frame, event, arg):
    # We only asked for 'opcode' events
    if event != "opcode":
        return

    code = frame.f_code
    offset = frame.f_lasti
    ins = find_instr_by_offset(code, offset)
    if ins is None:
        return

    if ins.opname not in PUSHING_OPS:
        return

    obj_type = None

    try:
        if ins.opname == "LOAD_CONST":
            value = ins.argval
            obj_type = type(value)

        elif ins.opname in {"LOAD_FAST", "LOAD_NAME"}:
            name = ins.argval
            value = frame.f_locals.get(name, frame.f_globals.get(name, None))
            obj_type = type(value)

        elif ins.opname == "LOAD_GLOBAL":
            name = ins.argval
            value = frame.f_globals.get(name, frame.f_builtins.get(name, None))
            obj_type = type(value)

        elif ins.opname in {"LOAD_DEREF", "LOAD_CLOSURE"}:
            idx = ins.arg
            freevars = frame.f_code.co_freevars + frame.f_code.co_cellvars
            if 0 <= idx < len(freevars):
                name = freevars[idx]
                # cellvars are in f_locals; freevars in f_cells (CPython internals)
                value = frame.f_locals.get(name, None)
                if value is None:
                    # Try cell/free var slots
                    cells = frame.f_cells if hasattr(frame, "f_cells") else ()
                    if 0 <= idx < len(cells):
                        value = cells[idx].cell_contents
                obj_type = type(value)
            else:
                obj_type = type(None)

        elif ins.opname == "LOAD_ATTR":
            # value is top-of-stack attr access, we cannot see it directly.
            # Best-effort: evaluate attribute manually from locals/globals if simple NAME before
            # but that's fragile. We'll skip or mark as unknown.
            obj_type = "_unknown_attr_"

        elif ins.opname == "LOAD_METHOD":
            obj_type = "_method_obj_"

        else:
            obj_type = "_unknown_"

    except Exception:
        obj_type = "_error_while_resolving_"

    if isinstance(obj_type, type):
        key = obj_type.__module__ + "." + obj_type.__name__
    else:
        key = str(obj_type)

    type_counter[key] += 1


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 element_counter.py benchmark.py", file=sys.stderr)
        sys.exit(1)

    target = sys.argv[1]
    if not os.path.exists(target):
        print("error: bm does not exist.", file=sys.stderr)
        sys.exit(1)

    # Check Python version for opcode events
    if sys.version_info < (3, 12):
        print("error: This script requires Python 3.12+ (opcode profiling events).", file=sys.stderr)
        sys.exit(1)

    # Turn on opcode events
    sys.setprofile(profile_func)
    sys.setswitchinterval(0.0005)  # keep interpreter responsive

    try:
        runpy.run_path(target, run_name="__main__")
    finally:
        sys.setprofile(None)

    # Print results
    print("=== Element types pushed to the VM stack ===")
    for t, c in type_counter.most_common():
        print(f"{t}: {c}")

if __name__ == "__main__":
    main()
