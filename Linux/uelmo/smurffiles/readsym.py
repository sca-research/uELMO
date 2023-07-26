#!/usr/bin/python3
import sys
import smurf

UELMOCORE = "uelmo.json"
tracefile = None
usedict = False
DICTFILE = None
sdict = None


# Format control for Component printing.
def PrintComponent(comp):
    global sdict, usedict
    # Component info.
    print("{:s} : [".format(comp.name), end='')

    # Symbolic info.
    for i in range(len(comp.symid)):
        if usedict:
            # Options only available with a EncDict.
            # Print decoded Symbol.
            symstr = sdict[comp.symid[i]]

            # Simplify NULL by '--'
            if 'NULL' == symstr:
                symstr = '--'

            # Print Symbols with their IDs.
            print("{:d}:{:s}({:d}) ".format(
                i, symstr, comp.symid[i]), end='')
            pass

        else:
            # Print the encoded Symbol ID.
            print("{:02d} ".format(comp.symid[i]), end='')
            pass

    # Remove last space, then newline.
    print(']')

    return


def main(argc, argv):
    global usedict, sdict

    if len(sys.argv) < 2:
        print("Usage: python3 readsym.py TRACE_FILE [DICTIONARY]")
        exit()
        pass

    # Check if a dictionary file is provided.
    if len(sys.argv) >= 3:
        usedict = True
        DICTFILE = sys.argv[2]
        pass

    # Target trace.
    tracefile = sys.argv[1]

    # Read dictionary
    if usedict:
        sdict = smurf.EncodeDict()
        sdict.Import(DICTFILE)
        pass

    core = smurf.Core.Load(UELMOCORE)
    st = smurf.Trace(core)
    st.Open(tracefile)
    count = 0
    while True:
        frame = st.NextFrame()
        if frame is None:
            break
        print("======= FRAME {:02} =======".format(count))

        # Print current Execution cycle.
        print("Core status ~ {:s}".format(
            frame['Execute_instr_disp'].strip('\0')))

        nosym = True

        # Print all Components with Symbols.
        for i in frame.components:
            if frame.components[i].symid.any():
                PrintComponent(frame.components[i])
                nosym = False
                pass

        if nosym:
            print("Symbolic information not available.")
            pass
        pass

        count += 1
        print("========================\n")

    return


if __name__ == '__main__':
    exit(main(len(sys.argv), sys.argv))
