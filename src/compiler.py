import re

from ir_optimizer import IRInstr

# ------------------- Tokenizer ------------------- #

def tokenize(code: str):
    # Improved tokenizer to handle identifiers, numbers, and operators
    tokens = re.findall(r"[A-Za-z_]\w*|\d+|[=;+*/(),-]", code)
    return [t for t in tokens if t.strip()]

# ------------------- Parser ------------------- #

def parse(tokens):
    ast = []
    i = 0
    while i < len(tokens):
        if tokens[i] == "let":
            var = tokens[i+1]
            if tokens[i+2] != "=":
                raise SyntaxError("Expected = after variable name")
            expr, j = parse_expr(tokens, i+3)
            ast.append(("assign", var, expr))
            i = j
            if i < len(tokens) and tokens[i] == ";": 
                i += 1
        elif tokens[i] == "print":
            if i+1 >= len(tokens) or tokens[i+1] != "(":
                raise SyntaxError("Expected ( after print")
            expr, j = parse_expr(tokens, i+2)
            if j >= len(tokens) or tokens[j] != ")":
                raise SyntaxError("Expected ) after print expr")
            ast.append(("print", expr))
            i = j + 1
            if i < len(tokens) and tokens[i] == ";": 
                i += 1
        else:
            i += 1  # Skip unknown tokens
    return ast

def parse_expr(tokens, i):
    """Parse expressions with operator precedence"""
    return parse_add_sub(tokens, i)

def parse_add_sub(tokens, i):
    left, i = parse_mul_div(tokens, i)
    
    while i < len(tokens) and tokens[i] in ['+', '-']:
        op = tokens[i]
        right, i = parse_mul_div(tokens, i+1)
        left = ('binop', op, left, right)
    
    return left, i

def parse_mul_div(tokens, i):
    left, i = parse_primary(tokens, i)
    
    while i < len(tokens) and tokens[i] in ['*', '/']:
        op = tokens[i]
        right, i = parse_primary(tokens, i+1)
        left = ('binop', op, left, right)
    
    return left, i

def parse_primary(tokens, i):
    if i >= len(tokens):
        raise SyntaxError("Unexpected end of input")
    
    token = tokens[i]
    if token.isdigit():
        return ('num', int(token)), i+1
    elif token.isidentifier():
        return ('var', token), i+1
    elif token == '(':
        expr, i = parse_expr(tokens, i+1)
        if i >= len(tokens) or tokens[i] != ')':
            raise SyntaxError("Expected )")
        return expr, i+1
    else:
        raise SyntaxError(f"Unexpected token in expression: {token}")

# ------------------- AST → IR ------------------- #

def compile_expr_to_ir(node, ir, new_temp):
    if node[0] == "num":
        # Directly return the number, no temporary needed
        return node[1]
    elif node[0] == "var":
        # Return the variable name
        return node[1]
    elif node[0] == "binop":
        _, op, left, right = node
        l = compile_expr_to_ir(left, ir, new_temp)
        r = compile_expr_to_ir(right, ir, new_temp)
        tmp = new_temp()
        ir.append(IRInstr(op, tmp, a=l, b=r))
        return tmp

def compile_program(code: str):
    tokens = tokenize(code)
    ast = parse(tokens)
    ir = []
    temp_id = 0

    def new_temp():
        nonlocal temp_id
        temp_id += 1
        return f"t{temp_id}"

    for stmt in ast:
        if stmt[0] == "assign":
            _, var, expr = stmt
            dest = compile_expr_to_ir(expr, ir, new_temp)
            # Only create mov instruction if dest is not already the variable
            if dest != var:
                ir.append(IRInstr("mov", var, a=dest))
        elif stmt[0] == "print":
            _, expr = stmt
            dest = compile_expr_to_ir(expr, ir, new_temp)
            ir.append(IRInstr("print", None, a=dest))
    
    return ir

def compile_file(path: str):
    with open(path) as f:
        code = f.read()
    # strip comments starting with //
    lines = []
    for line in code.splitlines():
        if '//' in line:
            line = line.split('//')[0]
        lines.append(line)
    code = "\n".join(lines)
    return compile_program(code)