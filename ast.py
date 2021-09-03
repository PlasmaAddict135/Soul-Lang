from typing import Dict, Iterable, List, overload
from runtime import *
from lexer import TokenKind
from lexer import Lexer
import sparser
class AST:
    pass

class SequenceNode(AST):
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def eval(self, state, subject):
        self.first.eval(state, subject)
        return self.second.eval(state, subject)
    def compile(self, state, subject, ind):
        try:
            return self.first.compile(state, subject, ind)+"\n"+self.second.compile(state, subject, ind)
        except:
            str(self.first.eval(state, subject))
            return self.second.compile(state, subject, ind)

class Assign(AST):
    def __init__(self, cmpt: AST, var: AST, assignment: AST):
        self.var = var
        self.assignment = assignment
        self.cmpt = cmpt
    def __repr__(self):
        return self.var
    def eval(self, state, subject):
        state.bind(self.var, self.assignment.eval(state, subject))
        return (TypeChecker(self.var).check(state), self.var)
    def compile(self, state, subject, ind):
        if self.cmpt == None:
            return "    "*ind+"var "+self.var.compile(state, subject, ind)+" = "+self.assignment.compile(state, subject, ind)
        else:
            state.bind(self.var, self.assignment.eval(state, subject))

class AlgerbraicVariable(AST):
    def __init__(self, var: AST):
        self.var = var
    def __repr__(self):
        return self.var
    def eval(self, state, subject):
        state.bind(self.var, None)
    def compile(self, state, subject, ind):
        pass

class AlgebraicCalling(AST):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def eval(self, state, subject):
        state.lookup(self.name)
    def compile(self, state, subject, ind):
        pass

class NumExpr(AST):
    def __init__(self, val: int):
        self.val = val
    def __repr__(self):
        return str(self.val)
    def eval(self, state, subject):
        return self.val
    def compile(self, state, subject, ind):
        return str(self.val)

class String(AST):
    def __init__(self, string: str):
        self.string = string
    def __repr__(self):
        return self.string
    def eval(self, state, subject):
        return self.string
    def compile(self, state, subject, ind):
        return '"'+self.string+'"'

class Comment:
    def __init__(self, comment):
        self.comment = comment
    def eval(self, state, subject):
        pass
    def compile(self, state, subject, ind):
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
    def compile(self, state, subject, ind):
        return "    "*ind+"echo "+self.data.compile(state, subject, 0)

class Echo(AST):
    def __init__(self, data: AST):
        self.data = data
    def __repr__(self):
        return f"echo {self.data}"
    def eval(self, state, subject):
        return self.data.eval(state, subject)
    def compile(self, state, subject, ind):
        print(self.data)
        return "    "*ind+"echo "+self.data.compile(state, subject, 0)

class BreakNode(AST):
    def __init__(self, cmpt, value):
        self.cmpt = cmpt
        self.value = value
    def __repr__(self):
        return self.value
    def eval(self, state, subject):
        raise EarlyBreak(self.value.eval(state, subject))
    def compile(self, state, subject, ind):
        if self.cmpt != None:
            raise str(EarlyBreak(self.value.eval(state, subject)))
        else:
            return "    "*ind+"break"

class ReturnNode(AST):
    def __init__(self, cmpt, value):
        self.cmpt = cmpt
        self.value = value
    def __repr__(self):
        return self.value
    def eval(self, state, subject):
        raise EarlyReturn(self.value.eval(state, subject))
    def compile(self, state, subject, ind):
        if self.cmpt == None:
            return "    "*ind+"return "+self.value.compile(state, subject, 0)
        else:
            raise str(EarlyReturn(self.value.eval(state, subject)))

