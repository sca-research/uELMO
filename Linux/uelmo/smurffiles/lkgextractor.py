#!/usr/bin/python3
import sys
import smurf

TESTCORE = "uelmo.json"
TESTTRACE = "/tmp/smuelmo.test"


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


# Hamming weight function.
def HW(x):
    hw = 0
    while 0 != x:
        hw += x & 0x01
        x = x >> 1
    return hw


# Hamming weight based on D2E registers.
def D2E_data_HW(frame):
    op1 = frame['D2E_reg1_data'][0]
    op2 = frame['D2E_reg2_data'][0]
    print(HW(op1) + HW(op2))
    return


# Main function.
def main(argc, argv):
    # Initialise
    if len(argv) >= 1:
        TESTTRACE = argv[1]

    # Load Core.
    core = smurf.Core.Load(TESTCORE)

    # Load Trace.
    st = smurf.Trace(core)
    st.Open(TESTTRACE)

    # Extract leakage.
    count = st.Extract(D2E_data_HW)

    print("# Number of leakage extraced:", count)

    return 0


# main() entry.
if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
