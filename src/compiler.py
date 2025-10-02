import re

def tokenize(code: str):
    # split words, numbers, operators, and symbols
    tokens = re.findall(r"[A-Za-z_]\w*|\d+|[=;+*/()-]", code)
    return tokens

def parse(tokens):
    # very naive parser: handles "let x = expr ;" and "print ( expr ) ;"
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
            if tokens[i] == ";": i += 1
        elif tokens[i] == "print":
            if tokens[i+1] != "(":
                raise SyntaxError("Expected ( after print")
            expr, j = parse_expr(tokens, i+2)
            if tokens[j] != ")":
                raise SyntaxError("Expected ) after print expr")
            ast.append(("print", expr))
            i = j+1
            if tokens[i] == ";": i += 1
        else:
            raise SyntaxError(f"Unexpected token: {tokens[i]}")
    return ast

def parse_expr(tokens, i):
    # parse simple binary expr: NUMBER | VAR ( + NUMBER | VAR )*
    left = tokens[i]
    if left.isdigit():
        node = ("num", int(left))
    else:
        node = ("var", left)
    i += 1

    while i < len(tokens) and tokens[i] in {"+", "-", "*", "/"}:
        op = tokens[i]
        right_tok = tokens[i+1]
        if right_tok.isdigit():
            right = ("num", int(right_tok))
        else:
            right = ("var", right_tok)
        node = ("binop", op, node, right)
        i += 2
    return node, i

def compile_expr(node, bytecode):
    if node[0] == "num":
        bytecode.append(("LOAD_CONST", node[1]))
    elif node[0] == "var":
        bytecode.append(("LOAD_VAR", node[1]))
    elif node[0] == "binop":
        _, op, left, right = node
        compile_expr(left, bytecode)
        compile_expr(right, bytecode)
        if op == "+": bytecode.append(("BINARY_ADD", None))
        elif op == "-": bytecode.append(("BINARY_SUB", None))
        elif op == "*": bytecode.append(("BINARY_MUL", None))
        elif op == "/": bytecode.append(("BINARY_DIV", None))

def compile_program(code: str):
    tokens = tokenize(code)
    ast = parse(tokens)
    bytecode = []
    for stmt in ast:
        if stmt[0] == "assign":
            _, var, expr = stmt
            compile_expr(expr, bytecode)
            bytecode.append(("STORE_VAR", var))
        elif stmt[0] == "print":
            _, expr = stmt
            compile_expr(expr, bytecode)
            bytecode.append(("PRINT", None))
    return bytecode

def compile_file(path: str):
    with open(path) as f:
        code = f.read()
    return compile_program(code)
