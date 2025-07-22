#!/usr/bin/env python3
"""
Dynamic Type Counter - Tracks types loaded during bytecode execution
Usage: python3 element_counter.py benchmark.py
"""

import sys
import types
import importlib.util
import traceback
from collections import defaultdict, Counter
import dis
import gc

class BytecodeTypeTracker:
    def __init__(self):
        self.operation_counts = Counter()
        self.type_loads = Counter()
        self.value_types = Counter()
        self.tracking = False
        self.original_trace = None
        
    def start_tracking(self):
        """Start tracing bytecode execution"""
        self.tracking = True
        self.original_trace = sys.gettrace()
        sys.settrace(self._trace_calls)
        
    def stop_tracking(self):
        """Stop tracing bytecode execution"""
        self.tracking = False
        sys.settrace(self.original_trace)
        
    def _trace_calls(self, frame, event, arg):
        """Trace function calls and returns"""
        if event == 'call':
            # Set line tracer for this frame
            return self._trace_lines
        return None
        
    def _trace_lines(self, frame, event, arg):
        """Trace line execution and analyze bytecode"""
        if not self.tracking:
            return
            
        if event == 'line':
            # Get the current instruction
            code = frame.f_code
            lasti = frame.f_lasti
            
            # Find the instruction at current position
            for instruction in dis.get_instructions(code):
                if instruction.offset == lasti:
                    self._analyze_instruction(instruction, frame)
                    break
                    
        return self._trace_lines
    
    def _analyze_instruction(self, instr, frame):
        """Analyze a single bytecode instruction"""
        opname = instr.opname
        self.operation_counts[opname] += 1
        
        # Track LOAD operations
        if opname in ['LOAD_GLOBAL', 'LOAD_NAME', 'LOAD_FAST', 'LOAD_DEREF']:
            var_name = instr.argval
            self.type_loads[f"LOAD:{var_name}"] += 1
            
            # Try to get the actual value and its type
            try:
                if opname == 'LOAD_GLOBAL':
                    if var_name in frame.f_globals:
                        value = frame.f_globals[var_name]
                        self._track_value_type(value, f"global:{var_name}")
                elif opname == 'LOAD_FAST':
                    if var_name in frame.f_locals:
                        value = frame.f_locals[var_name]
                        self._track_value_type(value, f"local:{var_name}")
            except:
                pass  # Ignore errors in value access
                
        elif opname == 'LOAD_CONST':
            const_val = instr.argval
            self.type_loads[f"CONST:{type(const_val).__name__}"] += 1
            self._track_value_type(const_val, "const")
            
        elif opname == 'LOAD_ATTR':
            attr_name = instr.argval
            self.type_loads[f"ATTR:{attr_name}"] += 1
            
        # Track BUILD operations
        elif opname.startswith('BUILD_'):
            structure_type = opname.replace('BUILD_', '').lower()
            count = instr.argval or 0
            self.type_loads[f"BUILD:{structure_type}"] += 1
            self.value_types[f"built_{structure_type}"] += 1
            
        # Track CALL operations
        elif opname.startswith('CALL_'):
            self.type_loads[f"CALL:{opname}"] += 1
            
        # Track STORE operations
        elif opname in ['STORE_GLOBAL', 'STORE_NAME', 'STORE_FAST', 'STORE_DEREF']:
            var_name = instr.argval
            self.type_loads[f"STORE:{var_name}"] += 1
    
    def _track_value_type(self, value, context):
        """Track the type of a loaded value"""
        if value is not None:
            type_name = type(value).__name__
            module_name = getattr(type(value), '__module__', 'builtins')
            full_type = f"{module_name}.{type_name}" if module_name != 'builtins' else type_name
            self.value_types[f"{context}:{full_type}"] += 1

