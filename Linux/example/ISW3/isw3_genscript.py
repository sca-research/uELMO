#!/usr/bin/python3

# Requires: Python >= 3.7


import sys
import json
import re

indentlv = 0


def PrintHelpMsg():
    print("Usage: (requires Python >= 3.7)")
    print("\tpython3 [EXTRACTED_LEAKAGE_FILE] [INIT_SCRIPT] [VERIF_SCRIPT]")
    return


# Split an argument string into a list.
def SplitArgs(argstr):
    args = list()

    level = 0
    current = 0
    for i in range(len(argstr)):
        # Step in a parenthesis.
        if argstr[i] == '(':
            level += 1
            pass
        # Step out a parenthesis.
        if argstr[i] == ')':
            level -= 1
            pass

        if argstr[i] == ',':
            # Not in a parenthesis.
            if level == 0:
                # Resolved an arg.
                args.append(argstr[current:i])
                current = i+1
                pass
            pass
        pass

    # Last arg without delimiter.
    args.append(argstr[current:])

    return args


# Decode functional expression "FUNCTIONNAME(ARG0, ARG1, ...)"
def DecodeFunc(exp):
    # Find the first left bracket.
    lb = exp.find('(')

    # Find the last right bracket.
    rb = exp.rfind(')')

    # Function name
    funcname = exp[0: lb]

    # Args.
    args = SplitArgs(exp[lb + 1: -1])

    return (funcname, args)


# Full model.
def Full(x):
    print("# Full({})".format(x))
    return "({})".format(x)


# Full model.
def Linear(x):
    print("# Linear({})".format(x))
    return "({})".format(x)


# Transition
def Transition(x, y):
    #    return "C0"
    print("# Transition({},{})".format(x, y))
    return "(({})*({}))".format(x, y)


# Interaction
def Interaction(a, b, c, d):
    print("# Interaction({},{},{},{})".format(a, b, c, d))
    return "(({})+({})+({})+({}))".format(a, b, c, d)


# Interpret leakage functions into expressions.
def IntepretLkgFunc(func, args):
    if func == "Full":
        exp = Full(*args)
        pass
    elif func == "Linear":
        exp = Linear(*args)
        pass
    elif func == "Transition":
        exp = Transition(*args)
        pass
    elif func == "Interaction":
        exp = Interaction(*args)
        pass
    else:
        print("#Unknown function:", func, args)
        raise Exception("Unknown Leakage Function")
        pass

    return exp


# Generate VerifMsi script initialisation.
def GenScriptInit(importfile=None, frameexp="frameexp", indentlv=0):
    # Import initial Python script.
    if importfile is not None:
        f = open(importfile, 'r')
        importinit = f.read()
        f.close()
        pass
    else:
        importinit = ""
        pass

    initstatement = importinit

    # Init Frame expressions as a list.
    initstatement += '\t'*indentlv + "{} = list()\n".format(frameexp)
    return initstatement


# Expand the current expression.
def ExpandExp(current, new, func=None):
    return "{}+{}".format(current, new)


# Generate VerifMsi script from decoded expressions.
def GenScriptBody(frameexps, frameno, indentlv=0, explist="frameexp", tempexp="tempexp"):
    # Initialise RHS to 0
    rhs = "C0"

    # Interpret the leakage functions into strings.
    for e in frameexps:
        (f, args) = e

        # Skip expressions with NULL.
        if 'NULL' in args:
            continue
            pass

        # Skip address leakages.
        IsAddrArg = False
        for a in args:
            if a.startswith('&'):
                IsAddrArg = True
                break
                pass
            pass
        if IsAddrArg:
            continue
            pass

        # Interpret Leakage functions.
        lkgexp = IntepretLkgFunc(f, args)

        # Combile leakages by sum.
        rhs = ExpandExp(rhs, lkgexp)
        pass

    # Statement for temporary expression.
    tempexp_s = '\t'*indentlv + "{} = {}".format(tempexp, rhs)

    # Add tempexp to the expression list.
    vrfstatement = "{}\n{}.append({})".format(tempexp_s, explist, tempexp)

    return vrfstatement


# Compile symbols.
def CompileSyms(sym):
    global indentlv

    filteredsym = list()

    for s in sym:
        # Skip NO_SYMBOL terms.
        if s == 'NO_SYMBOL':
            continue
            pass

        (func, args) = DecodeFunc(s)
        filteredsym.append((func, args))
        pass

    return filteredsym


# Import verification Python script.
def ImportVerifyScript(importfile=None):
    print('')
    if importfile is None:
        return '# No verify script.'
        pass

    f = open(importfile, 'r')
    verifcode = f.read()
    f.close()

    return verifcode


# Main entry.
def main(argc, argv):
    global indentlv

    if argc < 4 or '-h' in argv:
        PrintHelpMsg()
        return 0
        pass

    lkgfile = json.load(open(argv[1], 'r'))

    # Only need Trace 0.
    trace0 = lkgfile['0']

    # Generate initialisation.
    initstatement = GenScriptInit(argv[2], indentlv=indentlv)
    print(initstatement)

    for frameno in trace0:
        print("# Frame {}".format(frameno))
        frame = trace0[frameno]

        syms = [frame[i]['sym'] for i in frame]

        decodedexp = CompileSyms(syms)

        s = GenScriptBody(decodedexp, frameno, indentlv=indentlv)
        print(s)
        print('')
        pass

    print(ImportVerifyScript(argv[3]))

    return 0


if __name__ == '__main__':
    exit(main(len(sys.argv), sys.argv))
