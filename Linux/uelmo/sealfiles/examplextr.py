#!/usr/bin/python3
import sys
import numpy

import seal
from seal import LeakageModels

TESTCORE = "uelmo.json"
TESTTRACE = "/tmp/smuelmo.test"

# Weights for bits.
w1 = numpy.random.random((1, 32))[0]  # Weight of OP1
w2 = numpy.random.random((1, 32))[0]  # Weight of OP2

# Dictionary for Seal Symbols
symdict = None


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
    return LeakageModels.HW(x)


# Hamming distance function.
def HD(x, y):
    return LeakageModels.HD(x, y)


# Hamming weight based on D2E registers.
def D2E_data_HW(frame):
    op1 = frame['D2E_reg1_data'][0]
    op2 = frame['D2E_reg2_data'][0]
    print('HW:', HW(op1) + HW(op2))
    return


# Hamming distance based on D2E registers.
def D2E_data_HD(frames):
    op1_pre = frames[0]['D2E_reg1_data'][0]
    op2_pre = frames[0]['D2E_reg2_data'][0]
    op1_pos = frames[1]['D2E_reg1_data'][0]
    op2_pos = frames[1]['D2E_reg2_data'][0]

    print('HD:', HD(op1_pre, op1_pos) + HD(op2_pre, op2_pos))

    return


# Lineart combination of weighted bits based on D2E registers.
def D2E_data_LB(frame):
    global w1, w2
    op1 = frame['D2E_reg1_data'][0]
    op2 = frame['D2E_reg2_data'][0]
    print('LB:', LeakageModels.LinearBits(
        op1, w1) + LeakageModels.LinearBits(op2, w2))
    return


# Symbols of D2E registers.
def D2E_data_Sym(frame):
    global symdict
    sym1 = frame.components['D2E_reg1_data'].symid[0]
    sym2 = frame.components['D2E_reg2_data'].symid[0]

    if symdict is None:
        print('SymID:', sym1, sym2)
        pass
    else:
        print('Symbols:', symdict[sym1], symdict[sym2])

    return


# Main function.
def main(argc, argv):
    global symdict

    # Initialise
    if len(argv) >= 1:
        TESTTRACE = argv[1]

    # Load Core.
    core = seal.Core.Load(TESTCORE)

    # Load Trace.
    st = seal.Trace(core)
    st.Open(TESTTRACE)

    # Extract leakage.
    # HW of D2E regs.
    count = st.Extract(D2E_data_HW)
    print("# Number of leakage extraced:{}\n".format(count))
    st.Reset()

    # Linear weighted bits of D2E regs.
    count = st.Extract(D2E_data_LB)
    print("# Number of leakage extraced:{}\n".format(count))
    st.Reset()

    # HD of D2E regs.
    count = st.Extract(D2E_data_HD, 2)
    print("# Number of leakage extraced:{}\n".format(count))
    st.Reset()

    # Symbol IDs of D2E regs.
    # Import Dictionary if provided.
    if len(sys.argv) >= 3:
        symdict = seal.EncodeDict()
        symdict.Import(sys.argv[2])
        pass
    count = st.Extract(D2E_data_Sym)
    print("# Number of leakage extraced:{}\n".format(count))

    return 0


# main() entry.
if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
