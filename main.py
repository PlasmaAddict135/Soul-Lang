from enum import Enum
from collections import defaultdict

TokenKind = Enum('TokenKind', 'IF THEN ELSE IDENT INT OPERATOR PRINT STRING VAR ASSIGN UNKNOWN EOF')

class Token:    
    def __init__(self, kind: TokenKind, data):
        self.kind = kind 
        self.data = data 
    
    def as_tuple(self):
        return (self.kind, self.data)

class Lexer:
    src = []
    idx = 0
    kws = defaultdict(lambda: TokenKind.IDENT)

    def __init__(self, src):
        self.src = src 
        self.kws['if'] = TokenKind.IF
        self.kws['{'] = TokenKind.THEN
        self.kws['else'] = TokenKind.ELSE
        self.kws['plus'] = TokenKind.OPERATOR
        self.kws['min'] = TokenKind.OPERATOR
        self.kws['mul'] = TokenKind.OPERATOR
        self.kws['div'] = TokenKind.OPERATOR
        self.kws['print'] = TokenKind.PRINT
        self.kws['var'] = TokenKind.VAR
        self.kws['='] = TokenKind.ASSIGN
    
    def lex_num(self):
        match = ""
        while self.idx < len(self.src) and self.src[self.idx].isdigit():
            match += self.src[self.idx]
            self.idx += 1
        return Token(TokenKind.INT, int(match))

    def lex_ident(self):
        match = ""
        while self.idx < len(self.src) and self.src[self.idx].isidentifier():
            match += self.src[self.idx]
            self.idx += 1
        
        kind = self.kws[match]
        return Token(kind, match)

    def consume_whitespace(self):
        while self.idx < len(self.src) and self.src[self.idx].isspace():
            self.idx += 1
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.idx >= len(self.src):
            raise StopIteration
        self.consume_whitespace()
        ch = self.src[self.idx]

        if ch.isalpha():
            return self.lex_ident()
        elif ch.isdigit():
            return self.lex_num()
        elif ch == '"':
            return self.lex_string_literal()
        elif ch == '=':
            self.idx +=1
            return Token(TokenKind.ASSIGN, None)
        elif ch == '{':
            self.idx += 1
            return Token(TokenKind.THEN, None)
        else:
            return Token(TokenKind.UNKOWN, ch)

    def lex_string_literal(self):
        assert(self.src[self.idx] == '"')
        self.idx += 1

        literal = ""
        while self.idx < len(self.src) and self.src[self.idx] != '"':
            literal += self.src[self.idx]
            self.idx += 1
        
        if self.idx >= len(self.src):
            print("missing end of string delimiter!")
            return Token(TokenKind.UNKNOWN, literal)
        assert(self.src[self.idx] == '"')
        self.idx += 1
        return Token(TokenKind.STRING, literal)


class AST:
    pass 

class State:
    vals = {}
    def bind(self, name, val):
        self.vals[name] = val
    def lookup(self, name):
        return self.vals[name]

class Assign(AST):
    def __init__(self, var: AST, assignment: AST):
        self.var = var
        self.assignment = assignment
    def eval(self, state):
        state.bind(self.var, self.assignment.eval(state))

class IfExpr(AST):
    def __init__(self, cond: AST, left: AST, right: AST):
        self.cond = cond 
        self.left = left 
        self.right = right
    def __repr__(self):
        return "if {} { {} } else {}".format(self.cond, self.left, self.right)
    def eval(self, state):
        if self.cond.eval(state):
            return self.left.eval(state)
        else:
            return self.right.eval(state)


class VarExpr(AST):
    def __init__(self, name: str):
        self.name = name 
    def __repr__(self):
        return self.name
    def eval(self, state):
        return state.lookup(self.name)

class NumExpr(AST):
    def __init__(self, val: int):
        self.val = val
    def __repr__(self):
        return str(self.val)
    def eval(self, state):
        return self.val

class String(AST):
    def __init__(self, string: str):
        self.string = string
    def __repr__(self):
        return self.string
    def eval(self, state):
        return self.string

class Print(AST):
    def __init__(self, data: AST):
        self.data = data
    def __repr__(self):
        return f"print {self.data}"
    def eval(self, state):
        if self.data.eval(state) is not None:
            print(self.data.eval(state))
        else:
            return None
class SyntaxError(Exception):
    pass

class BinOp(AST):
    def __init__(self, op, first: AST, second: AST):
        self.op = op
        self.first = first
        self.second = second
    def __repr__(self):
        return "{} {} {}".format(self.first,self.op,self.second)
    def eval(self, state):
        if self.op == 'plus':
            return self.first.eval(state) + self.second.eval(state)
        elif self.op == 'min':
            return self.first.eval(state) - self.second.eval(state)
        elif self.op == 'mul':
            return self.first.eval(state) * self.second.eval(state)
        elif self.op == 'div':
            return self.first.eval(state) / self.second.eval(state)

class Parser:
    token = Token(TokenKind.UNKNOWN, "dummy")

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = next(self.lexer)
    
    def consume(self):
        try:
            next_token = next(self.lexer)
        except StopIteration:
            next_token = None 
        
        if self.token:
            # swap the current token with the new one
            ret = self.token
            self.token = next_token
            return ret
        return None

    def expect(self, kind: TokenKind):
        if self.token.kind == kind:
            return self.consume()
        raise SyntaxError("Expected token kind {}, found {}".format(kind, self.token.kind))

    def parse_if(self):
        self.expect(TokenKind.IF)
        cond = self.parse_expr()
        self.expect(TokenKind.THEN)
        csq = self.parse_expr()
        self.expect(TokenKind.ELSE)
        alt = self.parse_expr()
        return IfExpr(cond, csq, alt)

    def parse_binop(self):
        op = self.expect(TokenKind.OPERATOR).data 
        first = self.parse_expr()
        second = self.parse_expr()
        return BinOp(op, first, second)

    def parse_num(self):
        data = self.expect(TokenKind.INT).data
        return NumExpr(data)

    def parse_var(self):
        data = self.expect(TokenKind.IDENT).data
        return VarExpr(data)
    
    def parse_assign(self):
        self.expect(TokenKind.VAR)
        ident = self.expect(TokenKind.IDENT).data
        self.expect(TokenKind.ASSIGN)
        value = self.parse_expr()
        return Assign(ident, value)

    def parse_print(self):
        self.expect(TokenKind.PRINT)
        d = self.parse_expr()
        return Print(d)

    def parse_string(self):
        data = self.expect(TokenKind.STRING).data
        return String(data)
        
    def parse_expr(self):
        if self.token is None:
            raise SyntaxError("Unexpected EOF")
        t = self.token.kind
        if t == TokenKind.IF:
            return self.parse_if()
        elif t == TokenKind.IDENT:
            return self.parse_var()
        elif t == TokenKind.INT:
            return self.parse_num()
        elif t == TokenKind.OPERATOR:
            return self.parse_binop()
        elif t == TokenKind.PRINT:
            return self.parse_print()
        elif t == TokenKind.STRING:
            return self.parse_string()
        elif t == TokenKind.VAR:
            return self.parse_assign()
        else:
            raise SyntaxError("Unexpected token {}".format(t))

current_state = State()
while True:
    inpt = input('>>> ')
    print(Parser(Lexer(inpt)).parse_expr().eval(current_state))
