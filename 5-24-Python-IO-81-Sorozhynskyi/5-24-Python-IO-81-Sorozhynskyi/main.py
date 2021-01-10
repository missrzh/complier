from myparser import parse
from generator import generate

try:
    FILENAME_I = '5-24-Python-IO-81-Sorozhynskyi.txt'
    FILENAME_O = '5-24-Python-IO-81-Sorozhynskyi.asm'
    code = ''
    with open(FILENAME_I) as f:
        code = f.read()
    print(code)
    gp = generate(parse(code))
    print(gp)
    with open(FILENAME_O, 'w') as f:
        f.write(gp)
    input('Press ENTER to exit')
except Exception as err:
    print(f'error {err}')
    input('Press ENTER to exit')