class FunctionNode(AST):
    def __init__(self, cmpt: AST, name: AST, params: Dict[str, str], return_type: AST, body: AST):
        self.cmpt = cmpt
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
            state_copy.bind("self", state_copy.vals)

            if len(args) != len(self.params):
                raise SyntaxError(f"FunctionCallError: Invalid number of args. Row: {subject.row}, Column: {subject.column}")

            for (param, arg) in zip(self.params, args):
                state_copy.bind(param, arg)

            try:
                return self.body.eval(state_copy, subject)
            except EarlyReturn as ER:
                if self.return_type != "any":
                    if type(ER.value) == self.return_type.eval(current_state, subject):
                        return ER.value
                    if type(ER.value) != self.return_type.eval(current_state, subject):
                        raise TypeReturnNode(f"Function did not return type specified. Row: {subject.row}, Column: {subject.column}")
                else:
                    return ER.value

        state.bind(self.name, call_fn)
        state_copy.bind(self.name, call_fn)
    def compile(self, state, subject, ind):
        if self.cmpt == None:
            return "    "*ind+"proc "+self.name+"("+str(self.params)[1:-1].replace("'", "")+"): "+str(self.return_type)+" =\n"+"    "*ind+self.body.compile(state, subject, ind+1)
        else:
            state_copy = State()
            state_copy.vals = state.vals.copy()

            def call_fn(*args):
                state_copy = State()
                state_copy.vals = state.vals.copy()
                if len(args) != len(self.params):
                    raise SyntaxError(f"(COMPILE TIME) FunctionCallError: Invalid number of args. Row: {subject.row}, Column: {subject.column}")

                for (param, arg) in zip(self.params, args):
                    state_copy.bind(param, arg)

                try:
                    return self.body.eval(state_copy, subject)
                except EarlyReturn as ER:
                    if self.return_type != None:
                        if type(ER.value) == self.return_type.eval(current_state, subject):
                            return ER.value
                        if type(ER.value) != self.return_type.eval(current_state, subject):
                            raise TypeReturnNode(f"(COMPILE TIME) Function did not return type specified. Row: {subject.row}, Column: {subject.column}")
                    else:
                        return ER.value
            state.bind(self.name, call_fn)
            state_copy.bind(self.name, call_fn)


# Thanks Crunch! Very based!
class Call(AST):
    def __init__(self, cmpt: AST, func: AST, args: List[AST]):
        self.func = func
        self.args = args
        self.cmpt = cmpt
    def __repr__(self):
        return self.func
    def eval(self, state, subject):
        function = self.func.eval(state, subject)

        if callable(function):
            args = map(lambda arg: arg.eval(state, subject), self.args)
            return function(*args)
        else:
            raise SyntaxError(f"FunctionCallError: The identifier {self.func} does not belong to a function. Row: {subject.row}, Column: {subject.column}")

    def compile(self, state, subject, ind):
        if self.cmpt == None:
            args = map(lambda arg: arg.compile(state, subject, ind), self.args)
            return "    "*ind+self.name+"("+helper(*args).replace("'", "").replace(")", "").replace("(", "")+")"
        else:
            try:
                function = state.lookup(self.name)
            except:
                function = self.name.eval(state, subject)

            if callable(function):
                args = map(lambda arg: arg.eval(state, subject), self.args)
                return str(function(*args))
            else:
                raise SyntaxError(f"(COMPILE TIME) FunctionCallError: This identifier does not belong to a function. Row: {subject.row}, Column: {subject.column}")

class InputNode(AST):
    def __init__(self, prompt: AST):
        self.prompt = prompt
    def __repr__(self):
        return f'input {self.prompt}'
    def eval(self, state, subject):
        return input(self.prompt.eval(state, subject))
    def compile(self, state, subject, ind):
        return "stdout.write("+self.prompt.compile(state, subject, ind)+")\nreadLine(stdin)"

class VarExpr(AST):
    def __init__(self, cmpt: AST, name: str):
        self.cmpt = cmpt
        self.name = name
    def __repr__(self):
        return self.name
    def eval(self, state, subject):
        return state.lookup(self.name)
    def compile(self, state, subject, ind):
        if self.cmpt == None:
            return "    "*ind+self.name
        else:
            return str(state.lookup(self.name))

class Categories(AST):
    def __init__(self, cmpt: AST, name: AST, objects: AST, body: AST):
        self.cmpt = cmpt
        self.name = name
        self.objects = objects
        self.body = body
    def __repr__(self):
        return f"category {self.name}({self.objects}) { {self.body} }"
    def eval(self, state, subject):
        state_copy = State()
        state_copy.vals = state.vals.copy()

        def call_fn(*args):
            state_copy = State()
            state_copy.vals = state.vals.copy()
            state_copy.bind("self", state_copy.vals)
            try:
                return self.body.eval(state_copy, subject)
            except:
                pass
        state.bind(self.name, call_fn)
        state_copy.bind(self.name, call_fn)
        call_fn()
        return state_copy.vals

