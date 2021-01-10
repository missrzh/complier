from collections import ChainMap

var_map = ChainMap()
shift = -4

"""
AST Classes.
"""


class Module():
    def __init__(self, body):
        self.body = body

    def __eq__(self, other):
        return (other is not None
                and self.body == other.body)

    def visit(self):
        mod = ''
        for node in self.body:
            mod += node.visit()

        return mod


class FunctionDef():
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def __eq__(self, other):
        return (other is not None
                and self.name == other.name
                and self.args == other.args
                and self.body == other.body)

    def visit(self):
        global var_map, shift
        func = f'\n{self.name} PROC\n'
        func += 'push ebp\nmov ebp, esp\n'
        scope = {}
        var_map = var_map.new_child(scope)
        for num, param in enumerate(self.args):
            var_map[param] = num*4 + 8
        for node in self.body:
            func += node.visit()
        del var_map.maps[0]
        func += 'mov esp, ebp\npop ebp\n'
        func += f'\nret\n{self.name} ENDP'
        shift = -4
        return func


class CallFunc:
    def __init__(self, id, args):
        self.name = id
        self.args = args

    def visit(self):
        return '\n'.join([f'{val.visit()}\npush eax' for val in reversed(self.args)])+f'\ncall {self.name}\nadd esp, ' \
                                                                              f'{4*len(self.args)}\n'


class Return():
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return (other is not None
                and self.value == other.value)

    def visit(self):
        ret = self.value.visit()

        ret += 'mov esp, ebp\npop ebp\nret\n'
        return ret


class Bin_Op():
    def __init__(self, left, right, operation):
        self.left = left
        self.right = right
        self.operation = operation

    def __eq__(self, other):
        return (other is not None
                and self.left == other.left
                and self.right == other.right
                and self.operation == other.operation)

    def visit(self):
        if self.operation == '-':
            return self.left.visit() + 'push eax\n' + self.right.visit() + 'mov ebx, eax\npop eax\nsub eax, ebx\n'
        if self.operation == '+':
            return self.left.visit() + 'push eax\n' + self.right.visit() + 'mov ebx, eax\npop eax\nadd eax, ebx\n'
        if self.operation == '%':
            return self.left.visit() + 'push eax\n' + self.right.visit() + 'mov ebx, eax\npop eax\nxor edx, edx\n' \
                                                                           'div ebx\nmov eax, edx\n'
        if self.operation == '*':
            return self.left.visit() + 'push eax\n' + self.right.visit() + 'mov ebx, eax\npop eax\nxor edx, edx\n' \
                                                                           'mul ebx\n'


class Unary_Op:
    def __init__(self, target, operation):
        self.target = target
        self.operation = operation

    def visit(self):
        if self.operation == 'not':
            return self.target.visit() + '.if eax == 0\n mov eax, 1\n.else\nmov eax, 0\n.endif\n'


class Ternary:
    def __init__(self, true_con, false_con, condition):
        self.true_con = true_con
        self.false_con = false_con
        self.condition = condition

    def __eq__(self, other):
        return (other is not None
                and self.true_con == other.true_con
                and self.false_con == other.false_con
                and self.condition == other.condition)

    def visit(self):
        return self.condition.visit()+'.if eax == 0\n'+self.false_con.visit()+'.else\n'+self.true_con.visit()+'.endif\n'


class Assign:
    def __init__(self, id: str, expresion):
        self.id = id
        self.expression = expresion

    def __eq__(self, other):
        return (other is not None
                and self.id == other.id
                and self.expression == other.expression)

    def visit(self):
        global shift
        if var_map.get(self.id):
            shift_off = var_map.get(self.id)
            return self.expression.visit() + 'mov DWORD ptr[ebp+' + str(shift_off) + '], eax\n'
        var_map[self.id] = shift
        shift -= 4
        return self.expression.visit() + 'push eax\n'


class Id:
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return (other is not None
                and self.id == other.id)

    def visit(self):
        if var_map.get(self.id):
            shift_off = var_map.get(self.id)
            return 'mov eax, DWORD ptr[ebp+' + str(shift_off) + ']\n'


class Constant:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return (other is not None
                and self.value == other.value)

    def visit(self):
        if type(self.value) == float:
            return 'mov eax, ' + str(int(self.value)) + '\n'
        return 'mov eax, ' + str(self.value) + '\n'
