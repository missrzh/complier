"""
Simple lexer library.
"""

from enum import Enum

HELPERS = ['(', ')', ':', ',']
OPERATORS = ['-', 'not', '=', '+', '%', '*']


class Tag(Enum):
    NUM = 'num'
    CHAR = 'char'
    ID = 'id'
    INDENT = 'indent'
    DEDENT = 'dedent'
    NEWLINE = 'newline'
    RETURN = 'return'
    DEF = 'def'
    MIN = '-'
    LOGZAP = 'not'
    EQUAL = '='
    PLUS = '+'
    PROZENT = '%'
    IF = 'if'
    ELSE = 'else'
    EOF = 'eof'
    MNOZ = '*'


class Token:
    def __init__(self, tag):
        self.tag = tag

    def __eq__(self, other):
        return other is not None and self.tag == other.tag

    def __str__(self):
        return f'<{self.tag}>'

    def __repr__(self):
        return self.__str__()


class Operator(Token):
    def __init__(self, val):
        tag = None
        if val == '-':
            tag = Tag.MIN
        elif val == 'not':
            tag = Tag.LOGZAP
        elif val == '=':
            tag = Tag.EQUAL
        elif val == '+':
            tag = Tag.PLUS
        elif val == '%':
            tag = Tag.PROZENT
        elif val == '*':
            tag = Tag.MNOZ
        super().__init__(tag)
        self.value = val

    def __str__(self):
        return f'<{self.tag}, {self.value}>'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return other and self.value == other.value


class Num(Token):
    def __init__(self, val):
        super().__init__(Tag.NUM)
        self.value = val

    def __str__(self):
        return f'<{self.tag}, {self.value}>'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return other and self.value == other.value


class Char(Token):
    def __init__(self, val):
        super().__init__(Tag.CHAR)
        self.value = val

    def __str__(self):
        return f'<{self.tag}, {self.value}>'

    def __repr__(self):
        return self.__str__()


class Word(Token):
    def __init__(self, tag, lex):
        super().__init__(tag)
        self.lexeme = lex

    def __str__(self):
        return f'<{self.tag}, {self.lexeme}>'

    def __repr__(self):
        return self.__str__()


class Lexer:
    def __init__(self, inpstr):  # inputstream(iterator)
        self.inpstr = inpstr
        self.indstk = [0]  # indentstack
        self.pended = 0
        self.words = {}  # dict keywords, IDs ->TokenTag
        self.isnl = True  # logicline detection
        self.buff = ''
        self.curr = next(self.inpstr, '')
        self.line = 1
        self.wasind = False

    def __iter__(self):
        return self

    def get_raw(self):
        self.curr = next(self.inpstr, '')

    def get(self):
        if self.buff != '':
            self.curr = self.buff[0]
            self.buff = self.buff[1:]
        else:
            self.get_raw()

    def put(self):
        self.buff += self.curr

    def reserve(self, w):
        """Adds new entry to words, associating the lexeme with the token."""

        self.words.setdefault(w.lexeme, w)

    def number(self):
        """Returns NUM token."""

        v = 0
        p = 0
        if self.curr == '0':
            self.get()

        if self.curr == 'x':
            self.get()
            hex_digits = 'ABCDEFabcdef'
            hex_number = ''
            while (self.curr.isdigit() or self.curr in hex_digits) and self.curr != '':
                hex_number += self.curr
                # print(hex_number)
                self.get()
            v = int(hex_number, 16)
        else:
            part = False
            decimal_power = 0
            while self.curr.isdigit() or self.curr == '.':
                if self.curr == '.':
                    part = True
                    self.get()
                if not part:
                    v = v * 10 + int(self.curr)
                else:
                    decimal_power += 1
                    p = p + int(self.curr)/10**decimal_power
                self.get()
        # self.put() # TODO ??????????????????WTF???????????????????????
        return Num(v+p)

    def word(self):
        """Returns Word-type token (IDs, keywords)."""

        s = ''
        w = None
        while self.curr.isalpha():
            s += self.curr
            self.get()
        # self.put()
        # print(s, self.words)
        w = self.words.get(s)
        if w is not None:
            return w

        w = Word(Tag.ID, s)
        self.words.setdefault(w.lexeme, w)
        return w

    def char(self):
        """Returns Char token."""

        self.get()
        if (self.curr == '\''
                or self.curr == '\"'):
            raise SyntaxError(f'at line {self.line}: expected char, got {self.curr}')
        c = list(self.curr)
        self.get()
        if self.curr != '\'':
            raise SyntaxError(f'at line {self.line}: expected quote, got {self.curr}')

        return Char(c)

    def cut_lines(self):
        while self.isnl and (self.curr == '\n' or self.curr == ' '):
            if self.curr == '\n':
                self.line += 1
                self.get()
            if self.curr == ' ' and self.is_indent():
                self.get()
                break
            self.cut_spaces()

    def cut_spaces(self):
        spaces = 0
        while self.curr == ' ':
            self.get()
            spaces += 1
        return spaces

    def is_indent(self):
        if self.curr != ' ':
            return False
        tmp = self.curr
        while self.curr == ' ':
            self.get_raw()
            self.put()
        ch = self.curr
        self.curr = tmp
        return not (ch == '\n' or ch == '')

    def newline(self):
        self.line += 1
        self.isnl = True
        self.wasind = False
        self.get()
        return Token(Tag.NEWLINE)

    def end(self):
        if self.pended > 0:
            self.pended -= 1
            return Token(Tag.DEDENT)
        return Token(Tag.EOF)

    def other(self):
        if self.curr.isdigit():
            return self.number()
        if self.curr in OPERATORS:
            return self.operator()
        if self.curr.isalpha():
            return self.word()
        if self.curr == '\'':
            return self.char()
        if self.curr in HELPERS:
            return self.helper()
        raise SyntaxError(f'illegal character, at line {self.line}: {self.curr}')

    def operator(self):
        op = Operator(self.curr)
        self.get()
        return op

    def helper(self):
        hl = Token(self.curr)
        self.get()
        return hl

    def indent(self):
        self.wasind = False
        self.isnl = False
        self.pended += 1
        return Token(Tag.INDENT)

    def dedent(self):
        self.wasind = False
        self.indstk.pop()
        self.pended -= 1
        return Token(Tag.DEDENT)

    def dent(self):
        width = self.cut_spaces()
        if width > self.indstk[-1]:
            self.indstk.append(width)
            return self.indent()
        if width < self.indstk[-1] and width == self.indstk[-2]:
            return self.dedent()
        if width == self.indstk[-1]:
            self.wasind = True
            return self.__next__()

    def __next__(self):
        """Returns the next token."""

        self.cut_lines()

        if self.curr == '':
            return self.end()

        if self.isnl and self.curr == ' ':
            return self.dent()

        if self.isnl and not self.curr == '\n' and len(self.indstk) > 1 and not self.wasind:
            return self.dedent()
        # elif self.isnl and len(self.indstk) > 1 :
        #     self.indstk.pop()
        #     self.isnl = False
        #     return self.dedent()
        # print(self.curr, self.isnl, self.is_indent())

        self.isnl = False

        self.cut_spaces()

        if not self.isnl and self.curr == '\n':
            return self.newline()
        return self.other()
