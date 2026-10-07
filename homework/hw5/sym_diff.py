"""
sym_diff.py
遞迴下降解析器、遞迴符號微分、化簡器、求值及數值驗證（中央差分）
"""

import math
import re

# ----------------- 1. 遞迴下降解析器 (Recursive Descent Parser) -----------------

def tokenize(s):
    token_spec = [
        ('NUM', r'\d+(\.\d+)?'),
        ('FUNC', r'\b(sin|cos|tan|exp|ln|sqrt)\b'),
        ('VAR', r'\b[a-zA-Z]\b'),
        ('POW', r'\*\*|\^'),
        ('OP', r'[+\-*/()]'),
        ('SKIP', r'\s+'),
    ]
    regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
    tokens = []
    for match in re.finditer(regex, s):
        kind = match.lastgroup
        val = match.group()
        if kind == 'NUM':
            tokens.append(('NUM', float(val) if '.' in val else int(val)))
        elif kind in ('FUNC', 'VAR', 'OP'):
            tokens.append((kind, val))
        elif kind == 'POW':
            tokens.append(('OP', '^'))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def consume(self, expected_val=None):
        tok = self.peek()
        if expected_val and tok[1] != expected_val:
            raise SyntaxError(f"Expected {expected_val}, got {tok[1]}")
        self.pos += 1
        return tok

    def parse(self):
        res = self.expr()
        if self.pos < len(self.tokens):
            raise SyntaxError(f"Unexpected token: {self.peek()[1]}")
        return res

    def expr(self):
        node = self.term()
        while self.peek()[1] in ('+', '-'):
            op = self.consume()[1]
            right = self.term()
            node = ('add' if op == '+' else 'sub', node, right)
        return node

    def term(self):
        node = self.power()
        while self.peek()[1] in ('*', '/'):
            op = self.consume()[1]
            right = self.power()
            node = ('mul' if op == '*' else 'div', node, right)
        return node

    def power(self):
        node = self.unary()
        if self.peek()[1] == '^':
            self.consume('^')
            right = self.power()  # 右結合性
            node = ('pow', node, right)
        return node

    def unary(self):
        if self.peek()[1] == '-':
            self.consume('-')
            return ('neg', self.unary())
        return self.primary()

    def primary(self):
        tok_type, val = self.peek()
        if tok_type == 'NUM':
            self.consume()
            return ('num', val)
        elif tok_type == 'VAR':
            self.consume()
            return ('var', val)
        elif tok_type == 'FUNC':
            self.consume()
            self.consume('(')
            arg = self.expr()
            self.consume(')')
            return (val, arg)
        elif val == '(':
            self.consume('(')
            node = self.expr()
            self.consume(')')
            return node
        raise SyntaxError(f"Unexpected token at primary: {val}")


def parse(s):
    return Parser(tokenize(s)).parse()


# ----------------- 2. 遞迴符號微分核心 -----------------

def sym_diff(expr, var='x'):
    if isinstance(expr, str):
        expr = parse(expr)

    tag = expr[0]
    if tag == 'num':
        return ('num', 0)
    if tag == 'var':
        return ('num', 1 if expr[1] == var else 0)
    if tag == 'neg':
        return ('neg', sym_diff(expr[1], var))
    if tag == 'add':
        return ('add', sym_diff(expr[1], var), sym_diff(expr[2], var))
    if tag == 'sub':
        return ('sub', sym_diff(expr[1], var), sym_diff(expr[2], var))
    if tag == 'mul':
        f, g = expr[1], expr[2]
        # (f*g)' = f'*g + f*g'
        return ('add', ('mul', sym_diff(f, var), g), ('mul', f, sym_diff(g, var)))
    if tag == 'div':
        f, g = expr[1], expr[2]
        # (f/g)' = (f'*g - f*g') / (g^2)
        numerator = ('sub', ('mul', sym_diff(f, var), g), ('mul', f, sym_diff(g, var)))
        denominator = ('pow', g, ('num', 2))
        return ('div', numerator, denominator)
    if tag == 'pow':
        base, exp = expr[1], expr[2]
        if exp[0] == 'num':
            n = exp[1]
            # (f^n)' = n * f^(n-1) * f'
            inner = ('pow', base, ('num', n - 1))
            return ('mul', ('mul', ('num', n), inner), sym_diff(base, var))
        else:
            # 一般化冪次法則 (f^g)' = f^g * (g' * ln(f) + g * f' / f)
            term1 = ('mul', sym_diff(exp, var), ('ln', base))
            term2 = ('div', ('mul', exp, sym_diff(base, var)), base)
            return ('mul', expr, ('add', term1, term2))
    if tag == 'sin':
        return ('mul', ('cos', expr[1]), sym_diff(expr[1], var))
    if tag == 'cos':
        return ('mul', ('neg', ('sin', expr[1])), sym_diff(expr[1], var))
    if tag == 'tan':
        # (tan f)' = f' / cos(f)^2
        return ('div', sym_diff(expr[1], var), ('pow', ('cos', expr[1]), ('num', 2)))
    if tag == 'exp':
        return ('mul', ('exp', expr[1]), sym_diff(expr[1], var))
    if tag == 'ln':
        return ('div', sym_diff(expr[1], var), expr[1])
    if tag == 'sqrt':
        # (sqrt f)' = f' / (2 * sqrt f)
        return ('div', sym_diff(expr[1], var), ('mul', ('num', 2), ('sqrt', expr[1])))
    raise NotImplementedError(f"Unsupported node: {tag}")


# ----------------- 3. 語法樹化簡與求值 -----------------

