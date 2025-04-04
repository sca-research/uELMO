import re

# Files of Transition lines from printlkg.py.
f = open('../translkg.log', 'r')

l = set(f.readlines())

args = re.compile(r"(.+)Transition\((.+)\,(.+)\)\n")


def SyntaxParser(line):
    # Replace negative signs.
    line = line.replace('-a0', 'na0')
    line = line.replace('-a1', 'na1')
    line = line.replace('-b0', 'nb0')
    line = line.replace('-b1', 'nb1')

    # Replace constants by symbolic version.
    line = line.replace('256', 'C256')

    # Replace multiplications.
    line = line.replace('a0*b0', 'a0b0')
    line = line.replace('a0*b1', 'a0b1')
    line = line.replace('a1*b0', 'a1b0')
    line = line.replace('a1*b1', 'a1b1')

    return line


for i in l:
    i = SyntaxParser(i)

    params = args.split(i)
    (x, y) = params[2:4]

    if x.startswith('&') or y.startswith('&') or 'NULL' in [x, y] or x == y:
        continue
        pass

    # Replace 32 by C32 if used as a complete expression.
    if x == '32':
        x = 'C32'
        pass
    if y == '32':
        y = 'C32'
        pass

    #print('trs += [Concat(({}), ({}))]'.format(x, y))
    print('trs += [({}) + ({})]'.format(x, y))

    pass
