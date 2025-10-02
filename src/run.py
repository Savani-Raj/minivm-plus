from vm import VM
from compiler import compile_file
from ir_optimizer import optimize
from ir_optimizer_advanced import advanced_optimize
from jit_compiler import JITRuntime
from profiler import RuntimeProfiler
from feedback_optimizer import FeedbackDirectedOptimizer, TieredCompiler
import sys

def ir_to_bytecode(ir):
    bytecode = []
    for ins in ir:
        if ins.op == "const":
            bytecode.append(("LOAD_CONST", ins.a))
            if ins.dest:
                bytecode.append(("STORE_VAR", ins.dest))
        elif ins.op in {"+", "-", "*", "/", "<<", ">>", "//"}:
            if isinstance(ins.a, (int, float)):
                bytecode.append(("LOAD_CONST", ins.a))
            else:
                bytecode.append(("LOAD_VAR", ins.a))
                
            if isinstance(ins.b, (int, float)):
                bytecode.append(("LOAD_CONST", ins.b))
            else:
                bytecode.append(("LOAD_VAR", ins.b))
                
            if ins.op == "+": bytecode.append(("BINARY_ADD", None))
            elif ins.op == "-": bytecode.append(("BINARY_SUB", None))
            elif ins.op == "*": bytecode.append(("BINARY_MUL", None))
            elif ins.op == "/": bytecode.append(("BINARY_DIV", None))
            elif ins.op == "//": bytecode.append(("BINARY_FLOORDIV", None))
            elif ins.op == "<<": bytecode.append(("BINARY_SHL", None))
            elif ins.op == ">>": bytecode.append(("BINARY_SHR", None))
            
            if ins.dest:
                bytecode.append(("STORE_VAR", ins.dest))
        elif ins.op == "mov":
            if isinstance(ins.a, (int, float)):
                bytecode.append(("LOAD_CONST", ins.a))
            else:
                bytecode.append(("LOAD_VAR", ins.a))
            if ins.dest:
                bytecode.append(("STORE_VAR", ins.dest))
        elif ins.op == "print":
            if isinstance(ins.a, (int, float)):
                bytecode.append(("LOAD_CONST", ins.a))
            else:
                bytecode.append(("LOAD_VAR", ins.a))
            bytecode.append(("PRINT", None))
        elif ins.op in {"hot_annotation", "branch_hint", "inline_candidate"}:
            # Profile annotations - ignored in bytecode but useful for debugging
            bytecode.append(("PROFILE_ANNOTATION", f"{ins.op}:{ins.dest}"))
    return bytecode

def find_all_used_vars(ir):
    """Find all variables that are used in print statements or computations"""
    used_vars = set()
    
    # First pass: find variables used in print statements
    for ins in ir:
        if ins.op == "print" and ins.a:
            used_vars.add(ins.a)
    
    # Second pass: find dependencies of used variables
    changed = True
    while changed:
        changed = False
        for ins in reversed(ir):
            if ins.dest and ins.dest in used_vars:
                if isinstance(ins.a, str) and ins.a not in used_vars:
                    used_vars.add(ins.a)
                    changed = True
                if isinstance(ins.b, str) and ins.b not in used_vars:
                    used_vars.add(ins.b)
                    changed = True
    
    return list(used_vars)

def demonstrate_optimizations(original_ir, optimized_ir, advanced_ir, feedback_ir):
    """Show optimization progress"""
    print("\n=== Optimization Analysis ===")
    print(f"Original instructions: {len(original_ir)}")
    print(f"Basic optimized: {len(optimized_ir)}")
    print(f"Advanced optimized: {len(advanced_ir)}")
    print(f"Feedback optimized: {len(feedback_ir)}")
    print(f"Total reduction: {len(original_ir) - len(feedback_ir)} instructions ({((len(original_ir) - len(feedback_ir)) / len(original_ir) * 100):.1f}%)")

def simulate_profiling(profiler: RuntimeProfiler):
    """Simulate some profiling data for demonstration"""
    # Simulate type profiling
    profiler.profile_variable_type("a", 5)
    profiler.profile_variable_type("a", 5)  # Multiple observations
    profiler.profile_variable_type("a", 5)
    
    profiler.profile_variable_type("b", 10.5)  # Different type
    
    # Simulate block execution profiling
    profiler.profile_block_execution("main")
    for _ in range(1500):  # Make main block hot
        profiler.profile_block_execution("main")
    
    # Simulate branch profiling
    profiler.profile_branch("loop_exit", True)
    profiler.profile_branch("loop_exit", False)
    for _ in range(10):  # Bias the branch
        profiler.profile_branch("loop_exit", True)
    
    # Simulate function calls
    for _ in range(150):  # Make factorial hot
        profiler.profile_function_call("factorial")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/run.py examples/fib.mvm")
        sys.exit(1)
    
    filename = sys.argv[1]
    original_ir = compile_file(filename)
    
    print("=== Original IR ===")
    for i in original_ir: 
        print(i)
    
    # Find which variables are used
    used_vars = find_all_used_vars(original_ir)
    print(f"\nUsed variables: {used_vars}")
    
    # Initialize profiling system
    profiler = RuntimeProfiler()
    feedback_optimizer = FeedbackDirectedOptimizer(profiler)
    tiered_compiler = TieredCompiler()
    
    # Simulate profiling data (in real system, this would come from actual execution)
    simulate_profiling(profiler)
    
    # Show profile report
    print("\n" + profiler.generate_profile_report())
    
    # Basic optimizations
    optimized_ir = optimize(original_ir, used_vars=used_vars)
    
    # Advanced optimizations
    advanced_ir = advanced_optimize(original_ir, used_vars=used_vars)
    
    # Feedback-directed optimizations
    feedback_ir = feedback_optimizer.optimize_with_feedback(advanced_ir)
    
    # Demonstrate JIT compilation concepts
    print("\n=== JIT Compilation Demo ===")
    jit_runtime = JITRuntime()
    jit_functions = jit_runtime.jit_compile_expression(feedback_ir)
    
    for var, func in jit_functions:
        print(f"JIT compiled {var} = {func()}")
    
    # Show optimization analysis
    demonstrate_optimizations(original_ir, optimized_ir, advanced_ir, feedback_ir)
    
    # Demonstrate tiered compilation
    print("\n=== Tiered Compilation Demo ===")
    for func_name in ["main", "factorial", "helper"]:
        tier = tiered_compiler.get_compilation_tier(func_name)
        tiers = ["Interpreter", "Baseline JIT", "Optimizing JIT"]
        print(f"  {func_name}: {tiers[tier]} (tier {tier})")
    
    # Run with VM
    bytecode = ir_to_bytecode(feedback_ir)
    
    print("\n=== Bytecode ===")
    for b in bytecode: 
        print(b)
    
    print("\n=== Program Output ===")
    vm = VM()
    vm.run(bytecode)