from enum import Enum
from collections import defaultdict
from os import error
from typing import List, Dict

TokenKind = Enum('TokenKind', 'IF THEN ELSE IDENT INT OPERATOR PRINT STRING VAR ASSIGN UNKNOWN EOF ENDLN OPEN METHOD BLOCKEND EQ INPUT DIV MUL MINUS PLUS LPAREN RPAREN FUNC RUN COMMA NEQ GREAT LESS RETURN ALGEBRA ALC COMMENT')

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

    def lex_num(self):
        match = ""
        while self.idx < len(self.src) and self.src[self.idx].isdigit():
            match += self.src[self.idx]
            self.idx += 1
        return Token(TokenKind.INT, int(match))

    def current_char_is_valid_in_an_identifier(self):
        current = self.src[self.idx]
        return current.isidentifier() or current == '.'

    def lex_ident(self):
        match = ""
        while self.idx < len(self.src) and self.current_char_is_valid_in_an_identifier():
            match += self.src[self.idx]
            self.idx += 1
        
        kind = self.kws[match]
        return Token(kind, match)

    def consume_whitespace(self):
        while self.idx < len(self.src) and self.src[self.idx].isspace():
            self.idx += 1
    
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
            self.idx += 1
            if kind == TokenKind.IDENT:
                kind = TokenKind.UNKNOWN
            return Token(kind, ch)

    # FOR EVALUATING STRINGS
    def lex_string_literal(self):
        assert(self.src[self.idx] == '"')
        self.idx += 1

        literal = ""
        while self.idx < len(self.src) and self.src[self.idx] != '"':
            literal += self.src[self.idx]
            self.idx += 1
        
        if self.idx >= len(self.src):
            print("Missing end of string delimiter!")
            return Token(TokenKind.UNKNOWN, literal)
        assert(self.src[self.idx] == '"')
        self.idx += 1
        return Token(TokenKind.STRING, literal)

    def lex_comment(self):
        assert(self.src[self.idx] == '|')
        self.idx += 1

        literal = ""
        while self.idx < len(self.src) and self.src[self.idx] != '|':
            literal += self.src[self.idx]
            self.idx += 1
        
        if self.idx >= len(self.src):
            print("Missing end of comment; |; or just | at end of file")
            return Token(TokenKind.UNKNOWN, literal)
        assert(self.src[self.idx] == '|')
        self.idx += 1
        return Token(TokenKind.COMMENT, literal)

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
  def eval(self, state):
    self.first.eval(state)
    return self.second.eval(state)

class Assign(AST):
    def __init__(self, var: AST, assignment: AST):
        self.var = var
        self.assignment = assignment
    def __repr__(self):
        return self.var
    def eval(self, state):
        state.bind(self.var, self.assignment.eval(state))

class AlgerbraicVariable(AST):
    def __init__(self, var: AST):
        self.var = var
    def __repr__(self):
        return self.var
    def eval(self, state):
        state.bind(self.var, None)

class AlgebraicCalling(AST):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def eval(self, state):
        state.lookup(self.name)

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

class Comment(AST):
    def __init__(self, comment):
        self.comment = comment
    def eval(self, state):
        pass

######################################
# RUN CLASSES
######################################

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

class EarlyReturn(Exception):
    def __init__(self, value):
        self.value = value

