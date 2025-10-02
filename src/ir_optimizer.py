from typing import List, Tuple, Dict

class IRInstr:
    def __init__(self, op: str, dest: str, a=None, b=None):
        self.op = op      # e.g., "add", "mul", "const", "mov", "print"
        self.dest = dest  # target variable
        self.a = a
        self.b = b

    def __repr__(self):
        if self.op == "const":
            return f"{self.dest} = {self.a}"
        elif self.op == "mov":
            return f"{self.dest} = {self.a}"
        elif self.op == "print":
            return f"print {self.a}"
        elif self.op == "call":
            return f"{self.dest} = call {self.a}({self.b} args)"
        elif self.op == "return":
            return f"return {self.a}"
        elif self.op == "func_start":
            return f"func {self.a} (params: {self.b})"
        elif self.op == "param":
            return f"param {self.a} = ${self.b}"
        elif self.op == "arg":
            return f"arg {self.a} = {self.b}"
        elif self.op == "function_info":
            return f"function_info: {len(self.a) if self.a else 0} functions"
        elif self.op == "push_arg":
            return f"push_arg {self.a} = {self.b}"
        else:
            # Handle None values in binary operations
            a_str = self.a if self.a is not None else "None"
            b_str = self.b if self.b is not None else "None"
            return f"{self.dest} = {a_str} {self.op} {b_str}"

def is_const(x):
    return isinstance(x, (int, float))

# ------------------- Optimization Passes ------------------- #

def const_fold(instrs: List['IRInstr']) -> List['IRInstr']:
    """Constant Folding"""
    out = []
    for ins in instrs:
        if ins.op in {"+", "-", "*", "/"} and is_const(ins.a) and is_const(ins.b):
            if ins.op == "+": val = ins.a + ins.b
            elif ins.op == "-": val = ins.a - ins.b
            elif ins.op == "*": val = ins.a * ins.b
            elif ins.op == "/": val = ins.a / ins.b if ins.b != 0 else 0
            out.append(IRInstr("const", ins.dest, a=val))
        else:
            out.append(ins)
    return out

def const_propagation(instrs: List['IRInstr']) -> List['IRInstr']:
    """Replace variables with their known constant values"""
    out = []
    consts: Dict[str, int] = {}
    
    for ins in instrs:
        if ins.op == "const":
            consts[ins.dest] = ins.a
            out.append(ins)
        elif ins.op == "mov" and ins.a in consts:
            # variable move of constant
            out.append(IRInstr("const", ins.dest, a=consts[ins.a]))
            consts[ins.dest] = consts[ins.a]
        else:
            # FIX: Handle None values properly
            a = consts.get(ins.a, ins.a) if ins.a is not None else None
            b = consts.get(ins.b, ins.b) if ins.b is not None else None
            out.append(IRInstr(ins.op, ins.dest, a, b))
            
            # Remove destination from constants if it's being overwritten
            if ins.dest in consts and ins.op not in {"print", "function_info"}:
                del consts[ins.dest]
    
    return out

def algebraic_simplify(instrs: List['IRInstr']) -> List['IRInstr']:
    """Algebraic simplification rules like x+0=x, x*1=x"""
    out = []
    for ins in instrs:
        if ins.op == "+":
            if ins.b == 0: 
                out.append(IRInstr("mov", ins.dest, a=ins.a))
                continue
            if ins.a == 0: 
                out.append(IRInstr("mov", ins.dest, a=ins.b))
                continue
        elif ins.op == "*":
            if ins.b == 1: 
                out.append(IRInstr("mov", ins.dest, a=ins.a))
                continue
            if ins.a == 1: 
                out.append(IRInstr("mov", ins.dest, a=ins.b))
                continue
            if ins.a == 0 or ins.b == 0: 
                out.append(IRInstr("const", ins.dest, a=0))
                continue
        out.append(ins)
    return out

def cse(instrs: List['IRInstr']) -> List['IRInstr']:
    """Common Subexpression Elimination"""
    expr_map = {}
    out = []
    
    for ins in instrs:
        if ins.op in {"+", "-", "*", "/"}:
            key = (ins.op, ins.a, ins.b)
            if key in expr_map:
                # Replace with move from existing computation
                out.append(IRInstr("mov", ins.dest, a=expr_map[key]))
            else:
                expr_map[key] = ins.dest
                out.append(ins)
        else:
            out.append(ins)
    
    return out

def dead_code_elim(instrs: List['IRInstr'], used_vars: List[str]) -> List['IRInstr']:
    """Eliminate instructions whose results are never used"""
    if not used_vars:
        return instrs
    
    # Build dependency graph
    deps = {}
    for ins in instrs:
        if ins.dest:
            deps[ins.dest] = ins
    
    # Find all variables that are ultimately used
    needed = set(used_vars)
    worklist = list(used_vars)
    
    while worklist:
        var = worklist.pop()
        if var in deps:
            ins = deps[var]
            if isinstance(ins.a, str) and ins.a not in needed:
                needed.add(ins.a)
                worklist.append(ins.a)
            if isinstance(ins.b, str) and ins.b not in needed:
                needed.add(ins.b)
                worklist.append(ins.b)
    
    # Keep only needed instructions and prints
    out = []
    for ins in instrs:
        if ins.op == "print" or (ins.dest and ins.dest in needed):
            out.append(ins)
    
    return out

# ------------------- Pipeline ------------------- #

def optimize(instrs: List['IRInstr'], used_vars: List[str] = []) -> List['IRInstr']:
    passes = [const_fold, const_propagation, algebraic_simplify, cse]
    out = instrs
    for p in passes:
        out = p(out)
    out = dead_code_elim(out, used_vars)
    return out