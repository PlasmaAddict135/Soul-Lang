from enum import Enum
from collections import defaultdict
from os import error
from typing import List, Dict
import sys

TokenKind = Enum('TokenKind', 'IF THEN ELSE IDENT INT OPERATOR PRINT STRING VAR ASSIGN UNKNOWN EOF ENDLN OPEN METHOD BLOCKEND EQ INPUT DIV MUL MINUS PLUS LPAREN RPAREN FUNC RUN COMMA NEQ GREAT LESS RETURN ALGEBRA ALC COMMENT RETURN_TYPE IN WHILE RET BREAK LAMBDA GE LE')

class Token:    
    def __init__(self, row, column, kind: TokenKind, data):
        self.kind = kind 
        self.data = data
        self.row = row
        self.column = column
    
    def as_tuple(self):
        return (self.row, self.column, self.kind, self.data)

class Lexer:
    src = []
    idx = 0
    kws = defaultdict(lambda: TokenKind.IDENT)
    
    def __init__(self, src):
        self.src = src 
        self.kws['if'] = TokenKind.IF
        self.kws['{'] = TokenKind.THEN
        self.kws['}'] = TokenKind.BLOCKEND
        self.kws['('] = TokenKind.LPAREN 
        self.kws[')'] = TokenKind.RPAREN
        self.kws['else'] = TokenKind.ELSE
        self.kws['+'] = TokenKind.PLUS
        self.kws['-'] = TokenKind.MINUS
        self.kws['*'] = TokenKind.MUL
        self.kws['/'] = TokenKind.DIV
        self.kws['print'] = TokenKind.PRINT
        self.kws['var'] = TokenKind.VAR
        self.kws['='] = TokenKind.ASSIGN
        self.kws['open'] = TokenKind.OPEN
        self.kws['r'] = TokenKind.METHOD
        self.kws[';'] = TokenKind.ENDLN
        self.kws[','] = TokenKind.COMMA
        self.kws['=='] = TokenKind.EQ
        self.kws['is'] = TokenKind.EQ
        self.kws['!='] = TokenKind.NEQ
        self.kws['>'] = TokenKind.GREAT
        self.kws['<'] = TokenKind.LESS
        self.kws['input'] = TokenKind.INPUT
        self.kws['func'] = TokenKind.FUNC
        self.kws['return'] = TokenKind.RETURN
        self.kws['sio'] = TokenKind.RUN
        self.kws['import'] = TokenKind.RUN
        self.kws['alg'] = TokenKind.ALGEBRA
        self.kws['@'] = TokenKind.ALC
        self.kws[':'] = TokenKind.RETURN_TYPE
        self.kws['in'] = TokenKind.IN
        self.kws['while'] = TokenKind.WHILE
        self.kws['ret'] = TokenKind.RET
        self.kws['break'] = TokenKind.BREAK
        self.kws['lambda'] = TokenKind.LAMBDA
        self.kws['ge'] = TokenKind.GE
        self.kws['le'] = TokenKind.LE
        
        self.row = 1
        self.column = 1

    def lex_num(self):
        match = ""
        while self.idx < len(self.src) and self.src[self.idx].isdigit():
            match += self.src[self.idx]
            self.eat()
        return Token(self.row, self.column, TokenKind.INT, int(match))

    def current_char_is_valid_in_an_identifier(self):
        current = self.src[self.idx]
        return current.isidentifier() or current == '.'

    def lex_ident(self):
        match = ""
        while self.idx < len(self.src) and self.current_char_is_valid_in_an_identifier():
            match += self.src[self.idx]
            self.eat()
        
        kind = self.kws[match]
        return Token(self.row, self.column, kind, match)

    def consume_whitespace(self):
        while self.idx < len(self.src) and self.src[self.idx].isspace():
            self.eat()
    
    def __iter__(self):
        return self

    # RECOGNIZE NEXT TOKEN
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
        elif ch == "|":
            return self.lex_comment()
        else:
            kind = self.kws[ch]
            self.eat()
            if kind == TokenKind.IDENT:
                kind = TokenKind.UNKNOWN
            return Token(self.row, self.column, kind, ch)

    # FOR EVALUATING STRINGS
    def lex_string_literal(self):
        assert(self.src[self.idx] == '"')
        self.eat()

        literal = ""
        while self.idx < len(self.src) and self.src[self.idx] != '"':
            literal += self.src[self.idx]
            self.eat()
        
        if self.idx >= len(self.src):
            print("Missing end of string delimiter!")
            return Token(self.row, self.column, TokenKind.UNKNOWN, literal)
        assert(self.src[self.idx] == '"')
        self.eat()
        return Token(self.row, self.column, TokenKind.STRING, literal)

    def lex_comment(self):
        assert(self.src[self.idx] == '|')
        self.eat()

        literal = ""
        while self.idx < len(self.src) and self.src[self.idx] != '|':
            literal += self.src[self.idx]
            self.eat()
        
        if self.idx >= len(self.src):
            print("Missing end of comment; |; or just | at end of file")
            return Token(self.row, self.column, TokenKind.UNKNOWN, literal)
        assert(self.src[self.idx] == '|')
        self.eat()
        return Token(self.row, self.column, TokenKind.COMMENT, literal)

    def eat(self):
        if self.src[self.idx] == "\n":
            self.row += 1
            self.column = 1
        else:
            self.column += 1
        self.idx += 1

