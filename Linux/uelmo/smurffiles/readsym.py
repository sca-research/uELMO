#!/usr/bin/python3
import sys
import smurf

TESTCORE = "uelmo.json"
TESTTRACE = "/tmp/isw2.et"

if len(sys.argv) >= 1:
    TESTTRACE = sys.argv[1]


def PrintComponent(comp):
    # Component info.
    print("{:^8s}: [".format(comp.name), end='')

    # Symbolic info.
    for i in range(len(comp.symid)):
        print("{:02d} ".format(comp.symid[i]), end='')
        #print("{:>2d}:{:02d} ".format(i, comp.symid[i]), end='')
        pass

    # Remove last space, then newline.
    print("\b]")

    return


core = smurf.Core.Load(TESTCORE)
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
