from typing import Dict, List, Set, Any, Optional
from ir_optimizer import IRInstr, is_const
from profiler import RuntimeProfiler, TypeProfile

class FeedbackDirectedOptimizer:
    """
    Optimization passes driven by runtime profiling feedback
    Implements profile-guided optimization (PGO)
    """
    
    def __init__(self, profiler: RuntimeProfiler):
        self.profiler = profiler
        self.optimized_versions: Dict[str, List[IRInstr]] = {}
        self.specialized_code: Dict[str, Any] = {}
    
    def specialize_for_types(self, ir_instructions: List[IRInstr]) -> List[IRInstr]:
        """Create type-specialized version of code based on profiling"""
        type_stable_vars = self.profiler.get_type_stable_variables()
        if not type_stable_vars:
            return ir_instructions  # No specialization possible
        
        optimized_ir = []
        type_specializations = {}
        
        for var_name in type_stable_vars:
            type_profile = self.profiler.type_profiles[var_name]
            primary_type = type_profile.get_primary_type()
            if primary_type == int:
                type_specializations[var_name] = 'int'
            elif primary_type == float:
                type_specializations[var_name] = 'float'
        
        # Apply type-specific optimizations
        for ins in ir_instructions:
            if ins.op in {"+", "-", "*", "/"}:
                # Check if we can use type-specific operations
                a_type = type_specializations.get(ins.a)
                b_type = type_specializations.get(ins.b)
                
                if a_type == 'int' and b_type == 'int' and ins.op == '/':
                    # Replace integer division with faster version
                    new_ins = IRInstr("//", ins.dest, a=ins.a, b=ins.b)
                    optimized_ir.append(new_ins)
                    continue
            
            optimized_ir.append(ins)
        
        return optimized_ir
    
    def optimize_hot_paths(self, ir_instructions: List[IRInstr]) -> List[IRInstr]:
        """Apply aggressive optimizations to hot paths"""
        hot_blocks = self.profiler.get_hot_blocks()
        if not hot_blocks:
            return ir_instructions
        
        # In a real implementation, we'd identify hot paths and apply:
        # - More aggressive inlining
        # - Loop unrolling
        # - Advanced vectorization
        
        # For now, we'll just mark hot blocks for special treatment
        optimized_ir = []
        for ins in ir_instructions:
            # Add hot path annotations (would be used by later passes)
            if hasattr(ins, 'dest') and ins.dest in hot_blocks:
                # Mark as hot - in real implementation this would trigger special optimizations
                optimized_ir.append(IRInstr("hot_annotation", f"hot_{ins.dest}"))
            optimized_ir.append(ins)
        
        return optimized_ir
    
    def apply_branch_optimizations(self, ir_instructions: List[IRInstr]) -> List[IRInstr]:
        """Optimize branches based on profiling data"""
        branch_suggestions = self.profiler.get_optimization_suggestions()['branch_predictions']
        if not branch_suggestions:
            return ir_instructions
        
        optimized_ir = []
        
        for ins in ir_instructions:
            # In a real implementation, we'd reorder basic blocks
            # based on branch likelihood and add hint instructions
            if ins.op == "branch" and ins.dest in branch_suggestions:
                prediction = branch_suggestions[ins.dest]
                # Add branch prediction hint
                optimized_ir.append(IRInstr("branch_hint", ins.dest, a=prediction))
            
            optimized_ir.append(ins)
        
        return optimized_ir
    
    def inline_hot_functions(self, ir_instructions: List[IRInstr]) -> List[IRInstr]:
        """Inline frequently called functions"""
        inline_candidates = self.profiler.get_optimization_suggestions()['inline_candidates']
        if not inline_candidates:
            return ir_instructions
        
        # In a real implementation, we'd replace function calls
        # with the function body for hot functions
        
        optimized_ir = []
        for ins in ir_instructions:
            if ins.op == "call" and ins.a in inline_candidates:
                # Mark for inlining (would be implemented in later pass)
                optimized_ir.append(IRInstr("inline_candidate", ins.a))
            optimized_ir.append(ins)
        
        return optimized_ir
    
    def optimize_with_feedback(self, ir_instructions: List[IRInstr]) -> List[IRInstr]:
        """Main feedback-directed optimization pipeline"""
        print("\n=== Applying Feedback-Directed Optimizations ===")
        
        # Apply various profile-guided optimizations
        optimized = ir_instructions
        optimized = self.specialize_for_types(optimized)
        optimized = self.optimize_hot_paths(optimized)
        optimized = self.apply_branch_optimizations(optimized)
        optimized = self.inline_hot_functions(optimized)
        
        # Show what optimizations were applied
        suggestions = self.profiler.get_optimization_suggestions()
        print("Profile-guided optimizations applied:")
        if suggestions['type_specialization']:
            print(f"  - Type specialization for: {suggestions['type_specialization']}")
        if suggestions['hot_blocks']:
            print(f"  - Hot path optimization for {len(suggestions['hot_blocks'])} blocks")
        if suggestions['inline_candidates']:
            print(f"  - Inline candidates identified: {suggestions['inline_candidates']}")
        
        return optimized

class TieredCompiler:
    """
    Multi-tier compilation system based on profiling
    Interpreter → Baseline JIT → Optimizing JIT
    """
    
    def __init__(self):
        self.profiler = RuntimeProfiler()
        self.feedback_optimizer = FeedbackDirectedOptimizer(self.profiler)
        self.optimization_tier = 0  # 0=interpreter, 1=baseline, 2=optimized
        
    def should_compile_to_jit(self, function_name: str) -> bool:
        """Determine if function is hot enough for JIT compilation"""
        call_count = self.profiler.function_profiles.get(function_name, 0)
        return call_count >= 100  # Threshold for JIT compilation
    
    def should_optimize(self, function_name: str) -> bool:
        """Determine if function is hot enough for aggressive optimization"""
        call_count = self.profiler.function_profiles.get(function_name, 0)
        return call_count >= 1000  # Threshold for optimization
    
    def get_compilation_tier(self, function_name: str) -> int:
        """Get appropriate compilation tier based on profiling"""
        if self.should_optimize(function_name):
            return 2  # Optimizing JIT
        elif self.should_compile_to_jit(function_name):
            return 1  # Baseline JIT
        else:
            return 0  # Interpreter
    
    def compile_with_tier(self, ir_instructions: List[IRInstr], function_name: str) -> List[IRInstr]:
        """Compile with appropriate optimization level based on profiling"""
        tier = self.get_compilation_tier(function_name)
        
        if tier == 0:
            # Interpreter - minimal optimizations
            return ir_instructions
        elif tier == 1:
            # Baseline JIT - basic optimizations
            from ir_optimizer import optimize
            return optimize(ir_instructions, [])
        else:
            # Optimizing JIT - full optimizations + profile-guided
            from ir_optimizer import optimize
            from ir_optimizer_advanced import advanced_optimize
            
            optimized = optimize(ir_instructions, [])
            optimized = advanced_optimize(optimized, [])
            optimized = self.feedback_optimizer.optimize_with_feedback(optimized)
            return optimized