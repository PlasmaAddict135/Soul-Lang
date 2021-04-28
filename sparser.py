from ast import *
from lexer import *

def update(l, position, new_value):
    l[position] = new_value

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

    def parse_while(self, cmpt=None):
        ret = None
        self.expect(TokenKind.WHILE)
        if self.accept(TokenKind.RET):
            ret = ""
        cond = self.parse_statements()
        then = self.parse_block()
        return WhileExpr(cmpt, cond, ret, then)

    def parse_if(self, cmpt=None):
        self.expect(TokenKind.IF)
        cond = self.parse_statements()
        then = self.parse_block()
        els = None
        if self.accept(TokenKind.ELSE):
            try:
                els = self.parse_block()
            except:
                els = self.parse_expr()
        return IfExpr(cmpt, cond, then, els)

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

    def parse_operator_expr(self, cmpt=None):
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

    def parse_operator(self, cmpt=None):
        return self.expect_any(self.operators).kind

    def parse_binop(self, first, op, cmpt=None):
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

    def parse_num(self, cmpt=None):
        data = self.expect(TokenKind.INT).data
        return NumExpr(data)

    def parse_input(self, cmpt=None):
        self.expect(TokenKind.INPUT)
        prompt = self.parse_expr()
        return InputNode(prompt)

    def parse_var(self, cmpt=None):
        data = self.expect(TokenKind.IDENT).data
        return VarExpr(data)

    def parse_alcall(self, cmpt=None):
        self.expect(TokenKind.ALC)
        ident = self.expect(TokenKind.IDENT).data
        return AlgebraicCalling(ident)

    def parse_assign(self, cmpt=None):
        self.expect(TokenKind.VAR)
        ident = self.expect(TokenKind.IDENT).data
        self.expect(TokenKind.ASSIGN)
        value = self.parse_expr()
        return Assign(cmpt, ident, value)

    def parse_alg(self, cmpt=None):
        self.expect(TokenKind.ALGEBRA)
        ident = self.expect(TokenKind.IDENT).data
        return AlgerbraicVariable(ident)

    def parse_statements(self, cmpt=None):
        left = self.parse_expr()
        while self.accept(TokenKind.ENDLN):
            right = self.parse_expr()
            left = SequenceNode(left, right)
        return left

    def parse_block(self, cmpt=None):
        self.expect(TokenKind.THEN).data
        a = self.parse_statements()
        #print(a)
        self.expect(TokenKind.BLOCKEND).data
        return a

    def parse_parenthesized_expr(self, cmpt=None):
        self.expect(TokenKind.LPAREN)
        data = self.parse_operator_expr()
        self.expect(TokenKind.RPAREN)
        return data

    def parse_print(self, cmpt=None):
        self.expect(TokenKind.PRINT)
        d = self.parse_expr()
        return Print(d)

    def parse_function(self, cmpt=None):
        self.expect(TokenKind.FUNC)
        name = self.expect(TokenKind.IDENT).data
        self.expect(TokenKind.LPAREN)
        params = {}
        while self.token.kind == TokenKind.IDENT:
            t = self.expect(TokenKind.IDENT).data
            if self.accept(TokenKind.COLON):
                pt = self.expect(TokenKind.IDENT).data
                update(params, t, pt)
            else:
                update(params, t, "any")
            self.accept(TokenKind.COMMA)
        self.expect(TokenKind.RPAREN)
        try:
            rt = self.parse_term()
        except:
            rt = "any"
        code = self.parse_block()
        return FunctionNode(cmpt, name, params, rt, code)
