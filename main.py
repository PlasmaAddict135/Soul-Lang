from enum import Enum
from collections import defaultdict
from os import error
from typing import Dict, List
import sys
import time

TokenKind = Enum(
    'TokenKind',
    '''
    IF
    THEN
    ELSE
    IDENT
    INT
    OPERATOR
    PRINT
    STRING
    VAR
    ASSIGN
    UNKNOWN
    EOF
    ENDLN
    METHOD
    BLOCKEND
    EQ
    INPUT
    DIV
    MUL
    MINUS
    PLUS
    LPAREN
    RPAREN
    FUNC
    RUN
    COMMA
    NEQ
    GREAT
    LESS
    RETURN
    ALGEBRA
    ALC
    COMMENT
    COLON
    IN
    WHILE
    RET
    BREAK
    LAMBDA
    GE
    LE
    ASSERT
    OR
    AND
    TRY
    EXCEPT
    RAISE
    TRUE
    FALSE
    NONE
    LBRACK
    RBRACK
    DOT
    INIT
    NEWLINE
    MATCH
    WITH
    NEXT
    COMP
    '''
)

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
        self.kws[';'] = TokenKind.ENDLN
        self.kws[','] = TokenKind.COMMA
        self.kws['=='] = TokenKind.EQ
        self.kws['is'] = TokenKind.EQ
        self.kws['!='] = TokenKind.NEQ
        self.kws['not'] = TokenKind.NEQ
        self.kws['>'] = TokenKind.GREAT
        self.kws['<'] = TokenKind.LESS
        self.kws['input'] = TokenKind.INPUT
        self.kws['func'] = TokenKind.FUNC
        self.kws['return'] = TokenKind.RETURN
        self.kws['sio'] = TokenKind.RUN
        self.kws['import'] = TokenKind.RUN
        self.kws['alg'] = TokenKind.ALGEBRA
        self.kws['@'] = TokenKind.ALC
        self.kws[':'] = TokenKind.COLON
        self.kws['in'] = TokenKind.IN
        self.kws['while'] = TokenKind.WHILE
        self.kws['ret'] = TokenKind.RET
        self.kws['break'] = TokenKind.BREAK
        self.kws['lambda'] = TokenKind.LAMBDA
        self.kws['ge'] = TokenKind.GE
        self.kws['le'] = TokenKind.LE
        self.kws['or'] = TokenKind.OR
        self.kws['and'] = TokenKind.AND
        self.kws['assert'] = TokenKind.ASSERT
        self.kws['try'] = TokenKind.TRY
        self.kws['except'] = TokenKind.EXCEPT
        self.kws['raise'] = TokenKind.RAISE
        self.kws['None'] = TokenKind.NONE
        self.kws['True'] = TokenKind.TRUE
        self.kws['False'] = TokenKind.FALSE
        self.kws['['] = TokenKind.LBRACK
        self.kws[']'] = TokenKind.RBRACK
        self.kws['.'] = TokenKind.DOT
        self.kws['init'] = TokenKind.INIT
        self.kws['nl'] = TokenKind.NEWLINE
        self.kws['match'] = TokenKind.MATCH
        self.kws['with'] = TokenKind.WITH
        self.kws['next'] = TokenKind.NEXT
        self.kws['c'] = TokenKind.COMP

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
        return current.isidentifier()

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
        elif ch == "'":
            return self.lex_single_quote_literal()
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
    
    def lex_single_quote_literal(self):
        assert(self.src[self.idx] == "'")
        self.eat()

        literal = ""
        while self.idx < len(self.src) and self.src[self.idx] != "'":
            literal += self.src[self.idx]
            self.eat()
        
        if self.idx >= len(self.src):
            print("Missing end of string delimiter!")
            return Token(self.row, self.column, TokenKind.UNKNOWN, literal)
        assert(self.src[self.idx] == "'")
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
    def unbind(self, name):
        return self.vals.pop(name)

class SequenceNode(AST):
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def eval(self, state, subject):
        self.first.eval(state, subject)
        return self.second.eval(state, subject)
    def compile(self):
        return self.first.compile()+"\n"+self.first.compile()

