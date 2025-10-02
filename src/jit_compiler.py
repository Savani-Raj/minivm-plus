import ctypes
import mmap
import sys
from ir_optimizer import is_const

class SimpleJIT:
    def __init__(self):
        self.memory = None
        self.code_size = 0
        self.offset = 0
        
    def allocate_executable_memory(self, size=4096):
        """Allocate executable memory for JIT code"""
        self.memory = mmap.mmap(-1, size, prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
        self.code_size = size
        self.offset = 0
        return self.memory
    
    def emit_byte(self, byte):
        """Emit a single byte to JIT memory"""
        if self.offset >= self.code_size:
            raise RuntimeError("JIT memory full")
        self.memory[self.offset] = byte
        self.offset += 1
    
    def emit_bytes(self, bytes_list):
        """Emit multiple bytes"""
        for byte in bytes_list:
            self.emit_byte(byte)
    
    def compile_arithmetic(self, op: str, dest: str, a, b):
        """Compile simple arithmetic to x86-64 assembly"""
        # This is a simplified example - real JIT would be much more complex
        if sys.platform == "linux" or sys.platform == "linux2":
            # Linux x86-64 system call convention
            if op == "+":
                # mov rax, [a]; add rax, [b]; mov [dest], rax
                pass
            elif op == "*":
                # mov rax, [a]; imul rax, [b]; mov [dest], rax
                pass
        
        # For demonstration, we'll just return a Python function
        if op == "+":
            return lambda: a + b
        elif op == "*":
            return lambda: a * b
        elif op == "-":
            return lambda: a - b
        elif op == "/":
            return lambda: a / b if b != 0 else 0
        elif op == "<<":
            return lambda: a << b
        elif op == ">>":
            return lambda: a >> b
    
    def compile_const(self, value):
        """Compile constant loading"""
        return lambda: value
    
    def finalize(self):
        """Finalize JIT compilation"""
        if self.memory:
            # Convert to callable function
            func_type = ctypes.CFUNCTYPE(ctypes.c_int)
            return func_type(ctypes.addressof(ctypes.c_void_p.from_buffer(self.memory)))
        return None

class JITRuntime:
    """Simple managed runtime with JIT concepts"""
    
    def __init__(self):
        self.jit = SimpleJIT()
        self.heap = {}
        self.constant_pool = {}
        
    def jit_compile_expression(self, ir_instructions):
        """JIT compile a sequence of IR instructions"""
        compiled_functions = []
        computed_values = {}  # Track computed values by variable name
        
        for ins in ir_instructions:
            if ins.op == "const":
                func = self.jit.compile_const(ins.a)
                compiled_functions.append((ins.dest, func))
                computed_values[ins.dest] = func()
            elif ins.op in {"+", "-", "*", "/", "<<", ">>"}:
                # Look up values from previous computations
                a_val = self._resolve_operand(ins.a, computed_values)
                b_val = self._resolve_operand(ins.b, computed_values)
                func = self.jit.compile_arithmetic(ins.op, ins.dest, a_val, b_val)
                compiled_functions.append((ins.dest, func))
                computed_values[ins.dest] = func()
            elif ins.op == "print":
                # For print, we compile a function that returns the value to print
                val = self._resolve_operand(ins.a, computed_values)
                func = self.jit.compile_const(val)
                compiled_functions.append(("print_result", func))
        
        return compiled_functions
    
    def _resolve_operand(self, operand, computed_values):
        """Resolve operand to actual value"""
        if is_const(operand):
            return operand
        elif operand in computed_values:
            return computed_values[operand]
        else:
            return 0  # Default value
    
    def execute_jit(self, compiled_functions):
        """Execute JIT-compiled functions"""
        results = {}
        for var, func in compiled_functions:
            results[var] = func()
        return results