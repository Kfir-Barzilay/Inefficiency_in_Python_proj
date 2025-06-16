#!/usr/bin/env python3
import sys, dis, io, linecache, types

# ---------- helpers ---------------------------------------------------------
def _collect_code_objects(co):
    """Yield given code-object and all nested ones (depth-first)."""
    yield co
    for const in co.co_consts:
        if isinstance(const, types.CodeType):
            yield from _collect_code_objects(const)

def _format_instr(instr, count):
    """Return one disassembly line with an optional “|  N times” suffix."""
    start = f"{instr.starts_line:>3}" if instr.starts_line is not None else "   "
    return f"{start}{'':>11}{instr.offset:>4} {instr.opname:<20}{instr.argrepr:<24} | {count} times"

# ---------- static phase ----------------------------------------------------
def static_info(path):
    src = open(path, 'r').read()
    top_code = compile(src, path, 'exec')

    buf = io.StringIO()
    dis.dis(top_code, file=buf)
    bytecode_txt = buf.getvalue()

    opcode_hist = {}
    # ↓ עבר על כל אובייקט-קוד במודול, בעומק
    for co in _collect_code_objects(top_code):
        for ins in dis.get_instructions(co):
            opcode_hist[ins.opname] = opcode_hist.get(ins.opname, 0) + 1

    return top_code, bytecode_txt, opcode_hist

# ---------- dynamic phase ---------------------------------------------------
def dynamic_trace(top_code):
    opcode_exec = {}                  # opcode -> exec-count
    instr_exec  = {}                  # (code, offset) -> exec-count
    line_exec   = {}                  # lineno -> exec-count
    seen_codes  = set()               # code objects touched

    def tracer(frame, event, arg):
        if event == "call":
            frame.f_trace_opcodes = True
            return tracer
        if event == "opcode":
            co, off = frame.f_code, frame.f_lasti
            seen_codes.add(co)

            op = co.co_code[off]
            opname = dis.opname[op]
            opcode_exec[opname] = opcode_exec.get(opname, 0) + 1

            instr_exec[(co, off)] = instr_exec.get((co, off), 0) + 1

            lineno = frame.f_lineno
            if lineno is not None:                # ← guard against None
                line_exec[lineno] = line_exec.get(lineno, 0) + 1
        return tracer

    sys.settrace(tracer)
    try:
        exec(top_code, {"__name__": "__main__"})
    finally:
        sys.settrace(None)

    return opcode_exec, instr_exec, line_exec, seen_codes

# ---------- report ----------------------------------------------------------
def write_report(path, bytecode_txt, static_hist,
                 opcode_exec, instr_exec, line_exec, seen_codes,
                 out_path="bytecode_stats.txt"):

    with open(out_path, "w", encoding="utf-8") as f:
        # 1. raw byte-code
        f.write("FULL BYTECODE DISASSEMBLY:\n")
        f.write(bytecode_txt)
        f.write("\n")

        # 2. static histogram
        f.write("STATIC OPCODE COUNTS (appearance in byte-code):\n")
        for op, c in sorted(static_hist.items(), key=lambda kv: kv[1], reverse=True):
            f.write(f"{op:20} {c} times\n")
        f.write("\n")

        # 3. dynamic per-instruction counts
        f.write("DYNAMIC EXECUTION COUNTS PER INSTRUCTION:\n")
        for co in _collect_code_objects(compile(open(path).read(), path, 'exec')):
            for instr in dis.get_instructions(co):
                cnt = instr_exec.get((co, instr.offset), 0)
                f.write(_format_instr(instr, cnt) + "\n")
        f.write("\n")

        # 4. dynamic opcode histogram
        f.write("DYNAMIC OPCODE EXECUTION COUNTS:\n")
        for op, c in sorted(opcode_exec.items(), key=lambda kv: kv[1], reverse=True):
            f.write(f"{op:20} {c} times\n")
        f.write("\n")

        # 5. dynamic source-line histogram
        f.write("DYNAMIC SOURCE-LINE EXECUTION COUNTS:\n")
        for ln in sorted(k for k in line_exec if k is not None):    # ← skip None
            c   = line_exec[ln]
            src = linecache.getline(path, ln).rstrip()
            f.write(f"Line {ln:3}: executed {c:6} times | {src}\n")

    print(f"[*] Report written to '{out_path}'")

# ---------- main ------------------------------------------------------------
def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <script.py>")
        sys.exit(1)

    target = sys.argv[1]
    print(f"[*] analysing {target}")

    top_code, bytecode_txt, static_hist = static_info(target)
    opcode_exec, instr_exec, line_exec, seen_codes = dynamic_trace(top_code)
    write_report(target, bytecode_txt, static_hist,
                 opcode_exec, instr_exec, line_exec, seen_codes)

if __name__ == "__main__":
    main()
