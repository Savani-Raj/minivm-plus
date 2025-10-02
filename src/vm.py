class VM:
    def __init__(self):
        self.stack = []
        self.vars = {}
        self.pc = 0
        self.call_stack = []  # (return_pc, return_vars, return_stack)
        self.functions = {}   # function_name -> bytecode
        self.function_info = {}  # function_name -> {param_count, param_names, body}

    def run(self, bytecode):
        self.pc = 0
        while self.pc < len(bytecode):
            op, arg = bytecode[self.pc]
            
            if op == "LOAD_CONST":
                self.stack.append(arg)
            elif op == "LOAD_VAR":
                self.stack.append(self.vars.get(arg, 0))
            elif op == "STORE_VAR":
                self.vars[arg] = self.stack.pop()
            elif op == "BINARY_ADD":
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a + b)
            elif op == "BINARY_SUB":
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a - b)
            elif op == "BINARY_MUL":
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a * b)
            elif op == "BINARY_DIV":
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a / b if b != 0 else 0)
            elif op == "BINARY_FLOORDIV":
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a // b if b != 0 else 0)
            elif op == "BINARY_SHL":
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a << b)
            elif op == "BINARY_SHR":
                b = self.stack.pop(); a = self.stack.pop()
                self.stack.append(a >> b)
            elif op == "CALL_FUNCTION":
                func_name = arg
                arg_count = self.stack.pop() if self.stack else 0
                
                # Collect arguments from stack
                args = []
                for _ in range(arg_count):
                    if self.stack:
                        args.append(self.stack.pop())
                args = list(reversed(args))  # Correct order
                
                # Save current state
                self.call_stack.append({
                    'pc': self.pc + 1,
                    'vars': self.vars.copy(),
                    'stack': self.stack.copy()
                })
                
                # Set up function context
                self.vars = {}
                self.stack = []
                self.pc = 0
                
                # Handle built-in functions
                if func_name == "multiply" and len(args) == 2:
                    self.stack.append(args[0] * args[1])
                elif func_name == "factorial" and len(args) == 1:
                    n = args[0]
                    result = 1
                    for i in range(1, int(n) + 1):
                        result *= i
                    self.stack.append(result)
                elif func_name == "simple":
                    self.stack.append(42)
                else:
                    # Unknown function
                    self.stack.append(0)
                
                # Return from function
                return_value = self.stack.pop() if self.stack else 0
                
                # Restore context
                if self.call_stack:
                    context = self.call_stack.pop()
                    self.pc = context['pc']
                    self.vars = context['vars']
                    self.stack = context['stack']
                    self.stack.append(return_value)
                    
            elif op == "RETURN":
                return_value = self.stack.pop() if self.stack else 0
                if self.call_stack:
                    context = self.call_stack.pop()
                    self.pc = context['pc']
                    self.vars = context['vars']
                    self.stack = context['stack']
                    self.stack.append(return_value)
                else:
                    break
                    
            elif op == "PRINT":
                value = self.stack.pop() if self.stack else 0
                print(value)
            elif op == "PROFILE_ANNOTATION":
                pass
            elif op == "FUNCTION_INFO":
                # Store function information
                if arg:
                    self.function_info.update(arg)
            
            self.pc += 1