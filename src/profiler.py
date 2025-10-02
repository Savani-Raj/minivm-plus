from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from ir_optimizer import IRInstr

@dataclass
class TypeProfile:
    """Track type information for variables"""
    observed_types: Set[type]
    count: int = 0
    
    def add_observation(self, value):
        """Record a type observation"""
        self.observed_types.add(type(value))
        self.count += 1
    
    def is_monomorphic(self):
        """Check if variable has only one observed type"""
        return len(self.observed_types) == 1
    
    def get_primary_type(self):
        """Get the most common type"""
        return next(iter(self.observed_types)) if self.observed_types else None

@dataclass
class BranchProfile:
    """Track branch behavior"""
    taken_count: int = 0
    not_taken_count: int = 0
    
    def record_branch(self, taken: bool):
        """Record branch outcome"""
        if taken:
            self.taken_count += 1
        else:
            self.not_taken_count += 1
    
    def get_taken_ratio(self):
        """Get branch taken ratio"""
        total = self.taken_count + self.not_taken_count
        return self.taken_count / total if total > 0 else 0.5

@dataclass
class BasicBlockProfile:
    """Profile information for a basic block"""
    execution_count: int = 0
    instruction_count: int = 0
    
    def record_execution(self):
        """Record block execution"""
        self.execution_count += 1
    
    def is_hot(self, threshold=1000):
        """Check if block is hot based on execution count"""
        return self.execution_count >= threshold

class RuntimeProfiler:
    """
    Profiler for managed runtime optimization
    Collects runtime feedback for JIT compilation decisions
    """
    
    def __init__(self):
        self.type_profiles: Dict[str, TypeProfile] = {}
        self.branch_profiles: Dict[str, BranchProfile] = {}
        self.block_profiles: Dict[str, BasicBlockProfile] = {}
        self.function_profiles: Dict[str, int] = {}
        self.hot_paths: Set[str] = set()
        
        # Optimization thresholds
        self.hot_block_threshold = 1000
        self.hot_function_threshold = 100
        self.type_stable_threshold = 100
    
    def profile_variable_type(self, var_name: str, value: Any):
        """Profile type information for a variable"""
        if var_name not in self.type_profiles:
            self.type_profiles[var_name] = TypeProfile(set())
        
        self.type_profiles[var_name].add_observation(value)
    
    def profile_branch(self, branch_id: str, taken: bool):
        """Profile branch prediction information"""
        if branch_id not in self.branch_profiles:
            self.branch_profiles[branch_id] = BranchProfile()
        
        self.branch_profiles[branch_id].record_branch(taken)
    
    def profile_block_execution(self, block_id: str):
        """Profile basic block execution frequency"""
        if block_id not in self.block_profiles:
            self.block_profiles[block_id] = BasicBlockProfile()
        
        self.block_profiles[block_id].record_execution()
        
        # Check if block becomes hot
        if self.block_profiles[block_id].is_hot(self.hot_block_threshold):
            self.hot_paths.add(block_id)
    
    def profile_function_call(self, function_name: str):
        """Profile function call frequency"""
        if function_name not in self.function_profiles:
            self.function_profiles[function_name] = 0
        
        self.function_profiles[function_name] += 1
    
    def get_type_stable_variables(self) -> List[str]:
        """Get list of variables with stable types"""
        stable_vars = []
        for var_name, profile in self.type_profiles.items():
            if profile.is_monomorphic() and profile.count >= self.type_stable_threshold:
                stable_vars.append(var_name)
        return stable_vars
    
    def get_hot_blocks(self) -> List[str]:
        """Get list of hot basic blocks"""
        return [block_id for block_id, profile in self.block_profiles.items() 
                if profile.is_hot(self.hot_block_threshold)]
    
    def get_hot_functions(self) -> List[str]:
        """Get list of hot functions"""
        return [func_name for func_name, count in self.function_profiles.items()
                if count >= self.hot_function_threshold]
    
    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """Generate optimization suggestions based on profiling data"""
        suggestions = {
            'type_specialization': self.get_type_stable_variables(),
            'hot_blocks': self.get_hot_blocks(),
            'hot_functions': self.get_hot_functions(),
            'branch_predictions': {},
            'inline_candidates': []
        }
        
        # Add branch prediction hints
        for branch_id, profile in self.branch_profiles.items():
            if profile.get_taken_ratio() > 0.8:
                suggestions['branch_predictions'][branch_id] = 'likely_taken'
            elif profile.get_taken_ratio() < 0.2:
                suggestions['branch_predictions'][branch_id] = 'likely_not_taken'
        
        # Add inline candidates (simple heuristic: small hot functions)
        hot_functions = self.get_hot_functions()
        # In real implementation, we'd check function size here
        suggestions['inline_candidates'] = hot_functions
        
        return suggestions
    
    def generate_profile_report(self) -> str:
        """Generate human-readable profile report"""
        report = []
        report.append("=== Runtime Profile Report ===")
        
        report.append("\n--- Type Profiles ---")
        for var_name, profile in self.type_profiles.items():
            types_str = ', '.join(t.__name__ for t in profile.observed_types)
            report.append(f"  {var_name}: {types_str} (count: {profile.count})")
        
        report.append("\n--- Hot Blocks ---")
        hot_blocks = self.get_hot_blocks()
        for block_id in hot_blocks:
            count = self.block_profiles[block_id].execution_count
            report.append(f"  {block_id}: {count} executions")
        
        report.append("\n--- Branch Profiles ---")
        for branch_id, profile in self.branch_profiles.items():
            ratio = profile.get_taken_ratio()
            report.append(f"  {branch_id}: {ratio:.1%} taken")
        
        report.append("\n--- Optimization Suggestions ---")
        suggestions = self.get_optimization_suggestions()
        report.append(f"  Type specialization: {suggestions['type_specialization']}")
        report.append(f"  Inline candidates: {suggestions['inline_candidates']}")
        
        return "\n".join(report)
    
    def reset(self):
        """Reset all profile data"""
        self.type_profiles.clear()
        self.branch_profiles.clear()
        self.block_profiles.clear()
        self.function_profiles.clear()
        self.hot_paths.clear()