class ReturnNode(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return self.value
    def eval(self, state):
        raise EarlyReturn(self.value.eval(state))

# Thanks for cleaning this up a bit Jfecher
class FunctionNode(AST):
    def __init__(self, name: AST, params: List[str], body: AST):
        self.name = name
        self.params = params
        self.body = body
        self.params = params

    def __repr__(self):
        return f'func {self.name} ({self.params}) { {self.body} }'

    def eval(self, state):
        state_copy = State()
        state_copy.vals = state.vals.copy()

        def call_fn(*args): 
            if len(args) != len(self.params):
                raise SyntaxError("FunctionCallError: Invalid number of args")

            for (param, arg) in zip(self.params, args):
                state_copy.bind(param, arg)

            try:
                return self.body.eval(state_copy)
            except EarlyReturn as ER:
                return ER.value

        return state.bind(self.name, call_fn)

# Thanks Crunch! Very based!
class Call(AST):
    def __init__(self, name: str, args: List[AST]):
        self.name = name
        self.args = args
    def __repr__(self):
        return self.name
    def eval(self, state):
        function = state.lookup(self.name)
        state_copy = State()
        state_copy.vals = state.vals.copy()

        if callable(function):
            args = map(lambda arg: arg.eval(state), self.args)
            return function(*args)
        else:
            raise SyntaxError("FunctionCallError: This identifier does not belong to a function")
       
class InputNode(AST):
    def __init__(self, prompt: AST):
        self.prompt = prompt
    def __repr__(self):
        return f'input {self.prompt}'
    def eval(self, state):
        return input(self.prompt.eval(state))

class VarExpr(AST):
    def __init__(self, name: str):
        self.name = name 
    def __repr__(self):
        return self.name
    def eval(self, state):
        return state.lookup(self.name)

class Run(AST):
    def __init__(self, file: AST):
        self.file = file
    def __repr__(self):
        return self.file
    def eval(self, state):
        f = open(self.file+'.sio', 'r')
        inpt = f.read()
        f.close()
        ast = Parser(Lexer(inpt)).parse_statements()
        return ast.eval(state)
        

# WIP
class Open(AST):
    def __init__(self, file: AST, method: AST):
        self.file = file
        self.method = method
    def eval(self, state):
        if self.method == 'r':
            return open(self.file.eval(state), 'r').read()

class SyntaxError(Exception):
    pass

class IfExpr(AST):
    def __init__(self, cond: AST, left: AST, right: AST):
        self.cond = cond 
        self.left = left 
        self.right = right
    def __repr__(self):
        return "if {} { {} } else { {} }".format(self.cond, self.left, self.right)
    def eval(self, state):
        if self.cond.eval(state):
            return self.left.eval(state)
        elif self.right != None:
            return self.right.eval(state)

class BinOp(AST):
    def __init__(self, first: AST, op, second: AST):
        self.op = op
        self.first = first
        self.second = second
    def __repr__(self):
        return "{} {} {}".format(self.first, self.op,self.second)
    def eval(self, state):
        if self.op == TokenKind.PLUS:
            return self.first.eval(state) + self.second.eval(state)
        elif self.op == TokenKind.MINUS:
            return self.first.eval(state) - self.second.eval(state)
        elif self.op == TokenKind.MUL:
            return self.first.eval(state) * self.second.eval(state)
        elif self.op == TokenKind.DIV:
            return self.first.eval(state) / self.second.eval(state)
        elif self.op == TokenKind.EQ:
            return self.first.eval(state) == self.second.eval(state)
        elif self.op == TokenKind.NEQ:
            return self.first.eval(state) != self.second.eval(state)
        elif self.op == TokenKind.GREAT:
            return self.first.eval(state) > self.second.eval(state)
        elif self.op == TokenKind.LESS:
            return self.first.eval(state) < self.second.eval(state)
# if 1 == 1 {print "ea"}
        
class Parser:
    token = Token(TokenKind.UNKNOWN, "dummy")
    operators = [TokenKind.PLUS, TokenKind.MINUS, TokenKind.MUL, TokenKind.DIV, TokenKind.EQ, TokenKind.NEQ, TokenKind.LESS, TokenKind.GREAT]

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
        raise SyntaxError("Expected token kind {}, found {}".format(kind, self.token.kind))

    def accept(self, kind: TokenKind):
        if self.token is not None and self.token.kind == kind:
            self.consume()
            return True
        else:
            return False

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
        if op == TokenKind.EQ:
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
        while self.token.kind == TokenKind.IDENT:
            params.append(self.expect(TokenKind.IDENT).data)
            self.accept(TokenKind.COMMA)
        self.expect(TokenKind.RPAREN)
        code = self.parse_block()
        return FunctionNode(name, params, code)

    def parse_return(self):
        self.expect(TokenKind.RETURN)
        value = self.parse_operator_expr()
        return ReturnNode(value)

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
            raise SyntaxError("Unexpected token {}".format(t))

    # TO EXECUTE EACH AST NODE WITH ITS CASE    
    def parse_expr(self):
        if self.token is None:
            raise SyntaxError("Unexpected EOF")
        t = self.token.kind
        if t == TokenKind.IF:
            return self.parse_if()
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

# Inputs
while True:
    inpt = input('>>> ')
    print(Parser(Lexer(inpt)).parse_statements().eval(current_state))