# WORKING: func foo(arg) int { return arg }
# WORKING: func foo(arg) { return arg }

    def parse_cat(self, cmpt=None):
        self.expect(TokenKind.CAT)
        name = self.expect(TokenKind.IDENT).data
        self.expect(TokenKind.COLON)
        obj = self.parse_term()
        body = self.parse_block()
        return Categories(cmpt, name, obj, body)

    def parse_return(self, cmpt=None):
        self.expect(TokenKind.RETURN)
        value = self.parse_operator_expr()
        return ReturnNode(cmpt, value)

    def parse_break(self, cmpt=None):
        self.expect(TokenKind.BREAK)
        value = self.parse_operator_expr()
        return BreakNode(cmpt, value)

    def parse_call(self, name, cmpt=None):
        args = []
        while self.token.kind != TokenKind.RPAREN:
            # CHECK TO SEE IF THIS CAUSES AN ERROR, IF IT DOES CHANGE BACK TO parse_operator_expr()
            args.append(self.parse_expr())
            self.accept(TokenKind.COMMA)
        self.expect(TokenKind.RPAREN)
        return Call(cmpt, name, args)

    def parse_run(self, cmpt=None):
        c = None
        r = None
        self.expect(TokenKind.RUN)
        while self.accept(TokenKind.MINUS):
            if self.accept(TokenKind.COMP):
                c = ""
            elif self.accept(TokenKind.ROC):
                r = ""
        file = self.expect(TokenKind.IDENT).data
        return Run(c, r, file)

    def parse_string(self, cmpt=None):
        data = self.expect(TokenKind.STRING).data
        return String(data)

    def parse_comment(self, cmpt=None):
        data = self.expect(TokenKind.COMMENT).data
        return Comment(data)

    def parse_assert(self, cmpt=None):
        self.expect(TokenKind.ASSERT)
        value = self.parse_operator_expr()
        return AssertNode(value)

    def parse_true(self, cmpt=None):
        self.expect(TokenKind.TRUE)
        return TrueNode()

    def parse_false(self, cmpt=None):
        self.expect(TokenKind.FALSE)
        return FalseNode()

    def parse_none(self, cmpt=None):
        self.expect(TokenKind.NONE)
        return NoneNode()

    def parse_try_except(self, cmpt=None):
        self.expect(TokenKind.TRY)
        s = None
        left = self.parse_block()
        self.expect(TokenKind.EXCEPT)
        try:
            right = self.parse_block()
        except:
            s = self.expect(TokenKind.IDENT)
            right = self.parse_block()
        return TryExceptNode(cmpt, left, s, right)

    def parse_raise(self, cmpt=None):
        self.expect(TokenKind.RAISE)
        value = self.parse_expr()
        return RaiseNode(value)

    def parse_init(self, cmpt=None):
        self.expect(TokenKind.INIT)
        if self.accept(TokenKind.COLON):
            v = self.parse_expr()
        else:
            v = self.parse_block()
        return InitNode(v)

    def parse_newline(self, cmpt=None):
        self.expect(TokenKind.NEWLINE)
        return String("\n")

    def parse_echo(self, cmpt=None):
        self.expect(TokenKind.ECHO)
        value = self.parse_expr()
        return Echo(value)

    def parse_switch(self, cmpt=None):
        self.expect(TokenKind.SWITCH)
        i = {}
        switch = self.parse_expr()
        self.expect(TokenKind.THEN)
        while self.token.kind != TokenKind.BLOCKEND:
            self.expect(TokenKind.CASE)
            case = self.parse_expr()
            result = self.parse_block()
            update(i, case, result)
            self.accept(TokenKind.COMMA)
        self.expect(TokenKind.BLOCKEND)
        print(i)
        return SwitchNode(cmpt, switch, i)

    def parse_array(self, cmpt=None, name="any"):
        self.expect(TokenKind.LBRACK)
        elements = []
        while self.token.kind != TokenKind.RBRACK:
            element = self.parse_expr()
            elements.append(element)
            self.accept(TokenKind.COMMA)
        self.expect(TokenKind.RBRACK)
        return Array(name, elements)

    def parse_match(self, cmpt=None):
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
    # !self.foo: foo

    def parse_function_args(self):
        pass

    def parse_term(self):
        term = self.parse_inner_term()
        if self.accept(TokenKind.LPAREN):
            return self.parse_call(term)
        else:
            return term

    def parse_inner_term(self):
        t = self.token.kind
        if t == TokenKind.IDENT:
            name = self.expect(TokenKind.IDENT).data
            if self.accept(TokenKind.RARROW):
                return self.parse_array(None, name)
            else:
                return VarExpr(None, name)
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

    def parse_compile_time(self, cmpt):
        self.consume()
        if self.token is None:
            raise SyntaxError(f"Unexpected EOF. Row: {self.lexer.row}, Column: {self.lexer.column}")
        t = self.token.kind
        if t == TokenKind.IF:
            return self.parse_if(cmpt)
        elif t == TokenKind.WHILE:
            return self.parse_while(cmpt)
        elif t == TokenKind.PRINT:
            return self.parse_print(cmpt)
        elif t == TokenKind.VAR:
            return self.parse_assign(cmpt)
        elif t == TokenKind.ALGEBRA:
            return self.parse_alg(cmpt)
        elif t == TokenKind.INPUT:
            return self.parse_input(cmpt)
        elif t == TokenKind.FUNC:
            return self.parse_function(cmpt)
        elif t == TokenKind.CAT:
            return self.parse_cat()
        elif t == TokenKind.RUN:
            return self.parse_run(cmpt)
        elif t == TokenKind.RETURN:
            return self.parse_return(cmpt)
        elif t == TokenKind.BREAK:
            return self.parse_break(cmpt)
        elif t == TokenKind.IDENT:
            name = self.expect(TokenKind.IDENT).data
            if self.accept(TokenKind.LPAREN):
                return self.parse_call(name, cmpt)
            else:
                return VarExpr(cmpt, name)
        elif t == TokenKind.TRY:
            return self.parse_try_except(cmpt)
        elif t == TokenKind.RAISE:
            return self.parse_raise(cmpt)
        elif t == TokenKind.ASSERT:
            return self.parse_assert(cmpt)
        elif t == TokenKind.INIT:
            return self.parse_init(cmpt)
        elif t == TokenKind.ALC:
            return self.parse_alcall(cmpt)
        elif t == TokenKind.MATCH:
            return self.parse_match(cmpt)
        elif t == TokenKind.SWITCH:
            return self.parse_switch(cmpt)
        else:
            return self.parse_operator_expr(cmpt)

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
        elif t == TokenKind.CMPT:
            return self.parse_compile_time(t)
        elif t == TokenKind.ALC:
            return self.parse_alcall()
        elif t == TokenKind.MATCH:
            return self.parse_match()
        elif t == TokenKind.ECHO:
            return self.parse_echo()
        elif t == TokenKind.SWITCH:
            return self.parse_switch()
        else:
            return self.parse_operator_expr()
