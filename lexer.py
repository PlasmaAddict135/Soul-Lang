from enum import Enum
from collections import defaultdict

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
    ROC
    CMPT
    ECHO
    EXCLMK
    INDENT
    DENDENT
    SWITCH
    CASE
    RARROW
    CAT
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
        self.kws['!'] = TokenKind.EXCLMK
        self.kws['not'] = TokenKind.NEQ
        self.kws['>'] = TokenKind.GREAT
        self.kws['<'] = TokenKind.LESS
        self.kws['input'] = TokenKind.INPUT
        self.kws['func'] = TokenKind.FUNC
        self.kws['return'] = TokenKind.RETURN
        self.kws['soul'] = TokenKind.RUN
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
        self.kws['>='] = TokenKind.GE
        self.kws['le'] = TokenKind.LE
        self.kws['<='] = TokenKind.LE
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
        self.kws['r'] = TokenKind.ROC
        self.kws['$'] = TokenKind.CMPT
        self.kws['echo'] = TokenKind.ECHO
        self.kws['switch'] = TokenKind.SWITCH
        self.kws['case'] = TokenKind.CASE
        self.kws['!'] = TokenKind.EXCLMK
        self.kws['->'] = TokenKind.RARROW
        self.kws['category'] = TokenKind.CAT
        self.kws['cat'] = TokenKind.CAT

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
        self.consume_whitespace()
        if self.idx >= len(self.src):
            raise StopIteration
        ch = self.src[self.idx]
        if ch.isalpha() or ch == '_':
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
            try:
                nch = self.src[self.idx+1]
            except:
                nch = ch
            self.eat()
            if kind == TokenKind.ASSIGN:
                if self.kws[nch] == TokenKind.ASSIGN:
                    kind = TokenKind.EQ
                    self.eat()
                else:
                    kind = TokenKind.ASSIGN
            if kind == TokenKind.GREAT:
                if self.kws[nch] == TokenKind.ASSIGN:
                    kind = TokenKind.GE
                    self.eat()
                else:
                    kind = TokenKind.GREAT
            if kind == TokenKind.LESS:
                if self.kws[nch] == TokenKind.ASSIGN:
                    kind = TokenKind.LE
                    self.eat()
                else:
                    kind = TokenKind.LESS
            if kind == TokenKind.EXCLMK:
                if self.kws[nch] == TokenKind.ASSIGN:
                    kind = TokenKind.NEQ
                    self.eat()
                else:
                    kind = TokenKind.EXCLMK
            if kind == TokenKind.MINUS:
                if self.kws[nch] == TokenKind.GREAT:
                    kind = TokenKind.RARROW
                    self.eat()
                else:
                    kind = TokenKind.MINUS
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
        if self.src[self.idx] == "\n" or "\r":
            self.row += 1
            self.column = 1
        else:
            self.column += 1
        self.idx += 1