########################################
# DRIVER CLASSES
########################################

class AST:
    pass 

class State:
    # vals = {}
    def __init__(self):
        self.vals = dict()
    def bind(self, name, val):
        self.vals[name] = val
    def lookup(self, name):
        try:
            return self.vals[name]
        except:
            return eval(name)

class SequenceNode(AST):
  def __init__(self, first, second):
    self.first = first
    self.second = second
  def eval(self, state, subject):
    self.first.eval(state, subject)
    return self.second.eval(state, subject)

class Assign(AST):
    def __init__(self, var: AST, assignment: AST):
        self.var = var
        self.assignment = assignment
    def __repr__(self):
        return self.var
    def eval(self, state, subject):
        state.bind(self.var, self.assignment.eval(state, subject))

class AlgerbraicVariable(AST):
    def __init__(self, var: AST):
        self.var = var
    def __repr__(self):
        return self.var
    def eval(self, state, subject):
        state.bind(self.var, None)

class AlgebraicCalling(AST):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def eval(self, state, subject):
        state.lookup(self.name)

class NumExpr(AST):
    def __init__(self, val: int):
        self.val = val
    def __repr__(self):
        return str(self.val)
    def eval(self, state, subject):
        return self.val

class String(AST):
    def __init__(self, string: str):
        self.string = string
    def __repr__(self):
        return self.string
    def eval(self, state, subject):
        return self.string

class Comment:
    def __init__(self, comment):
        self.comment = comment
    def eval(self, state, subject):
        pass

######################################
# RUN CLASSES
######################################

class Print(AST):
    def __init__(self, data: AST):
        self.data = data
    def __repr__(self):
        return f"print {self.data}"
    def eval(self, state, subject):
        if self.data.eval(state, subject) is not None:
            print(self.data.eval(state, subject))
        else:
            return None

class EarlyReturn(Exception):
    def __init__(self, value):
        self.value = value

class EarlyBreak(Exception):
    def __init__(self, value):
        self.value = value

