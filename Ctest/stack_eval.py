import timeit
import dis

# --- Setup ---
# We'll use a large number of iterations within the timed statement.
# The number of iterations for timeit itself can be smaller if the inner loop is large.
timeit_number = 1000
loop_iterations = 10000 # Number of pushes/pops within the function

# --- Test Function for PUSH (LOAD_CONST) and POP (POP_TOP) ---
# We want a function that does many LOAD_CONST followed by POP_TOP.
# A simple way is to assign to a dummy variable in a loop,
# but the STORE_FAST/LOAD_FAST can add noise.
# Let's try a more direct approach within a list comprehension that's not stored,
# or a generator expression that's consumed, to emphasize LOAD_CONST and the stack.

# This still has some overhead, but it's a common pattern.
# The idea is that 'None' gets pushed and then popped by the list comprehension machinery
# or by the consumption of a generator.

# Option 1: List comprehension (might optimize differently)
# setup_code_push_pop = "pass" # No setup needed beyond the stmt
# stmt_push_pop = "[None for _ in range(loop_iterations)]"

# Option 2: Function with explicit load and pop (more controlled)
# This is better for analysis with 'dis'.
def push_pop_n_times(n):
    """
    Attempts to do n LOAD_CONST and n POP_TOP operations.
    The value '0' is loaded and then immediately popped.
    """
    for _ in range(n):
        # This sequence aims for LOAD_CONST followed by POP_TOP
        # However, Python's assignment might optimize this in unexpected ways.
        # A direct way to see this is to have a value on stack and then pop it.
        #
        # Consider bytecode of:
        #   0 LOAD_CONST 0 (0)
        #   2 POP_TOP
        #   4 LOAD_CONST 0 (None)
        #   6 RETURN_VALUE
        #
        # A loop like this:
        # for _ in range(n):
        #     _ = 0 # LOAD_CONST, STORE_FAST
        # might not be what we want.

        # Let's try a function whose bytecode is simpler for this.
        pass # placeholder

# Let's make a string that represents the loop for timeit directly
# to minimize function call overhead for `push_pop_n_times` itself.

# We want to execute the bytecode:
#   LOAD_CONST 0
#   POP_TOP
# repeatedly.

# Python doesn't have a direct way to write bytecode for timeit.
# We write Python that generates this. A simple unused expression
# like `0` on a line by itself in a loop often does this.

stmt_push_pop = """
for _ in range(loop_iterations):
    0 # This should be LOAD_CONST 0, then implicitly popped if not used.
      # However, the interpreter might optimize it away if truly unused.
      # A slightly better way:
      # x = 0 # LOAD_CONST 0, STORE_FAST x
      # del x # DELETE_FAST x (doesn't involve stack pop of the value)
      #
      # Let's try to force a pop.
      # We can use a structure that consumes values from the stack.
      # A function call with arguments pops them.
      # An expression statement 'expr' compiles to:
      #   ... bytecode for expr ...
      #   POP_TOP
"""

# A better controlled statement:
# We define a simple function `do_nothing(val)` and call it.
# The call will pop `val` from the stack.
setup_code_push_pop = f"""
loop_iterations = {loop_iterations}
def consume(val): pass
"""
stmt_push_pop = """
for _ in range(loop_iterations):
    consume(0) # 0 is LOAD_CONST, then `consume` call setup pops it
"""

# Analyze the bytecode of the inner part of the stmt
# To do this, we need to compile the loop body.
# Let's analyze: consume(0)
# def temp_func(): consume(0)
# dis.dis(temp_func)
# Will show:
# LOAD_GLOBAL (or LOAD_FAST if consume is local) 'consume'
# LOAD_CONST 0 (0)
# CALL_FUNCTION 1 (or PRECALL + CALL)
# POP_TOP (result of function call, which is None)

# This involves more than just LOAD_CONST and the argument pop.
# The CALL_FUNCTION itself has overhead.

# --- Let's refine for a more direct LOAD_CONST -> POP_TOP ---
# The bytecode for an expression statement `expr` is:
#   ... bytecode for expr ...
#   POP_TOP
# So, if `expr` is just a constant, it's `LOAD_CONST` then `POP_TOP`.

stmt_direct_push_pop = f"""
for _ in range({loop_iterations}):
    0 # Expression statement: LOAD_CONST 0 (0), then POP_TOP
"""
setup_direct_push_pop = "" # No special setup needed

