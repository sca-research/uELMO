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
    for dictentry in f:
        sep = '::'

        # Find "::" sperator between ID and expression.
        mo = re.search(sep, dictentry)
        if not mo:  # Not a valid entry
            print(dictentry, end='')
            continue
            pass

        # Decode an entry.
        (sepl, sepr) = mo.span()
        dictid = dictentry[:sepl]
        dictexp = dictentry[sepr:]

        # Rewrite constants.
        dictexp = re.sub("32", "C32", dictexp)
        dictexp = re.sub("250", "C250", dictexp)
        dictexp = re.sub("256", "C256", dictexp)

        # exp -> GExp
        dictexp = re.sub("exp", "GExp", dictexp)

        # a*b -> GMul(a,b)
        dictexp = re.sub("[ab][012]\*[ab][012]", Multiply, dictexp)

        # dictexpogX -> GLog(X)
        dictexp = re.sub("log[ab][012]", Logarithm, dictexp)

        print("{}{}{}".format(dictid, sep, dictexp), end='')
    pass

f.close()


done = "32/250/256, exp, x*y"
notdone = ""

# print("# Done:", done)
# print("# Not done: ", notdone)
