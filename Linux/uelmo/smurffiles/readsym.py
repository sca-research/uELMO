#!/usr/bin/python3
import sys
import smurf

UELMOCORE = "uelmo.json"
TESTTRACE = None
usedict = False
DICTFILE = None

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
TESTTRACE = sys.argv[1]

# Read dictionary
if usedict:
    sdict = smurf.EncodeDict()
    sdict.Import(DICTFILE)
    pass

# Format control for Component printing.


def PrintComponent(comp):
    global sdict, usedict
    # Component info.
    print("{:^8s}: [".format(comp.name), end='')

    # Symbolic info.
    for i in range(len(comp.symid)):
        if usedict:
            # Options only available with a EncDict.
            # Print decoded Symbol.
            #print("{:s} ".format(sdict[comp.symid[i]]), end='')

            # Print Symbols with their IDs.
            print("{:d}:{:s}({:02d}) ".format(
                i, sdict[comp.symid[i]], comp.symid[i]), end='')
            pass

        else:
            # Print the encoded Symbol ID.
            print("{:02d} ".format(comp.symid[i]), end='')
            pass

    # Remove last space, then newline.
    print("\b]")

    return


core = smurf.Core.Load(UELMOCORE)
st = smurf.Trace(core)
st.Open(TESTTRACE)
count = 0
while True:
    frame = st.NextFrame()
    if frame is None:
        break
    print("======= FRAME {:02} =======".format(count))
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
