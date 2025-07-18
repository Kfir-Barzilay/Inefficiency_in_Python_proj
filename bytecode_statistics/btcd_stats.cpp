#!/usr/bin/env python3
import sys, dis, io, linecache, types, os

# ---------- helpers ---------------------------------------------------------

def _collect_code_objects(co):
    """Recursively yield every nested code object inside *co*."""
    yield co
    for const in co.co_consts:
        if isinstance(const, types.CodeType):
            yield from _collect_code_objects(const)


def _format_instr(instr, count):
    """Pretty‑print a dis.Instruction with its dynamic execution count."""
    start = f"{instr.starts_line:>3}" if instr.starts_line is not None else "   "
    return f"{start}{'':>11}{instr.offset:>4} {instr.opname:<20}{instr.argrepr:<24} | {count} times"


def _is_small_value(val):
    """Classify *val* by payload size.

    Returns:
        True   – if payload \u2264 8 bytes (ints that fit in 64 bits, IEEE double, \n                   bytes/str length \u2264 8, etc.)
        False  – if payload > 8 bytes
        None   – if value type is not supported / should be ignored
    """
    if isinstance(val, bool):               # bool is a tiny int
        return True
    if isinstance(val, int):
        return val.bit_length() <= 64       # fits into 8 bytes
    if isinstance(val, float):
        return True                         # IEEE‑754 double
    if isinstance(val, (bytes, bytearray, str)):
        return len(val) <= 8
    return None                             # complex objects – ignore

# ---------- static phase ----------------------------------------------------

def static_info(path):
    """Parse *path* and return static byte‑code info."""
    src = open(path, 'r', encoding='utf-8').read()
    top_code = compile(src, path, 'exec')

    # Full disassembly text (for reference)
    buf = io.StringIO()
    dis.dis(top_code, file=buf)
    bytecode_txt = buf.getvalue()

    opcode_hist = {}
    instr_lookup = {}
    for co in _collect_code_objects(top_code):
        for ins in dis.get_instructions(co):
            opcode_hist[ins.opname] = opcode_hist.get(ins.opname, 0) + 1
            instr_lookup[(co, ins.offset)] = ins

    return top_code, bytecode_txt, opcode_hist, instr_lookup

# ---------- dynamic phase ---------------------------------------------------

def dynamic_trace(top_code, instr_lookup):
    """Run *top_code* under a tracer and gather dynamic statistics."""
    opcode_exec = {}
    instr_exec = {}
    line_exec = {}
    seen_codes = set()

    load_small = 0  # payload \u2264 8 bytes
    load_big = 0    # payload  > 8 bytes

    def tracer(frame, event, arg):
        nonlocal load_small, load_big

        if event == "call":
            # Enable per‑opcode tracing inside this new frame
            frame.f_trace_opcodes = True
            return tracer

        if event == "opcode":
            co, off = frame.f_code, frame.f_lasti
            seen_codes.add(co)

            op = co.co_code[off]
            opname = dis.opname[op]
            opcode_exec[opname] = opcode_exec.get(opname, 0) + 1
            instr_exec[(co, off)] = instr_exec.get((co, off), 0) + 1

            # -------- size classification for LOAD_* opcodes --------
            if opname.startswith("LOAD_"):
                ins = instr_lookup.get((co, off))
                val = None

                if ins is not None:
                    if ins.opname == "LOAD_CONST":
                        val = ins.argval
                    elif ins.opname == "LOAD_FAST":
                        val = frame.f_locals.get(ins.argval, None)
                    elif ins.opname in ("LOAD_DEREF", "LOAD_FREE"):
                        cell = frame.f_locals.get(ins.argval, None)
                        if isinstance(cell, types.CellType):
                            val = cell.cell_contents
                    elif ins.opname in ("LOAD_GLOBAL", "LOAD_NAME"):
                        nm = ins.argval
                        val = frame.f_globals.get(nm, frame.f_builtins.get(nm, None))

                cls = _is_small_value(val)
                if cls is not None:
                    if cls:
                        load_small += 1
                    else:
                        load_big += 1
            # --------------------------------------------------------

            # Line‑level execution counts
            lineno = frame.f_lineno
            if lineno is not None:
                line_exec[lineno] = line_exec.get(lineno, 0) + 1
        return tracer

    sys.settrace(tracer)
    try:
        exec(top_code, {"__name__": "__main__"})
    finally:
        sys.settrace(None)

    return (opcode_exec, instr_exec, line_exec, seen_codes,
            load_small, load_big)

# ---------- report ----------------------------------------------------------

def write_report(path, bytecode_txt, static_hist,
                 opcode_exec, instr_exec, line_exec, seen_codes,
                 load_small, load_big,
                 out_dir):

    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "bytecode.txt"), "w", encoding="utf-8") as f:
        f.write("FULL BYTECODE DISASSEMBLY:\n")
        f.write(bytecode_txt)

    with open(os.path.join(out_dir, "static_histogram.txt"), "w", encoding="utf-8") as f:
        f.write("STATIC OPCODE COUNTS (appearance in byte‑code):\n")
        for op, c in sorted(static_hist.items(), key=lambda kv: kv[1], reverse=True):
            f.write(f"{op:20} {c} times\n")

    with open(os.path.join(out_dir, "dynamic_instr_counts.txt"), "w", encoding="utf-8") as f:
        f.write("DYNAMIC EXECUTION COUNTS PER INSTRUCTION:\n")
        for co in _collect_code_objects(compile(open(path, encoding='utf-8').read(), path, 'exec')):
            for instr in dis.get_instructions(co):
                cnt = instr_exec.get((co, instr.offset), 0)
                f.write(_format_instr(instr, cnt) + "\n")

    with open(os.path.join(out_dir, "dynamic_opcode_line_counts.txt"), "w", encoding="utf-8") as f:
        f.write("DYNAMIC OPCODE EXECUTION COUNTS:\n")
        for op, c in sorted(opcode_exec.items(), key=lambda kv: kv[1], reverse=True):
            f.write(f"{op:20} {c} times\n")
        f.write("\nDYNAMIC SOURCE‑LINE EXECUTION COUNTS:\n")
        for ln in sorted(k for k in line_exec if k is not None):
            c = line_exec[ln]
            src = linecache.getline(path, ln).rstrip()
            f.write(f"Line {ln:3}: executed {c:6} times | {src}\n")

    with open(os.path.join(out_dir, "load_size_summary.txt"), "w", encoding="utf-8") as f:
        f.write("LOAD‑COMMAND SIZE CLASSIFICATION (dynamic):\n")
        f.write(f"\u2264 8‑byte payload : {load_small}\n")
        f.write(f"> 8‑byte payload : {load_big}\n")

    print(f"[*] Report written to folder '{out_dir}'")

# ---------- main ------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <script.py>")
        sys.exit(1)

    target = sys.argv[1]
    exec_name = os.path.splitext(os.path.basename(target))[0]
    out_folder = f"{exec_name}_folder"

    print(f"[*] analysing {target} \u2192 outputs to ./{out_folder}/")

    top_code, bytecode_txt, static_hist, instr_lookup = static_info(target)
    (opcode_exec, instr_exec, line_exec, seen_codes,
     load_small, load_big) = dynamic_trace(top_code, instr_lookup)

    write_report(target, bytecode_txt, static_hist,
                 opcode_exec, instr_exec, line_exec, seen_codes,
                 load_small, load_big,
                 out_folder)


if __name__ == "__main__":
    main()
