"""
Code generator.
"""

from tree import FunctionDef


class NoEntryError(Exception):
    def __init__(self, message):
        self.message = message


def has_main(tree):
    """Determines whether a tree has main function."""

    for node in tree.body:
        if (isinstance(node, FunctionDef)
                and node.name == 'main'):
            return True

    return False


def generate(tree):
    """Generates MASM32 code from AST."""

    if not has_main(tree):
        raise NoEntryError('No entry point has been found.')

    HEADER = (
        """.386
.model flat, stdcall
option casemap:none
include C://masm32/include/masm32rt.inc 
main PROTO
.data
.code
""")

    generated = tree.visit()

    ENTRY = ("""
start:
    invoke main
    fn MessageBox,0,str$(eax), "Lab5" ,MB_OK
    invoke ExitProcess, 0
    """)
    END = ("""

END start""")

    return f'{HEADER}{ENTRY}{generated}{END}'
