"""
Parser library.
"""

from lexer import *
from tree import *

functions = []


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.curr = next(self.lexer, Token(Tag.EOF))

    def match(self, tag):
        """Matches current token tag with the given and advances it."""
        if self.curr is None or self.curr.tag != tag:
            raise SyntaxError(f'at line {self.lexer.line}: expected {tag}, got {self.curr}')
        self.curr = next(self.lexer, Token(Tag.EOF))

    def module(self):
        """Generates Module root node."""

        funcs = []
        while self.curr.tag != Tag.EOF:
            funcs.append(self.func())
        return Module(funcs)

    def func(self):
        """Generates FunctionDef node."""

        global functions
        params = []
        self.match(Tag.DEF)
        name = self.curr.lexeme
        self.match(Tag.ID)
        self.match('(')
        if self.curr.tag == Tag.ID:
            params.append(self.curr.lexeme)
            self.match(Tag.ID)
            while self.curr.tag != ')':
                self.match(',')
                params.append(self.curr.lexeme)
                self.match(Tag.ID)
        functions.append((name, len(params)))
        self.match(')')
        self.match(':')
        body = []
        if self.curr.tag == Tag.NEWLINE:
            self.match(Tag.NEWLINE)
            body = self.func_body_suite()
        else:
            body = list(self.stmt())
        return FunctionDef(name, params, body)

    def func_body_suite(self):
        """Matches function body and generates related nodes."""

        body = []
        self.match(Tag.INDENT)
        while not self.curr.tag == Tag.DEDENT:
            body.append(self.stmt())
        self.match(Tag.DEDENT)

        #if self.curr.tag == Tag.NEWLINE:
        #    self.match(Tag.NEWLINE)
        #    self.match(Tag.INDENT)
        #    body.append(self.stmt())
        #    while not self.curr.tag == Tag.DEDENT:
        #        self.match(Tag.NEWLINE)
        #        body.append(self.stmt())
        #    self.match(Tag.DEDENT)
        #else:
        #    body.append(self.stmt())
        #
        return body

    def stmt(self):
        # print(self.curr.tag)
        """ Generate statement"""
        st = 0
        if self.curr.tag == Tag.RETURN:
            st = self.return_stmt()
        elif self.curr.tag == Tag.ID:
            st = self.assign()
        else:
            raise SyntaxError(f'at line {self.lexer.line}: expected variable or return, got {self.curr}')
        self.match(Tag.NEWLINE)
        return st

    def assign(self):

        id = self.curr.lexeme
        # print(id)
        self.match(Tag.ID)
        if self.curr.tag == Tag.EQUAL:
            self.match(Tag.EQUAL)
            return Assign(id, self.expression())
        elif self.curr.tag == Tag.MIN and self.lexer.curr == '=':
            self.match(Tag.MIN)
            self.match(Tag.EQUAL)
            return Assign(id, Bin_Op(Id(id), self.expression(), '-'))
        elif self.curr.tag == Tag.PLUS and self.lexer.curr == '=':
            self.match(Tag.PLUS)
            self.match(Tag.EQUAL)
            return Assign(id, Bin_Op(Id(id), self.expression(), '+'))

    def div_mul(self):
        left = self.term()
        while self.curr.tag == Tag.PROZENT or self.curr.tag == Tag.MNOZ:
            op = '%' if self.curr == Tag.PROZENT else '*'
            self.match(self.curr.tag)
            right = self.term()
            left = Bin_Op(left, right, op)
        return left

    def plus_minus(self):
        left = self.div_mul()
        while self.curr.tag == Tag.MIN or self.curr.tag == Tag.PLUS:
            op = '-' if self.curr.tag == Tag.MIN else '+'
            self.match(self.curr.tag)
            right = self.div_mul()
            # print(op)
            left = Bin_Op(left, right, op)
        return left

    def operator_not(self):
        if self.curr.tag == Tag.LOGZAP:
            self.match(Tag.LOGZAP)
            return Unary_Op(self.expression(), 'not')
        return self.plus_minus()

    def expression(self):
        true_con = self.operator_not()
        if self.curr.tag == Tag.IF:
            self.match(Tag.IF)
            condition = self.operator_not()
            self.match(Tag.ELSE)
            false_con = self.expression()
            return Ternary(true_con, false_con, condition)
        return true_con

    def term(self):
        # print(self.curr)
        name = self.curr
        if self.curr.tag == Tag.NUM:
            self.match(Tag.NUM)
            return Constant(name.value)
        elif self.curr.tag == Tag.CHAR:
            self.match(Tag.CHAR)
            return Constant(name.value)
        elif self.curr.tag == Tag.ID:
            id = self.curr.lexeme
            self.match(Tag.ID)
            if self.curr.tag == '(':
                self.match('(')
                arguments = []
                if self.curr.tag != ')':
                    arguments.append(self.expression())
                    while self.curr.tag != ')':
                        self.match(',')
                        arguments.append(self.expression())
                self.match(')')
                if (id, len(arguments)) not in functions:
                    raise SyntaxError(f'at line {self.lexer.line}: Unknown Function, {id}')
                return CallFunc(id, arguments)
            #if self.curr.tag == '-' and self.lexer.buff ==
            return Id(id)


        # elif self.curr.tag == Tag.LOGZAP:
        #     self.match(Tag.LOGZAP)
        #     return Unary_Op(self.expression(), 'not')
        else:
            return 'hz'

    def return_stmt(self):
        """Generates Return node."""
        self.match(Tag.RETURN)
        return Return(self.expression())


def parse(code):
    """Parses Python source file."""

    lx = Lexer(iter(code+'\n'))
    lx.reserve(Word(Tag.DEF, 'def'))
    lx.reserve(Word(Tag.LOGZAP, 'not'))
    lx.reserve(Word(Tag.RETURN, 'return'))
    lx.reserve(Word(Tag.IF, 'if'))
    lx.reserve(Word(Tag.ELSE, 'else'))
    ps = Parser(lx)

    return ps.module()