def simplify(node):
    tag = node[0]
    if tag in ('num', 'var'):
        return node
    if tag == 'neg':
        sub = simplify(node[1])
        if sub[0] == 'num':
            return ('num', -sub[1])
        return ('neg', sub)
    if tag in ('add', 'sub', 'mul', 'div', 'pow'):
        a = simplify(node[1])
        b = simplify(node[2])
        if a[0] == 'num' and b[0] == 'num':
            va, vb = a[1], b[1]
            if tag == 'add': return ('num', va + vb)
            if tag == 'sub': return ('num', va - vb)
            if tag == 'mul': return ('num', va * vb)
            if tag == 'div' and vb != 0: return ('num', va / vb)
            if tag == 'pow': return ('num', va ** vb)

        if tag == 'add':
            if a == ('num', 0): return b
            if b == ('num', 0): return a
        elif tag == 'sub':
            if b == ('num', 0): return a
            if a == ('num', 0): return ('neg', b)
        elif tag == 'mul':
            if a == ('num', 0) or b == ('num', 0): return ('num', 0)
            if a == ('num', 1): return b
            if b == ('num', 1): return a
        elif tag == 'div':
            if a == ('num', 0): return ('num', 0)
            if b == ('num', 1): return a
        elif tag == 'pow':
            if b == ('num', 0): return ('num', 1)
            if b == ('num', 1): return a
            if a == ('num', 0): return ('num', 0)
            if a == ('num', 1): return ('num', 1)

        return (tag, a, b)

    if tag in ('sin', 'cos', 'tan', 'exp', 'ln', 'sqrt'):
        sub = simplify(node[1])
        return (tag, sub)
    return node


def to_str(node, parent_precedence=0):
    precedences = {'add': 1, 'sub': 1, 'mul': 2, 'div': 2, 'neg': 3, 'pow': 4}
    tag = node[0]
    if tag == 'num':
        val = node[1]
        return str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
    if tag == 'var':
        return node[1]
    if tag == 'neg':
        res = f"-{to_str(node[1], precedences['neg'])}"
        return f"({res})" if parent_precedence > precedences['neg'] else res
    if tag in ('add', 'sub', 'mul', 'div', 'pow'):
        op_map = {'add': ' + ', 'sub': ' - ', 'mul': ' * ', 'div': ' / ', 'pow': ' ^ '}
        my_prec = precedences[tag]
        left_str = to_str(node[1], my_prec)
        right_str = to_str(node[2], my_prec + (1 if tag in ('sub', 'div') else 0))
        res = f"{left_str}{op_map[tag]}{right_str}"
        return f"({res})" if parent_precedence > my_prec else res
    if tag in ('sin', 'cos', 'tan', 'exp', 'ln', 'sqrt'):
        return f"{tag}({to_str(node[1], 0)})"
    return str(node)


def evaluate(node, val, var='x'):
    tag = node[0]
    if tag == 'num': return node[1]
    if tag == 'var': return val if node[1] == var else 0.0
    if tag == 'neg': return -evaluate(node[1], val, var)
    if tag == 'add': return evaluate(node[1], val, var) + evaluate(node[2], val, var)
    if tag == 'sub': return evaluate(node[1], val, var) - evaluate(node[2], val, var)
    if tag == 'mul': return evaluate(node[1], val, var) * evaluate(node[2], val, var)
    if tag == 'div': return evaluate(node[1], val, var) / evaluate(node[2], val, var)
    if tag == 'pow': return evaluate(node[1], val, var) ** evaluate(node[2], val, var)
    if tag == 'sin': return math.sin(evaluate(node[1], val, var))
    if tag == 'cos': return math.cos(evaluate(node[1], val, var))
    if tag == 'tan': return math.tan(evaluate(node[1], val, var))
    if tag == 'exp': return math.exp(evaluate(node[1], val, var))
    if tag == 'ln':  return math.log(evaluate(node[1], val, var))
    if tag == 'sqrt': return math.sqrt(evaluate(node[1], val, var))
    raise ValueError(f"Unknown tag: {tag}")


# ----------------- 4. 執行與數值比對驗證 -----------------

if __name__ == '__main__':
    test_cases = [
        "3 * x ^ 2 + 2 * x - 5",
        "x ^ 2 * sin(x)",
        "sin(x ^ 2)",
        "exp(x) / (1 + x ^ 2)",
        "tan(x)",
        "x ^ x",
    ]

    x0 = 0.7
    h = 1e-6

    for expr_str in test_cases:
        ast = parse(expr_str)
        diff_ast = simplify(sym_diff(ast, 'x'))
        sym_val = evaluate(diff_ast, x0, 'x')
        num_val = (evaluate(ast, x0 + h, 'x') - evaluate(ast, x0 - h, 'x')) / (2 * h)
        err = abs(sym_val - num_val)

        print(f"f(x)  = {to_str(ast)}")
        print(f"f'(x) = {to_str(diff_ast)}")
        print(f"  驗證 x={x0}: 符號={sym_val:.10f}  數值={num_val:.10f}  誤差={err:.2e}\n")

    # 二階導數測試
    f_str = "x ^ 3 * sin(x)"
    f_ast = parse(f_str)
    f_p = simplify(sym_diff(f_ast, 'x'))
    f_pp = simplify(sym_diff(f_p, 'x'))
    print("-" * 60)
    print("二階導數測試:")
    print(f"f   = {to_str(f_ast)}")
    print(f"f'  = {to_str(f_p)}")
    print(f"f'' = {to_str(f_pp)}")
