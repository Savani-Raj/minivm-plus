class VM:
    def __init__(self):
        self.stack = []
        self.vars = {}
        self.pc = 0

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
                self.stack.append(a / b)
            elif op == "PRINT":
                print(self.stack.pop())
            self.pc += 1
