import re

# Files of Transition lines from printlkg.py.
f = open('intlkg.log', 'r')

l = set(f.readlines())

args = re.compile(r"(.+)Interaction\((.+)\,(.+),(.+),(.+)\)\n")


def SyntaxParser(line):
    # Replace negative signs.
    line = line.replace('-a0', 'na0')
    line = line.replace('-a1', 'na1')
    line = line.replace('-b0', 'nb0')
    line = line.replace('-b1', 'nb1')

    # Replace constants by symbolic version.
    line = line.replace('256', 'C256')

    return line


for i in l:
    i = SyntaxParser(i)

    params = args.split(i)

    # Skip NULL and address leakage. Also replace constant 32 by its symbolic version.
    invalidleakage = False
    for p in range(2, 6):
        if params[p] == 'NULL' or params[p].startswith('&'):
            invalidleakage = True
            pass

        if params[p] == '32':
            params[p] = 'C32'
            pass
        pass

    if invalidleakage:
        continue
        pass

    # Parse arguments.
    (a1, a2, a3, a4) = params[2:6]

    print("itl += [({}) + ({}) + ({}) + ({})]".format(a1, a2, a3, a4))

    pass
