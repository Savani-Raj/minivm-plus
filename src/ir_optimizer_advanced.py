from typing import List, Dict, Set, Tuple
from ir_optimizer import IRInstr, is_const

class BasicBlock:
    def __init__(self, name: str):
        self.name = name
        self.instructions: List[IRInstr] = []
        self.predecessors: List['BasicBlock'] = []
        self.successors: List['BasicBlock'] = []
    
    def __repr__(self):
        return f"Block {self.name}"

def build_cfg(instructions: List[IRInstr]) -> List[BasicBlock]:
    """Build Control Flow Graph from linear IR"""
    blocks = []
    current_block = BasicBlock("entry")
    blocks.append(current_block)
    
    for ins in instructions:
        current_block.instructions.append(ins)
    
    return blocks

def copy_propagation(blocks: List[BasicBlock]) -> List[BasicBlock]:
    """Replace copies with original variables"""
    copies = {}
    
    for block in blocks:
        new_instructions = []
        for ins in block.instructions:
            # Substitute copies in operands first
            new_a = copies.get(ins.a, ins.a)
            new_b = copies.get(ins.b, ins.b)
            
            if ins.op == "mov" and isinstance(new_a, str):
                # Track this copy
                copies[ins.dest] = new_a
                # Don't add the mov instruction to output
                continue
            elif ins.op in {"+", "-", "*", "/", "<<", ">>"}:
                new_ins = IRInstr(ins.op, ins.dest, new_a, new_b)
                new_instructions.append(new_ins)
            elif ins.op == "const":
                new_instructions.append(IRInstr("const", ins.dest, a=new_a))
                copies[ins.dest] = new_a  # Track constants
            elif ins.op == "print":
                new_instructions.append(IRInstr("print", None, a=new_a))
            else:
                new_instructions.append(ins)
        
        block.instructions = new_instructions
    
    return blocks

def strength_reduction(blocks: List[BasicBlock]) -> List[BasicBlock]:
    """Replace expensive operations with cheaper ones"""
    for block in blocks:
        new_instructions = []
        for ins in block.instructions:
            if ins.op == "*" and is_const(ins.b):
                if ins.b == 2:
                    # x * 2 → x + x
                    new_ins = IRInstr("+", ins.dest, a=ins.a, b=ins.a)
                    new_instructions.append(new_ins)
                    continue
                elif ins.b == 4:
                    # x * 4 → x << 2
                    new_ins = IRInstr("<<", ins.dest, a=ins.a, b=2)
                    new_instructions.append(new_ins)
                    continue
            elif ins.op == "/" and is_const(ins.b) and ins.b == 2:
                # x / 2 → x >> 1
                new_ins = IRInstr(">>", ins.dest, a=ins.a, b=1)
                new_instructions.append(new_ins)
                continue
            
            new_instructions.append(ins)
        
        block.instructions = new_instructions
    
    return blocks

def constant_propagation_advanced(blocks: List[BasicBlock]) -> List[BasicBlock]:
    """Advanced constant propagation"""
    constants = {}
    
    for block in blocks:
        new_instructions = []
        for ins in block.instructions:
            # Substitute constants in operands
            new_a = constants.get(ins.a, ins.a)
            new_b = constants.get(ins.b, ins.b)
            
            if ins.op == "const":
                constants[ins.dest] = new_a
                new_instructions.append(IRInstr("const", ins.dest, a=new_a))
            elif ins.op in {"+", "-", "*", "/", "<<", ">>"} and is_const(new_a) and is_const(new_b):
                # Compute constant expression
                if ins.op == "+": result = new_a + new_b
                elif ins.op == "-": result = new_a - new_b
                elif ins.op == "*": result = new_a * new_b
                elif ins.op == "/": result = new_a / new_b if new_b != 0 else 0
                elif ins.op == "<<": result = new_a << new_b
                elif ins.op == ">>": result = new_a >> new_b
                
                constants[ins.dest] = result
                new_instructions.append(IRInstr("const", ins.dest, a=result))
            elif ins.op == "mov" and new_a in constants:
                constants[ins.dest] = constants[new_a]
                new_instructions.append(IRInstr("const", ins.dest, a=constants[new_a]))
            elif ins.op in {"+", "-", "*", "/", "<<", ">>"}:
                new_ins = IRInstr(ins.op, ins.dest, new_a, new_b)
                new_instructions.append(new_ins)
            elif ins.op == "print":
                new_instructions.append(IRInstr("print", None, a=new_a))
            else:
                new_instructions.append(ins)
        
        block.instructions = new_instructions
    
    return blocks

def dead_code_elimination_advanced(blocks: List[BasicBlock], used_vars: List[str]) -> List[BasicBlock]:
    """Advanced dead code elimination that preserves dependencies"""
    if not used_vars:
        return blocks
    
    # Build dependency graph
    dependencies = {}
    for block in blocks:
        for ins in block.instructions:
            if ins.dest:
                deps = []
                if isinstance(ins.a, str):
                    deps.append(ins.a)
                if isinstance(ins.b, str):
                    deps.append(ins.b)
                dependencies[ins.dest] = deps
    
    # Find all variables that are needed
    needed = set(used_vars)
    worklist = list(used_vars)
    
    while worklist:
        var = worklist.pop()
        if var in dependencies:
            for dep in dependencies[var]:
                if dep not in needed:
                    needed.add(dep)
                    worklist.append(dep)
    
    # Filter instructions
    for block in blocks:
        block.instructions = [
            ins for ins in block.instructions
            if ins.op == "print" or (ins.dest and ins.dest in needed) or not ins.dest
        ]
    
    return blocks

def blocks_to_linear(blocks: List[BasicBlock]) -> List[IRInstr]:
    """Convert basic blocks back to linear IR"""
    instructions = []
    for block in blocks:
        instructions.extend(block.instructions)
    return instructions

def advanced_optimize(ir: List[IRInstr], used_vars: List[str] = []) -> List[IRInstr]:
    """Advanced optimization pipeline with CFG - FINAL FIXED VERSION"""
    from ir_optimizer import optimize
    
    # First do basic optimizations
    ir = optimize(ir, used_vars)
    
    print("\n=== After Basic Optimizations ===")
    for i in ir: print(i)
    
    # Build CFG and do advanced optimizations
    blocks = build_cfg(ir)
    blocks = strength_reduction(blocks)
    blocks = constant_propagation_advanced(blocks)
    blocks = copy_propagation(blocks)
    blocks = dead_code_elimination_advanced(blocks, used_vars)  # Use advanced DCE
    
    # Convert back to linear IR
    result = blocks_to_linear(blocks)
    
    print("\n=== After Advanced Optimizations ===")
    for i in result: print(i)
    
    return result