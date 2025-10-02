from vm import VM
from compiler import compile_file
from ir_optimizer import optimize
from ir_optimizer_advanced import advanced_optimize
from profiler import RuntimeProfiler
from feedback_optimizer import FeedbackDirectedOptimizer, TieredCompiler
from jit_compiler import JITRuntime
import sys

def ir_to_bytecode(ir):
    """Convert IR instructions to VM bytecode"""
    bytecode = []
    for ins in ir:
        if ins.op == "const":
            bytecode.append(("LOAD_CONST", ins.a))
            if ins.dest:
                bytecode.append(("STORE_VAR", ins.dest))
        elif ins.op in {"+", "-", "*", "/", "<<", ">>", "//"}:
            # Handle left operand
            if isinstance(ins.a, (int, float)):
                bytecode.append(("LOAD_CONST", ins.a))
            else:
                bytecode.append(("LOAD_VAR", ins.a))
                
            # Handle right operand  
            if isinstance(ins.b, (int, float)):
                bytecode.append(("LOAD_CONST", ins.b))
            else:
                bytecode.append(("LOAD_VAR", ins.b))
                
            # Add the operation
            if ins.op == "+": 
                bytecode.append(("BINARY_ADD", None))
            elif ins.op == "-": 
                bytecode.append(("BINARY_SUB", None))
            elif ins.op == "*": 
                bytecode.append(("BINARY_MUL", None))
            elif ins.op == "/": 
                bytecode.append(("BINARY_DIV", None))
            elif ins.op == "//": 
                bytecode.append(("BINARY_FLOORDIV", None))
            elif ins.op == "<<": 
                bytecode.append(("BINARY_SHL", None))
            elif ins.op == ">>": 
                bytecode.append(("BINARY_SHR", None))
            
            # Store result if there's a destination
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
            # Profile annotations - ignored in execution but useful for debugging
            bytecode.append(("PROFILE_ANNOTATION", f"{ins.op}:{ins.dest}"))
            
    return bytecode

def ir_to_bytecode(ir):
    """Convert IR instructions to VM bytecode"""
    bytecode = []
    for ins in ir:
        if ins.op == "const":
            bytecode.append(("LOAD_CONST", ins.a))
            if ins.dest:
                bytecode.append(("STORE_VAR", ins.dest))
        elif ins.op in {"+", "-", "*", "/", "<<", ">>", "//"}:
            # Handle left operand
            if isinstance(ins.a, (int, float)):
                bytecode.append(("LOAD_CONST", ins.a))
            else:
                bytecode.append(("LOAD_VAR", ins.a))
                
            # Handle right operand  
            if isinstance(ins.b, (int, float)):
                bytecode.append(("LOAD_CONST", ins.b))
            else:
                bytecode.append(("LOAD_VAR", ins.b))
                
            # Add the operation
            if ins.op == "+": 
                bytecode.append(("BINARY_ADD", None))
            elif ins.op == "-": 
                bytecode.append(("BINARY_SUB", None))
            elif ins.op == "*": 
                bytecode.append(("BINARY_MUL", None))
            elif ins.op == "/": 
                bytecode.append(("BINARY_DIV", None))
            elif ins.op == "//": 
                bytecode.append(("BINARY_FLOORDIV", None))
            elif ins.op == "<<": 
                bytecode.append(("BINARY_SHL", None))
            elif ins.op == ">>": 
                bytecode.append(("BINARY_SHR", None))
            
            # Store result if there's a destination
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
            # Profile annotations - ignored in execution but useful for debugging
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

def simulate_profiling(profiler: RuntimeProfiler):
    """Simulate runtime profiling data for demonstration"""
    # Simulate type profiling
    profiler.profile_variable_type("a", 5)
    profiler.profile_variable_type("a", 5)
    profiler.profile_variable_type("a", 5)  # Multiple observations
    
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