# Let's verify the bytecode for the loop body: "0"
# co = compile("0", "<string>", "exec")
# dis.dis(co)
# This should show:
#   1           0 LOAD_CONST               0 (0)
#               2 POP_TOP
#               4 LOAD_CONST               1 (None) # from the implicit return of the exec block
#               6 RETURN_VALUE

# So, within the loop, "0" indeed becomes LOAD_CONST then POP_TOP.
# The loop itself adds FOR_ITER, JUMP_ABSOLUTE etc.

# --- Benchmarking ---

# 1. Time the loop with the operations
print(f"Benchmarking {loop_iterations} (LOAD_CONST + POP_TOP) operations, repeated by timeit.\n")

total_time_direct = min(timeit.repeat(stmt_direct_push_pop,
                                      setup=setup_direct_push_pop,
                                      number=timeit_number,
                                      repeat=5)) # Use repeat for stability

avg_time_per_run_direct = total_time_direct / timeit_number
avg_time_per_push_pop_pair = avg_time_per_run_direct / loop_iterations

print(f"--- Direct LOAD_CONST + POP_TOP (using expression statement '0') ---")
print(f"Min total time for {timeit_number} runs of {loop_iterations} pairs: {total_time_direct:.6f} seconds")
print(f"Average time per run: {avg_time_per_run_direct:.10f} seconds")
print(f"Average time per (LOAD_CONST + POP_TOP) pair: {avg_time_per_push_pop_pair:.12f} seconds")
# This gives us the time for one push AND one pop.

# 2. Time an "empty" loop to estimate loop overhead
# This is an attempt to subtract overhead, but it's imperfect as
# the mere presence of operations can change how the loop itself behaves or is optimized.
stmt_empty_loop = f"""
for _ in range({loop_iterations}):
    pass # The 'pass' statement also has some (minimal) bytecode
"""
setup_empty_loop =""

# dis.dis(compile("pass", "<string>", "exec")) shows `LOAD_CONST 0 (None), RETURN_VALUE`
# dis.dis(compile("for _ in range(1): pass", "<string>", "exec")) will show loop structure.

total_time_empty_loop = min(timeit.repeat(stmt_empty_loop,
                                          setup=setup_empty_loop,
                                          number=timeit_number,
                                          repeat=5))

avg_time_per_run_empty_loop = total_time_empty_loop / timeit_number
avg_time_per_empty_loop_iteration = avg_time_per_run_empty_loop / loop_iterations

print(f"\n--- Empty Loop Overhead ---")
print(f"Min total time for {timeit_number} runs of {loop_iterations} 'pass' iterations: {total_time_empty_loop:.6f} seconds")
print(f"Average time per run: {avg_time_per_run_empty_loop:.10f} seconds")
print(f"Average time per 'pass' iteration (loop overhead estimate): {avg_time_per_empty_loop_iteration:.12f} seconds")

# 3. Subtracting overhead (use with caution)
estimated_time_for_pair_ops_only = avg_time_per_push_pop_pair - avg_time_per_empty_loop_iteration
print(f"\n--- Estimated Time (with overhead subtraction attempt) ---")
if estimated_time_for_pair_ops_only > 0:
    print(f"Estimated time for (LOAD_CONST + POP_TOP) excluding loop overhead: {estimated_time_for_pair_ops_only:.12f} seconds")
    print(f"Estimated time per single stack op (push or pop, assuming they are similar): {(estimated_time_for_pair_ops_only / 2):.12f} seconds")
else:
    print("Could not reliably subtract loop overhead (result was zero or negative).")
    print("This indicates the operations are extremely fast and dominated by loop mechanics or measurement noise at this scale.")

print("\n--- Bytecode for the core of the direct push/pop loop ('0') ---")
dis.dis(compile("0", "<string>", "eval")) # 'eval' is better here to see just the expression
# Or, for the statement context:
# fragment = compile("0", "<string>", "exec")
# dis.dis(fragment) # you'll see LOAD_CONST 0, POP_TOP, then LOAD_CONST None, RETURN_VALUE

print("\n--- Bytecode for 'pass' (for overhead reference) ---")
dis.dis(compile("pass", "<string>", "exec")) # 'pass' in eval is just None
# dis.dis(compile("pass", "<string>", "exec")) # More relevant for loop body