class RaiseNode(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f'raise {self.value}'
    def eval(self, state, subject):
        raise self.value.eval(state, subject)
    def compile(self, state, subject, ind):
        return "    "*ind+f"raise {self.value}"

class Run(AST):
    def __init__(self, c: AST, roc: AST, file: AST):
        self.file = file
        self.c = c
        self.roc = roc
    def __repr__(self):
        return self.file
    def eval(self, state, subject):
        if self.c == None:
            f = open(str(self.file)+'.soul', 'r')
            inpt = f.read()
            f.close()
            ast = sparser.Parser(Lexer(inpt)).parse_statements()
            return ast.eval(state, subject)
        elif self.c != None:
            f = open(str(self.file)+'.soul', 'r')
            inpt = f.read()
            f.close()
            start = time.time()
            ast = sparser.Parser(Lexer(inpt)).parse_statements()
            out = open(str(self.file)+".nim", 'w')
            out.write(ast.compile(state, subject, ind))
            if self.roc == None:
                return "Compiled in: "+str(time.time()-start)+" seconds"
            elif self.roc != None:
                print("Compiled in: "+str(time.time()-start)+" seconds")
                print(self.file)
                def prCyan(skk): print('\x1b[0;36m' + skk + '\x1b[0m')
                prCyan("\bExecuting with Nim compiler...")
                sub.Popen(['cmd', '/K', f'nim c -r {self.file}'])
    def compile(self, state, subject, ind):
        return "    "*ind+Run(None, None, self.file).eval(state, subject)

class TypeChecker:
    def __init__(self, name):
        self.name =name
    def check(self, state: State):
        return type(state.lookup(self.name))

class IfExpr(AST):
    def __init__(self, cmpt: AST, cond: AST, left: AST, right: AST):
        self.cmpt = cmpt
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
    def compile(self, state, subject, ind):
        if self.cmpt == None:
            if self.right == None:
                return "    "*ind+"if "+self.cond.compile(state, subject, 0)+":\n"+self.left.compile(state, subject, ind+1)
            else:
                return "    "*ind+"if "+self.cond.compile(state, subject, 0)+":\n"+self.left.compile(state, subject, ind+1)+"\n"+"    "*ind+"else:\n"+self.right.compile(state, subject, ind+1)
        else:
            if self.cond.eval(state, subject):
                return str(self.left.eval(state, subject))
            elif self.right != None:
                return str(self.right.eval(state, subject))

class AssertNode(AST):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"assert {self.value}"
    def eval(self, state, subject):
        assert self.value.eval(state, subject)
    def compile(self, state, subject, ind):
        return "    "*ind+f"assert {self.value}"

class TryExceptNode(AST):
    def __init__(self, cmpt: AST, left: AST, specified: AST, right: AST):
        self.cmpt = cmpt
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
    def compile(self, state, subject, ind):
        if self.cmpt == None:
            if self.specified == None:
                return "    "*ind+"try:\n"+self.left.compile(state, subject, ind), "    "*ind+"except:\n"+self.right.compile(state, subject, ind+1)
            else:
                return "    "*ind+"try:\n"+self.left.compile(state, subject, ind), "    "*ind+f"except {self.specified}:\n"+self.right.compile(state, subject, ind+1)
        else:
            if self.specified == None:
                try:
                    return str(self.left.eval(state, subject))
                except:
                    return str(self.right.eval(state, subject))
            else:
                try:
                    return str(self.left.eval(state, subject))
                except self.specified:
                    return str(self.right.eval(state, subject))

class TrueNode(AST):
    def __init__(self):
        pass
    def __repr__(self):
        return "True"
    def eval(self, state, subject):
        return True
    def compile(self, state, subject, ind):
        return "    "*ind+"True"
class FalseNode(AST):
    def __init__(self):
        pass
    def __repr__(self):
        return "False"
    def eval(self, state, subject):
        return False
    def compile(self, state, subject, ind):
        return "    "*ind+"False"
class NoneNode(AST):
    def __init__(self):
        pass
    def __repr__(self):
        return "None"
    def eval(self, state, subject):
        return None
    def compile(self, state, subject, ind):
        return "    "*ind+"None"

class InitNode(AST):
    def __init__(self, value: AST):
        self.value = value
    def __repr__(self):
        return f"init { {self.value} }"
    def eval(self, state, subject):
        state.bind("self", self.value.eval(state, subject))
        try:
            state.lookup("self")()
        except:
            state.lookup("self")
    def compile(self, state, subject, ind):
        state.bind("self", self.value.eval(state, subject))
        try:
            str(state.lookup("self")())
        except:
            str(state.lookup("self"))

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
    def compile(self, state, subject, ind):
        pass

######################################################################
# WIP (not currently functional)
class SwitchNode(AST):
    def __init__(self, cmpt: AST, switch: AST, cases: Dict[str, AST]):
        self.cmpt = cmpt
        self.switch = switch
        self.cases = cases
    def __repr__(self):
        return f"switch {self.switch} { {self.cases} }"
    def eval(self, state, subject):
        call = self.switch.eval(state, subject)
        print(self.cases)
        if call in self.cases:
            print(self.cases[call].eval(state, subject))
            return self.cases[call].eval(state, subject)
######################################################################

class WhileExpr(AST):
    def __init__(self, cmpt: AST, cond: AST, ret: AST, left: AST):
        self.cmpt = cmpt
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
    def compile(self, state, subject, ind):
        if self.cmpt == None:
            if self.ret == None:
                return "    "*ind+"while "+self.cond.compile(state, subject, ind)+":\n"+"    "*ind+self.left.compile(state, subject, ind)
            else:
                return "    "*ind+"var ret = @[]\nwhile "+self.cond.compile(state, subject, ind)+":    \n"+"ret.add("+self.left.compile(state, subject, ind)+")"+"    "*ind+"ret"
        else:
            x = []
            if self.ret == None:
                while self.cond.eval(state, subject):
                    try:
                        str(x.append(self.left.eval(state, subject)))
                    except EarlyBreak as EB:
                        return str(EB.value)
            else:
                while self.cond.eval(state, subject):
                    try:
                        str(x.append(self.left.eval(state, subject)))
                    except EarlyBreak as EB:
                        return str(EB.value)
                return str(x)
# while

class TypeNode(AST):
    def __init__(self, name: AST, body: Dict[AST, AST]):
        self.name = name
        self.body = body
    def __repr__(self):
        return f"type {self.name} { {self.body} }"
    def eval(self, state, subject):
        cont = {}
        for i in self.body.values():
            for j in self.body.items():
                state.bind(i, state.lookup(j))
                cont[i] = j
        type(self.name, (object, ), cont)

class Array(AST):
    def __init__(self, type_: AST, values: List[AST]):
        self.type = type_
        self.values = values
    def __repr__(self):
        return f"{self.type} -> {self.values}"
    def eval(self, state, subject):
        vals = set([type(i.eval(state, subject)) for i in self.values])
        tvals = {}

        for i in vals: tvals = i
        if self.type != "any":
            if tvals == state.lookup(self.type):
                return self.values
            else:
                raise TypeError("Type of list elements did not match specification")
        else:
            return self.values

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
            name = self.second.eval(state, subject)
            try:
                # NOTE: Enums are accessed by doing: (x being an enum with atribute Y) x."Y"
                return getattr(self.first.eval(state, subject), name)
            except:
                return self.first.eval(state, subject)[name]
    def compile(self, state, subject, ind):
        if self.op == TokenKind.PLUS:
            return "    "*ind+self.first.compile(state, subject, ind)+" + "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.MINUS:
            return "    "*ind+self.first.compile(state, subject, ind)+" - "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.MUL:
            return "    "*ind+self.first.compile(state, subject, ind)+" * "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.DIV:
            return "    "*ind+self.first.compile(state, subject, ind)+" / "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.EQ:
            return "    "*ind+self.first.compile(state, subject, ind)+" == "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.NEQ:
            return "    "*ind+self.first.compile(state, subject, ind)+" != "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.GREAT:
            return "    "*ind+self.first.compile(state, subject, ind)+" > "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.LESS:
            return "    "*ind+self.first.compile(state, subject, ind)+" < "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.IN:
            return "    "*ind+self.first.compile(state, subject, ind)+" in "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.GE:
            return "    "*ind+self.first.compile(state, subject, ind)+" >= "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.LE:
            return "    "*ind+self.first.compile(state, subject, ind)+" <= "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.OR:
            return "    "*ind+self.first.compile(state, subject, ind)+" or "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.AND:
            return "    "*ind+self.first.compile(state, subject, ind)+" and "+self.second.compile(state, subject, ind)
        elif self.op == TokenKind.DOT:
            return "    "*ind+self.first.compile(state, subject, ind)+"."+self.second.compile(state, subject, ind)
# if 1 == 1 {print "ea"}