def demonstrate_optimizations(original_ir, optimized_ir, advanced_ir, feedback_ir):
    """Show optimization progress and statistics"""
    print("\n" + "="*50)
    print("OPTIMIZATION ANALYSIS")
    print("="*50)
    print(f"Original instructions:      {len(original_ir)}")
    print(f"After basic optimizations:  {len(optimized_ir)}")
    print(f"After advanced optimizations: {len(advanced_ir)}")
    print(f"After feedback optimization: {len(feedback_ir)}")
    
    total_reduction = len(original_ir) - len(feedback_ir)
    percentage_reduction = (total_reduction / len(original_ir)) * 100 if original_ir else 0
    
    print(f"Total reduction:           {total_reduction} instructions ({percentage_reduction:.1f}%)")
    print("="*50)

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/run.py <filename.mvm>")
        print("Available examples:")
        print("  python src/run.py examples/fib.mvm")
        print("  python src/run.py examples/advanced.mvm") 
        print("  python src/run.py examples/working_functions.mvm")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Debug: Show file content
    print("="*60)
    print(f"LOADING: {filename}")
    print("="*60)
    try:
        with open(filename) as f:
            file_content = f.read()
            print(file_content)
        print("="*60)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    
    # Compile the source file to IR
    print("\n" + "="*60)
    print("COMPILATION PIPELINE")
    print("="*60)
    
    original_ir = compile_file(filename)
    
    print("ORIGINAL INTERMEDIATE REPRESENTATION (IR):")
    print("-" * 40)
    for i, instr in enumerate(original_ir):
        print(f"{i:2d}: {instr}")
    
    # Find which variables are used for dead code elimination
    used_vars = find_all_used_vars(original_ir)
    print(f"\nVariables used: {used_vars}")
    
    # Initialize profiling and optimization systems
    print("\n" + "="*60)
    print("PROFILING & OPTIMIZATION SYSTEM")
    print("="*60)
    
    profiler = RuntimeProfiler()
    feedback_optimizer = FeedbackDirectedOptimizer(profiler)
    tiered_compiler = TieredCompiler()
    
    # Simulate profiling data (in real system, this would come from actual execution)
    simulate_profiling(profiler)
    
    # Show profile report
    print("\nRUNTIME PROFILE REPORT:")
    print("-" * 40)
    print(profiler.generate_profile_report())
    
    # Apply optimization pipeline
    print("\nOPTIMIZATION PIPELINE:")
    print("-" * 40)
    
    # 1. Basic optimizations
    print("Applying basic optimizations...")
    optimized_ir = optimize(original_ir, used_vars=used_vars)
    print("BASIC OPTIMIZED IR:")
    for i, instr in enumerate(optimized_ir):
        print(f"{i:2d}: {instr}")
    
    # 2. Advanced optimizations
    print("\nApplying advanced optimizations...")
    advanced_ir = advanced_optimize(original_ir, used_vars=used_vars)
    print("ADVANCED OPTIMIZED IR:")
    for i, instr in enumerate(advanced_ir):
        print(f"{i:2d}: {instr}")
    
    # 3. Feedback-directed optimizations
    print("\nApplying feedback-directed optimizations...")
    feedback_ir = feedback_optimizer.optimize_with_feedback(advanced_ir)
    print("FEEDBACK-OPTIMIZED IR:")
    for i, instr in enumerate(feedback_ir):
        print(f"{i:2d}: {instr}")
    
    # Demonstrate JIT compilation concepts
    print("\n" + "="*60)
    print("JIT COMPILATION DEMONSTRATION")
    print("="*60)
    
    jit_runtime = JITRuntime()
    try:
        jit_functions = jit_runtime.jit_compile_expression(feedback_ir)
        print("JIT Compiled Functions:")
        for var, func in jit_functions:
            result = func()
            print(f"  {var} = {result}")
    except Exception as e:
        print(f"JIT compilation demo skipped: {e}")
    
    # Demonstrate tiered compilation
    print("\n" + "="*60)
    print("TIERED COMPILATION DECISIONS")
    print("="*60)
    
    test_functions = ["main", "factorial", "multiply", "helper"]
    for func_name in test_functions:
        tier = tiered_compiler.get_compilation_tier(func_name)
        tiers = ["Interpreter", "Baseline JIT", "Optimizing JIT"]
        call_count = tiered_compiler.profiler.function_profiles.get(func_name, 0)
        print(f"  {func_name:12} -> {tiers[tier]:15} (tier {tier}, called {call_count} times)")
    
    # Show optimization analysis
    demonstrate_optimizations(original_ir, optimized_ir, advanced_ir, feedback_ir)
    
    # Generate and execute bytecode
    print("\n" + "="*60)
    print("BYTECODE GENERATION & EXECUTION")
    print("="*60)
    
    bytecode = ir_to_bytecode(feedback_ir)
    
    print("GENERATED BYTECODE:")
    print("-" * 40)
    for i, (op, arg) in enumerate(bytecode):
        print(f"{i:2d}: {op:15} {arg if arg is not None else ''}")
    
    print("\n" + "="*60)
    print("PROGRAM OUTPUT")
    print("="*60)
    
    vm = VM()
    vm.run(bytecode)
    
    print("="*60)
    print("EXECUTION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()