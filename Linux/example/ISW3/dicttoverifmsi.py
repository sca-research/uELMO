#!/usr/bin/python3

import sys
import re


def Multiply(mo):
    (start, end) = mo.span()
    s = mo.string[start: end]
    r = s.replace('*', ',')
    r = "GMul({})".format(r)
    return r


def Logarithm(mo):
    (start, end) = mo.span()
    s = mo.string[start: end]
    arg = s.strip('log')

    ret = "GLog({})".format(arg)

    return ret


with open(sys.argv[1], 'r') as f:
    for l in f:
        # Rewrite constants.
        l = re.sub("32", "C32", l)
        l = re.sub("250", "C250", l)
        l = re.sub("256", "C256", l)

        # exp -> GExp
        l = re.sub("exp", "GExp", l)

        # a*b -> GMul(a,b)
        l = re.sub("[ab][012]\*[ab][012]", Multiply, l)

        # logX -> GLog(X)
        l = re.sub("log[ab][012]", Logarithm, l)

        print(l, end='')
    pass

f.close()


done = "32/250/256, exp, x*y"
notdone = ""

# print("# Done:", done)
# print("# Not done: ", notdone)