class Assign(AST):
    def __init__(self, var: AST, assignment: AST):
        self.var = var
        self.assignment = assignment
    def __repr__(self):
        return self.var
    def eval(self, state, subject):
        state.bind(self.var, self.assignment.eval(state, subject))
    def compile(self):
        return "var "+self.var.compile()+" = "+self.assignment.compile()

class AlgerbraicVariable(AST):
    def __init__(self, var: AST):
        self.var = var
    def __repr__(self):
        return self.var
    def eval(self, state, subject):
        state.bind(self.var, None)
    def compile(self):
        pass

class AlgebraicCalling(AST):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def eval(self, state, subject):
        state.lookup(self.name)
    def compile(self):
        pass

class NumExpr(AST):
    def __init__(self, val: int):
        self.val = val
    def __repr__(self):
        return str(self.val)
    def eval(self, state, subject):
        return self.val
    def compile(self):
        return str(self.val)

class String(AST):
    def __init__(self, string: str):
        self.string = string
    def __repr__(self):
        return self.string
    def eval(self, state, subject):
        return self.string
    def compile(self):
        return '"'+self.string+'"'

class Comment:
    def __init__(self, comment):
        self.comment = comment
    def eval(self, state, subject):
        pass
    def compile(self):
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
    def compile(self):
        print(self.data.compile())
        return "echo "+self.data.compile()

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
    def compile(self):
        return "break"

