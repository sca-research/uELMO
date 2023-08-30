#!/usr/bin/python3
import sys
import numpy

import smurf
from smurf import LeakageModels

TESTCORE = "uelmo.json"
TESTTRACE = None

# Dictionary for Smurf Symbols
symdict = None

# MaskVerif proc name
procname = 'UNDEFINED'


def PrintHelp():
    print("Usage: {} TARGET_TRACE DICTIONARY [PROC_NAME]".format(sys.argv[0]))
    return


'''
# Parse components in a frame into a structured string.
def ParseComponent(comp, seperator=":"):
    compname = comp.name
    comptype = comp.type
    complen = comp.Size()
    compval = ""

    if comp.type == 'OCTET':
        for i in range(comp.len):
            compval += "{:02X} ".format(comp.val[i])
            pass
        pass
    elif comp.type == 'BOOL':
        for i in range(comp.len):
            if comp.val[i]:
                compval += 'T '
                pass
            else:
                compval += 'F '
                pass
            pass
        pass
    elif comp.type == 'STRING':
        compval = comp.val.strip("\0")
        pass

    elif comp.type in {'INT16', 'UINT16'}:
        for i in range(comp.len):
            compval += "{v:04X}({v:d}) ".format(v=comp.val[i])
            pass
    elif comp.type in {'INT32', 'UINT32'}:
        for i in range(comp.len):
            compval += "{v:08X}({v:d}) ".format(v=comp.val[i])
            pass
    else:
        raise("Unknown Component type")

    return "{n}{sep}{t}{sep}{l}{sep}{v}".format(n=compname, t=comptype, l=complen, v=compval.strip(" "), sep=seperator)
'''


# Print with indention control.
def Prt(mvstatement, ilv=0, ichr='    ', iscomment=False):
    indentstr = ''

    # Prepend indention.
    i = 0
    while i < ilv:
        indentstr += ichr
        i += 1
        pass

    # Print the content.
    if iscomment:  # Print in comments.
        print("{:s} (* {:s} *)".format(indentstr, mvstatement))
        pass
    else:
        print(indentstr, mvstatement)
        pass

    return


# Produce MaskVerif header.
def PrintMVHeader():
    global procname
    Prt('proc {:s}:'.format(procname))
    Prt('(* Variable declarations goes here. *)', 1)
    print('')
    return


# Produce MaskVerif script from a Frame.
def FrameToMV(frame):
    global symdict

    # Frame number in comment.
    Prt("Frame {:02d}".format(frame["FrameNo"][0]), 1, iscomment=True)

    # Assign Components with a Symbol
    for compname in frame.components:
        comp = frame.components[compname]

        # Parse annotated Components into a MaskVerif statements.
        if 1 == comp.len:   # Non array Components.
            if comp.symid[0] != 0:
                # Variable name.
                varname = comp.name
                # Value expression decoded from Dictionary.
                valexpr = symdict[comp.symid[0]]
                # Construct MaskVerif statement.
                mvstm = "{:s} := {:s};".format(varname, valexpr)
                # Print
                Prt(mvstm, 1)
            pass

        else:   # Array Compontns.
            if comp.symid.any() != 0:
                # Find all nonzero elements in the array.
                for i in numpy.nonzero(comp.symid)[0]:
                    # Variable name of one member in the array.
                    varname = "{:s}[{:d}]".format(comp.name, int(i))
                    # Value expression decoded from Dictionary for this memer.
                    valexpr = symdict[comp.symid[i]]
                    # Construct MaskVerif statement.
                    mvstm = "{:s} := {:s};".format(varname, valexpr)
                    # Print
                    Prt(mvstm, 1)

                    pass

                pass

            pass
        pass

    # Add a newline serperator.
    print('')

    return


# Procude MaskVerif tailing lines.
def PrintMVTailer():
    Prt('(* End of Frames *)', 1)
    Prt('end\n', 1)
    Prt('verbose 1')
    Prt('noglitch NI {:s}'.format(procname))
    return


# Main function.
def main(argc, argv):
    global symdict, procname

    # Initialise
    if len(argv) < 3:
        PrintHelp()
        exit(0)
        pass

    # Trace file
    TESTTRACE = argv[1]

    # Dictionary file
    symdict = smurf.EncodeDict()
    symdict.Import(sys.argv[2])

    # Load Core.
    core = smurf.Core.Load(TESTCORE)

    # Load Trace.
    st = smurf.Trace(core)
    st.Open(TESTTRACE)

    # Print MaskVerif header.
    if len(sys.argv) >= 4:
        procname = sys.argv[3]
        pass

    # Print MaskVerif header.
    PrintMVHeader()

    # Conver Frames into MaskVerif statements.
    count = st.Extract(FrameToMV)
    # print("# Number of leakage extraced:{}\n".format(count))

    # Print MaskVerif end lines.
    PrintMVTailer()

    return 0


# main() entry.
if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
