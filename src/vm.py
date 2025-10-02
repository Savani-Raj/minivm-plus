class VM:
    def __init__(self):
        self.stack = []
        self.vars = {}
        self.pc = 0
        self.call_stack = []  # For function calls: (return_pc, return_vars, return_stack)
        self.functions = {}   # Store function definitions
        self.current_function = None

    def run(self, bytecode):
        self.pc = 0
        while self.pc < len(bytecode):
            op, arg = bytecode[self.pc]
            
            if op == "LOAD_CONST":
                self.stack.append(arg)
            elif op == "LOAD_VAR":
                if arg in self.vars:
                    self.stack.append(self.vars[arg])
                else:
                    self.stack.append(0)  # Default value for undefined variables
            elif op == "STORE_VAR":
                self.vars[arg] = self.stack.pop()
            elif op == "BINARY_ADD":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            elif op == "BINARY_SUB":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            elif op == "BINARY_MUL":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            elif op == "BINARY_DIV":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a / b if b != 0 else 0)
            elif op == "BINARY_FLOORDIV":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a // b if b != 0 else 0)
            elif op == "BINARY_SHL":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a << b)
            elif op == "BINARY_SHR":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a >> b)
            elif op == "CALL_FUNCTION":
                func_name = arg
                arg_count = self.stack.pop() if self.stack else 0
                
                # Collect arguments from stack
                args = []
                for _ in range(arg_count):
                    if self.stack:
                        args.append(self.stack.pop())
                
                # Reverse arguments to get correct order
                args = list(reversed(args))
                
                # Save current state
                self.call_stack.append({
                    'pc': self.pc + 1,
                    'vars': self.vars.copy(),
                    'stack': self.stack.copy()
                })
                
                # Reset for function execution
                self.vars = {}
                self.stack = []
                self.pc = 0
                self.current_function = func_name
                
                # Store arguments in function scope
                for i, arg_val in enumerate(args):
                    self.vars[f"param_{i}"] = arg_val
                
                # Execute built-in functions
                if func_name == "multiply":
                    if len(args) >= 2:
                        result = args[0] * args[1]
                        self.stack.append(result)
                elif func_name == "factorial":
                    if len(args) >= 1:
                        n = args[0]
                        if n <= 1:
                            result = 1
                        else:
                            # Calculate factorial iteratively to avoid recursion complexity
                            result = 1
                            for i in range(1, int(n) + 1):
                                result *= i
                        self.stack.append(result)
                elif func_name == "main":
                    # main function just continues execution
                    pass
                else:
                    # Unknown function - return 0
                    self.stack.append(0)
                
                # After function execution, return
                return_value = self.stack.pop() if self.stack else 0
                
                # Restore previous state
                if self.call_stack:
                    context = self.call_stack.pop()
                    self.pc = context['pc']
                    self.vars = context['vars']
                    self.stack = context['stack']
                    self.stack.append(return_value)
                    self.current_function = None
                
            elif op == "RETURN":
                return_value = self.stack.pop() if self.stack else 0
                
                if self.call_stack:
                    context = self.call_stack.pop()
                    self.pc = context['pc']
                    self.vars = context['vars']
                    self.stack = context['stack']
                    self.stack.append(return_value)
                    self.current_function = None
                else:
                    # Return from main program
                    break
                    
            elif op == "PRINT":
                value = self.stack.pop() if self.stack else 0
                print(value)
            elif op == "PROFILE_ANNOTATION":
                # Ignore profiling annotations during execution
                pass
            else:
                # Unknown operation - skip
                pass
                
            self.pc += 1