class ReturnNode(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return self.value
    def eval(self, state, subject):
        raise EarlyReturn(self.value.eval(state, subject))
    def compile(self):
        return "return "+self.value.compile()

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
                return self.body.eval(state_copy, subject)
            except EarlyReturn as ER:
                if self.return_type != None:
                    if type(ER.value) == self.return_type.eval(current_state, subject):
                        return ER.value
                    if type(ER.value) != self.return_type.eval(current_state, subject):
                        raise TypeReturnNode(f"Function did not return type specified. Row: {subject.row}, Column: {subject.column}")
                else:
                    return ER.value

        state.bind(self.name, call_fn)
        state_copy.bind(self.name, call_fn)
    def compile(self):
        return "method "+self.name+"("+str(self.params)[1:-1].strip("'")+"): "+self.return_type.compile()+" =\n\t"+self.body.compile()

# Thanks Crunch! Very based!
class Call(AST):
    def __init__(self, name: str, args: List[AST]):
        self.name = name
        self.args = args
    def __repr__(self):
        return self.name
    def eval(self, state, subject):
        try:
            function = state.lookup(self.name)
        except:
            function = self.name.eval(state, subject)

        if callable(function):
            args = map(lambda arg: arg.eval(state, subject), self.args)
            return function(*args)
        else:
            raise SyntaxError(f"FunctionCallError: This identifier does not belong to a function. Row: {subject.row}, Column: {subject.column}")
    def compile(self):
        return self.name+"("+str(self.args)[1:-1].strip("'")+")"
       
class InputNode(AST):
    def __init__(self, prompt: AST):
        self.prompt = prompt
    def __repr__(self):
        return f'input {self.prompt}'
    def eval(self, state, subject):
        return input(self.prompt.eval(state, subject))
    def compile(self):
        return "readLine(stdin)"

class VarExpr(AST):
    def __init__(self, name: str):
        self.name = name 
    def __repr__(self):
        return self.name
    def eval(self, state, subject):
        return state.lookup(self.name)
    def compile(self):
        return self.name

class RaiseNode(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f'raise {self.value}'
    def eval(self, state, subject):
        raise self.value.eval(state, subject)
    def compile(self):
        return f"raise {self.value}"

class Run(AST):
    def __init__(self, c: AST, file: AST):
        self.file = file
        self.c = c
    def __repr__(self):
        return self.file
    def eval(self, state, subject):
        if self.c == None:
            f = open(self.file+'.sio', 'r')
            inpt = f.read()
            f.close()
            ast = Parser(Lexer(inpt)).parse_statements()
            return ast.eval(state, subject)
        elif self.c != None:
            print("ping 2")
            f = open(self.file+'.sio', 'r')
            inpt = f.read()
            f.close()
            ast = Parser(Lexer(inpt)).parse_statements()
            out = open(self.file+".nim", 'w')
            return out.write(ast.compile())
    def compile(self):
        return f"import {self.file}"

class SyntaxError(Exception):
    pass

class IfExpr(AST):
    def __init__(self, cond: AST, left: AST, right: AST):
        self.cond = cond 
        self.left = left 
        self.right = right
    def __repr__(self):
        return f"if {self.cond} { {self.left} } else { {self.right} }"
    def eval(self, state, subject):
        if self.cond.eval(state, subject):
            return self.left.eval(state, subject)
        elif self.right != None:
            return self.right.eval(state, subject)
    def compile(self):
        if self.right == None:
            return "if "+self.cond.compile()+":\n\t"+self.left.compile()
        elif self.right != None:
            return "if "+self.cond.compile()+":\n\t"+self.left.compile()+" else:\n\t"+self.right.compile()

class AssertNode(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"assert {self.value}"
    def eval(self, state, subject):
        assert self.value.eval(state, subject)
    def compile(self):
        return f"assert {self.value}"

class TryExceptNode(AST):
    def __init__(self, left, specified, right):
        self.left = left
        self.right = right
        self.specified = specified
    def __repr__(self):
        return f"try { {self.left} } except {self.specified} { {self.right} }"
    def eval(self, state, subject):
        if self.specified == None:
            try:
                return self.left.eval(state, subject)
            except:
                return self.right.eval(state, subject)
        else:
            try:
                return self.left.eval(state, subject)
            except self.specified:
                return self.right.eval(state, subject)
    def compile(self):
        if self.specified == None:
            return "try:\n\t"+self.left.compile(), "except:\n\t"+self.right.compile()
        else:
            return "try:\n\t"+self.left.compile(), f"except {self.specified}:\n\t"+self.right.compile()

class TrueNode(AST):
    def __init__(self):
        pass
    def __repr__(self):
        return "True"
    def eval(self, state, subject):
        return True
    def compile(self):
        return "True"
class FalseNode(AST):
    def __init__(self):
        pass
    def __repr__(self):
        return "False"
    def eval(self, state, subject):
        return False
    def compile(self):
        return "False"
class NoneNode(AST):
    def __init__(self):
        pass
    def __repr__(self):
        return "None"
    def eval(self, state, subject):
        return None
    def compile(self):
        return "None"

class InitNode(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"init { {self.value} }"
    def eval(self, state, subject):
        state.bind("self", self.value.eval(state, subject))
        try:
            state.lookup("self")()
        except:
            state.lookup("self")
    def compile(self):
        pass

class MatchNode(AST):
    def __init__(self, match: AST, cases: Dict[str, AST]):
        self.match = match
        self.cases = cases
    def __repr__(self):
        return f"match {self.match} with { {self.cases} }"
    def eval(self, state, subject):
        if self.match.eval(state, subject) in self.cases:
            return "hello world"
        else:
            print(self.match.eval(state, subject))
            print(self.cases)
    def compile(self):
        pass

class NextNode(AST):
    def __init__(self, iter_: AST):
        self.iter_ = iter_
    def __repr__(self):
        return f"next { {self.iter_} }"
    def eval(self, state, subject):
        return next(self.iter_.eval(state, subject))
    def compile(self):
        pass

class IterNode(AST):
    def __init__(self, value: AST):
        self.value = value
    def __repr__(self):
        return f"iter { {self.value} }"
    def eval(self, state, subject):
        pass
    def __iter__(self):
        return self.value
    def compile(self):
        pass


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
    def compile(self):
        if self.ret == None:
            return "while "+self.cond.compile()+":\t\n"+self.left.compile()
        else:
            return "var ret = @[]\nwhile "+self.cond.compile()+":\t\n"+"ret.add("+self.left.compile()+")", "ret"
# while

class BinOp(AST):
    def __init__(self, first: AST, op, second: AST):
        self.op = op
        self.first = first
        self.second = second
    def __repr__(self):
        return f"{self.first} {self.op} {self.second}"
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
        elif self.op == TokenKind.OR:
            return self.first.eval(state, subject) or self.second.eval(state, subject)
        elif self.op == TokenKind.AND:
            return self.first.eval(state, subject) and self.second.eval(state, subject)
        elif self.op == TokenKind.DOT:
            try:
                # NOTE: Enums are accessed by doing: (x being an enum with atribute Y) x."Y"
                return getattr(self.first.eval(state, subject), self.second.eval(state, subject))
            except:
                return self.first.eval(state, subject)[self.second.eval(state, subject)]
    def compile(self):
        if self.op == TokenKind.PLUS:
            return self.first.compile()+" + "+self.second.compile()
        elif self.op == TokenKind.MINUS:
            return self.first.compile()+" - "+self.second.compile()
        elif self.op == TokenKind.MUL:
            return self.first.compile()+" * "+self.second.compile()
        elif self.op == TokenKind.DIV:
            return self.first.compile()+" / "+self.second.compile()
        elif self.op == TokenKind.EQ:
            return self.first.compile()+" == "+self.second.compile()
        elif self.op == TokenKind.NEQ:
            return self.first.compile()+" != "+self.second.compile()
        elif self.op == TokenKind.GREAT:
            return self.first.compile()+" > "+self.second.compile()
        elif self.op == TokenKind.LESS:
            return self.first.compile()+" < "+self.second.compile()
        elif self.op == TokenKind.IN:
            return self.first.compile()+" in "+self.second.compile()
        elif self.op == TokenKind.GE:
            return self.first.compile()+" >= "+self.second.compile()
        elif self.op == TokenKind.LE:
            return self.first.compile()+" <= "+self.second.compile()
        elif self.op == TokenKind.OR:
            return self.first.compile()+" or "+self.second.compile()
        elif self.op == TokenKind.AND:
            return self.first.compile()+" and "+self.second.compile()
        elif self.op == TokenKind.DOT:
            return self.first.compile()+"."+self.second.compile()
# if 1 == 1 {print "ea"}
        
class Parser:
    token = Token(1, 1, TokenKind.UNKNOWN, "dummy")
    operators = [TokenKind.PLUS, TokenKind.MINUS, TokenKind.MUL, TokenKind.DIV, TokenKind.EQ, TokenKind.NEQ, TokenKind.LESS, TokenKind.GREAT, TokenKind.IN, TokenKind.LE, TokenKind.GE, TokenKind.AND, TokenKind.OR, TokenKind.DOT, TokenKind.ASSIGN]

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
            try:
                els = self.parse_block()
            except:
                els = self.parse_expr()
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
        if op == TokenKind.DOT or TokenKind.ASSIGN or TokenKind.AND or TokenKind.OR:
            return 4

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
                if self.accept(TokenKind.LPAREN):
                    return self.parse_call(self.parse_binop(BinOp(first, op, second), next_))
                else:
                    return self.parse_binop(BinOp(first, op, second), next_)  # Binop(first, op, second) becomes the 
                                                                    # first for the recursive call
            else:  # prece(next) > prece(op)
                if self.accept(TokenKind.LPAREN):
                    return self.parse_call(BinOp(first, op, self.parse_binop(second, next_)))
                else:
                    return BinOp(first, op, self.parse_binop(second, next_))  # recurse to the right, and make the 
                                                                    # resulting expr the second for this call
        else:
            if self.accept(TokenKind.LPAREN):
                return self.parse_call(BinOp(first, op, second))
            else:
                return BinOp(first, op, second)

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
        try:
            rt = self.parse_term()
        except:
            rt = None
        code = self.parse_block()
        return FunctionNode(name, params, rt, code)
# WORKING: func foo(arg) int { return arg }
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
            # CHECK TO SEE IF THIS CAUSES AN ERROR, IF IT DOES CHANGE BACK TO parse_operator_expr()
            args.append(self.parse_expr())
            self.accept(TokenKind.COMMA)
        self.expect(TokenKind.RPAREN)
        return Call(name, args)
 
    def parse_run(self):
        c = None
        print("ping 1")
        self.expect(TokenKind.RUN)
        if self.accept(TokenKind.MINUS):
            if self.accept(TokenKind.COMP):
                c = ""
        file = self.expect(TokenKind.STRING).data
        return Run(c, file)

    def parse_string(self):
        data = self.expect(TokenKind.STRING).data
        return String(data)

    def parse_comment(self):
        data = self.expect(TokenKind.COMMENT).data
        return Comment(data)

    def parse_assert(self):
        self.expect(TokenKind.ASSERT)
        value = self.parse_operator_expr()
        return AssertNode(value)

    def parse_true(self):
        self.expect(TokenKind.TRUE)
        return TrueNode()
    
    def parse_false(self):
        self.expect(TokenKind.FALSE)
        return FalseNode()
    
    def parse_none(self):
        self.expect(TokenKind.NONE)
        return NoneNode()

    def parse_try_except(self):
        self.expect(TokenKind.TRY)
        s = None
        left = self.parse_block()
        self.expect(TokenKind.EXCEPT)
        try:
            right = self.parse_block()
        except:
            s = self.expect(TokenKind.IDENT)
            right = self.parse_block()
        return TryExceptNode(left, s, right)

    def parse_raise(self):
        self.expect(TokenKind.RAISE)
        value = self.parse_expr()
        return RaiseNode(value)

    def parse_init(self):
        self.expect(TokenKind.INIT)
        if self.accept(TokenKind.COLON):
            v = self.parse_expr()
        else:
            v = self.parse_block()
        return InitNode(v)

    def parse_newline(self):
        self.expect(TokenKind.NEWLINE)
        return String("\n")

    def parse_match(self):
        self.expect(TokenKind.MATCH)
        cases = {}
        match = self.parse_expr()
        self.expect(TokenKind.WITH)
        self.expect(TokenKind.THEN)
        while self.token.kind != TokenKind.BLOCKEND:
            matched = self.parse_expr()
            self.expect(TokenKind.COLON)
            result = self.parse_expr()
            cases[matched] = result
            self.accept(TokenKind.COMMA)
        self.expect(TokenKind.BLOCKEND)
        return MatchNode(match, cases)

    def parse_next_method(self):
        self.expect(TokenKind.NEXT)
        try:
            self.expect(TokenKind.COLON)
            it = self.parse_expr()
        except:
            it = self.parse_block()
        return NextNode(it)

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
        elif t == TokenKind.TRUE:
            return self.parse_true()
        elif t == TokenKind.FALSE:
            return self.parse_false()
        elif t == TokenKind.NONE:
            return self.parse_none()
        elif t == TokenKind.COMMENT:
            return self.parse_comment()
        elif t == TokenKind.LPAREN:
            return self.parse_parenthesized_expr()
        elif t == TokenKind.NEWLINE:
            return self.parse_newline()
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
        elif t == TokenKind.TRY:
            return self.parse_try_except()
        elif t == TokenKind.RAISE:
            return self.parse_raise()
        elif t == TokenKind.ASSERT:
            return self.parse_assert()
        elif t == TokenKind.INIT:
            return self.parse_init()
        elif t == TokenKind.ALC:
            return self.parse_alcall()
        elif t == TokenKind.MATCH:
            return self.parse_match()
        elif t == TokenKind.NEXT:
            return self.parse_next_method()
        else:
            return self.parse_operator_expr()

current_state = State()

# Builtins
def get_state():
    return current_state.vals

def delete(variable):
    current_state.unbind(variable)
    return None

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

def split(l, val):
    return l.split(val)

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

def exit():
    return sys.exit()

def print_s(value):
    print(value, end=" ")

def dd(value):
    return defaultdict(lambda: value)

def is_digit(value):
    return value.isdigit()

def is_alpha(value):
    return value.isalpha()

def is_ident(value):
    return value.isidentifier()

def is_space(value):
    return value.isspace()

def sep_enum(name, value):
    x = Enum(name, value)
    return current_state.bind(f"{name}.{value}", str(helper(*x)))

def helper(*args):
    return args

def dict_(key, value):
    return {key: value}

def next_(x):
    return next(x)

# Inputs
while True:
    try:
        f = open(sys.argv[1]+".sio", 'r')
        inpt = f.read()
        f.close()
        print(Parser(Lexer(inpt)).parse_statements().eval(current_state, Lexer(inpt)))
        break
    except:
        inpt = input('>>> ')
        print(Parser(Lexer(inpt)).parse_statements().eval(current_state, Lexer(inpt)))