def analyze_benchmark_file(benchmark_file):
    """Analyze the benchmark file statically first"""
    print(f"🔍 Static Analysis of: {benchmark_file}")
    print("=" * 60)
    
    try:
        with open(benchmark_file, 'r') as f:
            code_content = f.read()
            
        # Compile the code
        compiled_code = compile(code_content, benchmark_file, 'exec')
        
        # Analyze bytecode statically
        print("\n📋 STATIC BYTECODE ANALYSIS:")
        print("-" * 40)
        
        static_ops = Counter()
        static_loads = Counter()
        
        def analyze_code_object(code_obj, name="<module>"):
            for instr in dis.get_instructions(code_obj):
                static_ops[instr.opname] += 1
                
                if instr.opname in ['LOAD_GLOBAL', 'LOAD_NAME', 'LOAD_FAST', 'LOAD_DEREF']:
                    static_loads[f"LOAD:{instr.argval}"] += 1
                elif instr.opname == 'LOAD_CONST':
                    const_type = type(instr.argval).__name__
                    static_loads[f"CONST:{const_type}"] += 1
                elif instr.opname == 'LOAD_ATTR':
                    static_loads[f"ATTR:{instr.argval}"] += 1
                elif instr.opname.startswith('BUILD_'):
                    structure = instr.opname.replace('BUILD_', '').lower()
                    static_loads[f"BUILD:{structure}"] += 1
                elif instr.opname.startswith('CALL_'):
                    static_loads[f"CALL:{instr.opname}"] += 1
                    
            # Recursively analyze nested code objects
            for const in code_obj.co_consts:
                if isinstance(const, types.CodeType):
                    analyze_code_object(const, const.co_name)
        
        analyze_code_object(compiled_code)
        
        print("Top Bytecode Operations:")
        for op, count in static_ops.most_common(10):
            print(f"  {op:<20} {count:>6}")
            
        print("\nTop Load/Build Operations:")
        for load, count in static_loads.most_common(15):
            print(f"  {load:<30} {count:>6}")
            
        return compiled_code, static_ops, static_loads
        
    except Exception as e:
        print(f"❌ Error in static analysis: {e}")
        return None, Counter(), Counter()

def run_dynamic_analysis(benchmark_file):
    """Run the benchmark with dynamic tracing"""
    print(f"\n🚀 DYNAMIC EXECUTION ANALYSIS:")
    print("=" * 60)
    
    tracker = BytecodeTypeTracker()
    
    try:
        # Load the benchmark module
        spec = importlib.util.spec_from_file_location("benchmark", benchmark_file)
        if spec is None:
            raise ImportError(f"Could not load spec from {benchmark_file}")
            
        benchmark_module = importlib.util.module_from_spec(spec)
        
        # Start tracking
        tracker.start_tracking()
        
        print("Executing benchmark with bytecode tracing...")
        # Execute the benchmark
        spec.loader.exec_module(benchmark_module)
        
        # Stop tracking
        tracker.stop_tracking()
        
        # Display results
        print(f"\n📊 RUNTIME BYTECODE OPERATIONS:")
        print("-" * 40)
        if tracker.operation_counts:
            print("Executed Operations:")
            for op, count in tracker.operation_counts.most_common(15):
                print(f"  {op:<20} {count:>6}")
        
        print(f"\n🎯 RUNTIME TYPE LOADS:")
        print("-" * 40)
        if tracker.type_loads:
            print("Load Operations:")
            for load, count in tracker.type_loads.most_common(20):
                print(f"  {load:<35} {count:>6}")
        
        print(f"\n📈 VALUE TYPES ENCOUNTERED:")
        print("-" * 40)
        if tracker.value_types:
            print("Types of loaded values:")
            for vtype, count in tracker.value_types.most_common(15):
                print(f"  {vtype:<40} {count:>6}")
                
        # Summary
        print(f"\n📊 EXECUTION SUMMARY:")
        print("-" * 40)
        print(f"  Total operations executed: {sum(tracker.operation_counts.values())}")
        print(f"  Total load operations: {sum(tracker.type_loads.values())}")
        print(f"  Unique value types: {len(tracker.value_types)}")
        
        return tracker
        
    except Exception as e:
        print(f"❌ Error in dynamic analysis: {e}")
        traceback.print_exc()
        return None
    finally:
        tracker.stop_tracking()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 element_counter.py benchmark.py")
        sys.exit(1)
    
    benchmark_file = sys.argv[1]
    
    try:
        # Run static analysis first
        compiled_code, static_ops, static_loads = analyze_benchmark_file(benchmark_file)
        
        if compiled_code:
            # Run dynamic analysis
            dynamic_tracker = run_dynamic_analysis(benchmark_file)
            
            # Compare results if both succeeded
            if dynamic_tracker:
                print(f"\n🔄 STATIC vs DYNAMIC COMPARISON:")
                print("-" * 40)
                print("Note: Dynamic counts show actual execution,")
                print("      Static counts show all possible operations")
                
    except FileNotFoundError:
        print(f"❌ File not found: {benchmark_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()