class BreakNode(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return self.value
    def eval(self, state, subject):
        raise EarlyBreak(self.value.eval(state, subject))

class ReturnNode(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return self.value
    def eval(self, state, subject):
        raise EarlyReturn(self.value.eval(state, subject))

class TypeReturnNode(Exception):
    pass

class FunctionNode(AST):
    def __init__(self, name: AST, params: List[str], return_type: AST, body: AST):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.params = params

    def __repr__(self):
        return f'func {self.name} ({self.params}) ${self.return_type} { {self.body} }'

    def eval(self, state, subject):
        state_copy = State()
        state_copy.vals = state.vals.copy()

        def call_fn(*args):
            state_copy = State()
            state_copy.vals = state.vals.copy()
            if len(args) != len(self.params):
                raise SyntaxError(f"FunctionCallError: Invalid number of args. Row: {subject.row}, Column: {subject.column}")

            for (param, arg) in zip(self.params, args):
                state_copy.bind(param, arg)

            try:
                return self.body.eval(state_copy)
            except EarlyReturn as ER:
                if self.return_type != None:
                    if type(ER.value) == self.return_type.eval(current_state):
                        return ER.value
                    if type(ER.value) != self.return_type.eval(current_state):
                        raise TypeReturnNode(f"Function did not return type specified. Row: {subject.row}, Column: {subject.column}")
                else:
                    return ER.value

        state.bind(self.name, call_fn)
        state_copy.bind(self.name, call_fn)

# Thanks Crunch! Very based!
class Call(AST):
    def __init__(self, name: str, args: List[AST]):
        self.name = name
        self.args = args
    def __repr__(self):
        return self.name
    def eval(self, state, subject):
        function = state.lookup(self.name)

        if callable(function):
            args = map(lambda arg: arg.eval(state, subject), self.args)
            return function(*args)
        else:
            raise SyntaxError(f"FunctionCallError: This identifier does not belong to a function. Row: {subject.row}, Column: {subject.column}")
       
class InputNode(AST):
    def __init__(self, prompt: AST):
        self.prompt = prompt
    def __repr__(self):
        return f'input {self.prompt}'
    def eval(self, state, subject):
        return input(self.prompt.eval(state, subject))

class VarExpr(AST):
    def __init__(self, name: str):
        self.name = name 
    def __repr__(self):
        return self.name
    def eval(self, state, subject):
        return state.lookup(self.name)

class Run(AST):
    def __init__(self, file: AST):
        self.file = file
    def __repr__(self):
        return self.file
    def eval(self, state, subject):
        f = open(self.file+'.sio', 'r')
        inpt = f.read()
        f.close()
        ast = Parser(Lexer(inpt)).parse_statements()
        return ast.eval(state, subject)
        

# WIP
class Open(AST):
    def __init__(self, file: AST, method: AST):
        self.file = file
        self.method = method
    def eval(self, state, subject):
        if self.method == 'r':
            return open(self.file.eval(state, subject), 'r').read()

class SyntaxError(Exception):
    pass

class IfExpr(AST):
    def __init__(self, cond: AST, left: AST, right: AST):
        self.cond = cond 
        self.left = left 
        self.right = right
    def __repr__(self):
        return "if {} { {} } else { {} }".format(self.cond, self.left, self.right)
    def eval(self, state, subject):
        if self.cond.eval(state, subject):
            return self.left.eval(state, subject)
        elif self.right != None:
            return self.right.eval(state, subject)

class WhileExpr(AST):
    def __init__(self, cond: AST, ret: AST, left: AST):
        self.cond = cond 
        self.left = left 
        self.ret = ret
    def __repr__(self):
        return f"while {self.ret} {self.cond} { {self.left} }"
    def eval(self, state, subject):
        x = []
        if self.ret == None:
            while self.cond.eval(state, subject):
                try:
                    x.append(self.left.eval(state, subject))
                except EarlyBreak as EB:
                    return EB.value
        else:
            while self.cond.eval(state, subject):
                try:
                    x.append(self.left.eval(state, subject))
                except EarlyBreak as EB:
                    return EB.value
            return x
# while

class BinOp(AST):
    def __init__(self, first: AST, op, second: AST):
        self.op = op
        self.first = first
        self.second = second
    def __repr__(self):
        return "{} {} {}".format(self.first, self.op,self.second)
    def eval(self, state, subject):
        if self.op == TokenKind.PLUS:
            return self.first.eval(state, subject) + self.second.eval(state, subject)
        elif self.op == TokenKind.MINUS:
            return self.first.eval(state, subject) - self.second.eval(state, subject)
        elif self.op == TokenKind.MUL:
            return self.first.eval(state, subject) * self.second.eval(state, subject)
        elif self.op == TokenKind.DIV:
            return self.first.eval(state, subject) / self.second.eval(state, subject)
        elif self.op == TokenKind.EQ:
            return self.first.eval(state, subject) == self.second.eval(state, subject)
        elif self.op == TokenKind.NEQ:
            return self.first.eval(state, subject) != self.second.eval(state, subject)
        elif self.op == TokenKind.GREAT:
            return self.first.eval(state, subject) > self.second.eval(state, subject)
        elif self.op == TokenKind.LESS:
            return self.first.eval(state, subject) < self.second.eval(state, subject)
        elif self.op == TokenKind.IN:
            return self.first.eval(state, subject) in self.second.eval(state, subject)
        elif self.op == TokenKind.GE:
            return self.first.eval(state, subject) >= self.second.eval(state, subject)
        elif self.op == TokenKind.LE:
            return self.first.eval(state, subject) <= self.second.eval(state, subject)
# if 1 == 1 {print "ea"}
        
class Parser:
    token = Token(1, 1, TokenKind.UNKNOWN, "dummy")
    operators = [TokenKind.PLUS, TokenKind.MINUS, TokenKind.MUL, TokenKind.DIV, TokenKind.EQ, TokenKind.NEQ, TokenKind.LESS, TokenKind.GREAT, TokenKind.IN, TokenKind.LE, TokenKind.GE]

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = next(self.lexer)
    
    def consume(self):
        try:
            next_token = next(self.lexer)
        except StopIteration:
            next_token = None 
        
        if self.token:
            # SWAP THE CURRENT TOKEN WITH THE NEW ONE
            ret = self.token
            self.token = next_token
            return ret
        return None

    def expect(self, kind: TokenKind):
        if self.token.kind == kind:
            return self.consume()
        raise SyntaxError(f"Expected token kind {kind}, found {self.token.kind}. Row: {self.lexer.row}, Column: {self.lexer.column}")

    def accept(self, kind: TokenKind):
        if self.token is not None and self.token.kind == kind:
            self.consume()
            return True
        else:
            return False

    def parse_while(self):
        ret = None
        self.expect(TokenKind.WHILE)
        if self.accept(TokenKind.RET):
            ret = ""
        cond = self.parse_statements()
        then = self.parse_block()
        return WhileExpr(cond, ret, then)

    def parse_if(self):
        self.expect(TokenKind.IF)
        cond = self.parse_statements()
        then = self.parse_block()
        els = None
        if self.accept(TokenKind.ELSE):
            els = self.parse_block()
        return IfExpr(cond, then, els)

    def prece(self, op: TokenKind):
        if op == TokenKind.PLUS:
            return 1
        if op == TokenKind.MUL:
            return 2
        if op == TokenKind.DIV:
            return 2
        if op == TokenKind.MINUS:
            return 1
        if op == TokenKind.EQ or TokenKind.NEQ or TokenKind.IN or TokenKind.LE or TokenKind.GE:
            return 3

    def next_is_operator(self):
        return self.token is not None and self.token.kind in self.operators

    def parse_operator_expr(self):
        first = self.parse_term()
        if self.next_is_operator():
            op = self.parse_operator()
            return self.parse_binop(first, op)  # parse binop needs to be given the previous value and 
                                                # operator, the way i wrote it
        else:
            return first

    def expect_any(self, kinds: list(TokenKind)):
        if self.token.kind in kinds:
            return self.consume()

    def parse_operator(self):
        return self.expect_any(self.operators).kind

    def parse_binop(self, first, op):
        second = self.parse_term()
        if self.next_is_operator():
            next_ = self.parse_operator()
            if self.prece(op) >= self.prece(next_):
                return self.parse_binop(BinOp(first, op, second), next_)  # Binop(first, op, second) becomes the 
                                                                    # first for the recursive call
            else:  # prece(next) > prece(op)
                return BinOp(first, op, self.parse_binop(second, next_))  # recurse to the right, and make the 
                                                                    # resulting expr the second for this call
        else:
            return BinOp(first, op, second)

    def parse_file_open(self):
        self.expect(TokenKind.OPEN).data
        file = self.parse_string()
        method = self.expect(TokenKind.METHOD)
        return Open(file, method)

    def parse_num(self):
        data = self.expect(TokenKind.INT).data
        return NumExpr(data)

    def parse_input(self):
        self.expect(TokenKind.INPUT)
        prompt = self.parse_expr()
        return InputNode(prompt)

    def parse_var(self):
        data = self.expect(TokenKind.IDENT).data
        return VarExpr(data)
    
    def parse_alcall(self):
        self.expect(TokenKind.ALC)
        ident = self.expect(TokenKind.IDENT).data
        return AlgebraicCalling(ident)
    
    def parse_assign(self):
        self.expect(TokenKind.VAR)
        ident = self.expect(TokenKind.IDENT).data
        self.expect(TokenKind.ASSIGN)
        value = self.parse_expr()
        return Assign(ident, value)
    
    def parse_alg(self):
        self.expect(TokenKind.ALGEBRA)
        ident = self.expect(TokenKind.IDENT).data
        return AlgerbraicVariable(ident)

    def parse_statements(self):
        left = self.parse_expr()
        while self.accept(TokenKind.ENDLN):
            right = self.parse_expr()
            left = SequenceNode(left, right)
        return left

    def parse_block(self):
        self.expect(TokenKind.THEN).data
        a = self.parse_statements()
        self.expect(TokenKind.BLOCKEND).data
        return a

    def parse_parenthesized_expr(self):
        self.expect(TokenKind.LPAREN)
        data = self.parse_operator_expr()
        self.expect(TokenKind.RPAREN)
        return data

    def parse_print(self):
        self.expect(TokenKind.PRINT)
        d = self.parse_expr()
        return Print(d)

    def parse_function(self):
        self.expect(TokenKind.FUNC)
        name = self.expect(TokenKind.IDENT).data
        self.expect(TokenKind.LPAREN)
        params = []
        rt = None
        while self.token.kind == TokenKind.IDENT:
            params.append(self.expect(TokenKind.IDENT).data)
            self.accept(TokenKind.COMMA)
        self.expect(TokenKind.RPAREN)
        if self.accept(TokenKind.RETURN_TYPE):
            rt = self.parse_term()
        code = self.parse_block()
        return FunctionNode(name, params, rt, code)
# TODO: func foo(arg) int { return arg }
# WORKING: func foo(arg): int { return arg }
# WORKING: func foo(arg) { return arg }

    def parse_return(self):
        self.expect(TokenKind.RETURN)
        value = self.parse_operator_expr()
        return ReturnNode(value)
    
    def parse_break(self):
        self.expect(TokenKind.BREAK)
        value = self.parse_operator_expr()
        return BreakNode(value)

    def parse_call(self, name):
        args = []
        while self.token.kind != TokenKind.RPAREN:
            args.append(self.parse_operator_expr())
            self.accept(TokenKind.COMMA)
        self.expect(TokenKind.RPAREN)
        return Call(name, args)
 
    def parse_run(self):
        self.expect(TokenKind.RUN)
        file = self.expect(TokenKind.STRING).data
        return Run(file)

    def parse_string(self):
        data = self.expect(TokenKind.STRING).data
        return String(data)

    def parse_comment(self):
        data = self.expect(TokenKind.COMMENT).data
        return Comment(data)

    def parse_term(self):
        t = self.token.kind
        if t == TokenKind.IDENT:
            name = self.expect(TokenKind.IDENT).data
            if self.accept(TokenKind.LPAREN):
                return self.parse_call(name)
            else:
                return VarExpr(name)
        elif t == TokenKind.INT:
            return self.parse_num()
        elif t == TokenKind.STRING:
            return self.parse_string()
        elif t == TokenKind.COMMENT:
            return self.parse_comment()
        elif t == TokenKind.LPAREN:
            return self.parse_parenthesized_expr()
        else:
            raise SyntaxError(f"Unexpected token {t}. Row: {self.lexer.row}, Column: {self.lexer.column}")

    # TO EXECUTE EACH AST NODE WITH ITS CASE    
    def parse_expr(self):
        if self.token is None:
            raise SyntaxError(f"Unexpected EOF. Row: {self.lexer.row}, Column: {self.lexer.column}")
        t = self.token.kind
        if t == TokenKind.IF:
            return self.parse_if()
        elif t == TokenKind.WHILE:
            return self.parse_while()
        elif t == TokenKind.PRINT:
            return self.parse_print()
        elif t == TokenKind.VAR:
            return self.parse_assign()
        elif t == TokenKind.ALGEBRA:
            return self.parse_alg()
        elif t == TokenKind.OPEN:
            return self.parse_file_open()
        elif t == TokenKind.INPUT:
            return self.parse_input()
        elif t == TokenKind.FUNC:
            return self.parse_function()
        elif t == TokenKind.RUN:
            return self.parse_run()
        elif t == TokenKind.RETURN:
            return self.parse_return()
        elif t == TokenKind.BREAK:
            return self.parse_break()
        elif t == TokenKind.ALC:
            return self.parse_alcall()
        else:
            return self.parse_operator_expr()

current_state = State()

# Builtins
def get_state():
    return current_state.vals

def array(*args):
    return list(args)

def append(l, x):
    return l.append(x)

def grab(l, position):
    return l[position]

def insert(l, item, position):
    return l.insert(item, position)

def remove(l, item):
    return l.remove(item)

def pop(l, position):
    return l.pop(position)

def update(l, position, new_value):
    l[position] = new_value

def clear(l):
    return l.clear()

def sys_open():
    return open(sys.argv[1], "r")

def read(file):
    return file.read()

def close(file):
    return file.close()

def write(file, text):
    return file.write(text)

# Inputs
while True:
    inpt = input('>>> ')
    print(Parser(Lexer(inpt)).parse_statements().eval(current_state, Lexer(inpt)))
