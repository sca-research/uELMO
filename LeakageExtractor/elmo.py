#!/usr/bin/python3
import os
import sys
import seal
from seal import LeakageModel
import copy
import json
import numpy

corefile = "uelmo.json"
tracefile = None
usedict = False
DICTFILE = None
sdict = None

# Verbose flag.
verbose = False

# ELMO leakage model configuration.
ELMO_CONFIG = 'elmo.coe'


# Print help message.
def PrintHelp():
    print("Usage: {} {{Trace file or FIFO}} [--dict DICTIONARY] [-v|--verbose] [-h|--help]".format(
        os.path.basename(__file__)))
    return


# Compute x \cdot c
def Mul(x, coe):
    s = 0  # Sum

    i = 0
    while (x != 0):
        if (len(coe) < i):
            raise Exception("Coefficient error")

        if (0x1 & x) == 1:
            s += coe[i]
            pass

        i += 1
        x >>= 1
        pass

    return s


# Convert instruction to constant delta.
def Delta(inst0, inst1):
    # Delta term ignored.
    return 0


# Extract instruction name.
def ExtractInst(inststr):
    return inststr.split()[1]


# The ELMO leakage model.
class Elmo(seal.LeakageModel.Transition):
    def __init__(self, core):
        super().__init__(core)

        # Load ELMO leakage model configurations.
        try:
            coes = numpy.loadtxt(ELMO_CONFIG)
            self.coe = dict()
            self.coe['O1'] = coes[0]
            self.coe['O2'] = coes[1]
            self.coe['T1'] = coes[2]
            self.coe['T2'] = coes[3]
        except:
            raise Exception("ELMO config error")

        return

    # ELMO proportional leakage model.
    def ExtractFN(self, frameseries):
        # Frames
        f0 = frameseries[0]
        f1 = frameseries[1]

        # TraceNo and FrameNo
        TraceNo = f0['TraceNo'][0]
        FrameNo = f0['FrameNo'][0]

        # Skip if the Frames are from difference traces.
        if f0['TraceNo'][0] != f1['TraceNo'][0]:
            return (TraceNo, FrameNo, 0)
            pass

        # Instructions
        inst0 = ExtractInst(f0.components['Execute_instr_disp'].val)
        inst1 = ExtractInst(f1.components['Execute_instr_disp'].val)

        # Operands
        o1 = f1['D2E_reg1'][0]
        o2 = f1['D2E_reg2'][0]

        # Transitions
        t1 = f0['D2E_reg1_data'][0] ^ f1['D2E_reg1_data'][0]
        t2 = f0['D2E_reg2_data'][0] ^ f1['D2E_reg2_data'][0]

        # Leakage of ELMO leakage model
        l = Delta(inst0, inst1) + \
            Mul(o1, self.coe['O1']) + Mul(o2, self.coe['O2']) + \
            Mul(t1, self.coe['T1']) + Mul(t2, self.coe['T2'])

        return (TraceNo, FrameNo, l)

    pass


# Format control for Component printing.
def PrintComponent(comp):
    global sdict, usedict
    # Component info.
    print("{:s} : [ ".format(comp.name), end='')

    # Symbolic info.
    for i in range(len(comp.symid)):
        if usedict:
            # Options only available with a EncDict.
            # Print decoded Symbol.
            symstr = sdict[comp.symid[i]]

            # Simplify NULL by '--'
            if 'NULL' == symstr:
                symstr = '-'

            # Print Symbols with their IDs.
            # print("{:d}:{:s}({:d}) ".format(
            #    i, symstr, comp.symid[i]), end='')
            print("{:s} ".format(symstr), end='')

            pass

        else:
            # Print the encoded Symbol ID.
            print("{:02d} ".format(comp.symid[i]), end='')
            pass

    # Remove last space, then newline.
    print(']')

    return


def main(argc, argv):
    global usedict, sdict, verbose

    # Cmd args check.
    if argc < 2 or '-h' in argv or '--help' in argv:
        PrintHelp()
        exit(0)
        pass

    # Set verbose flag.
    if '-v' in argv or '--verbose' in argv:
        verbose = True
        pass

    # Check if a dictionary file is provided.
    if '--dict' in sys.argv:
        usedict = True
        DICTFILE = sys.argv[sys.argv.index('--dict') + 1]
        pass

    # Initialise Core
    core = seal.Core.Load(corefile)

    # Read Trace
    st = seal.Trace(core)
    st.Open(sys.argv[1])

    # Initialise Leakage Model
    elmo = Elmo(core)

    # Select Components for this Leakage Function.
    elmo.Include(['TraceNo', 'FrameNo', 'Execute_instr_disp', 'D2E_reg1',
                 'D2E_reg2', 'D2E_reg1_data', 'D2E_reg2_data'])

    ntrc = elmo.ExtractTN(st)
    # strc = elmo.ExtractTS(st)

    for i in range(len(ntrc)):
        '''
        # Print each Frame.
        print("#======= FRAME {:02} ======= (Version = {})".format(
            i, core.version))
        print('Num:', ntrc[i])
        print('Sym:', strc[i])
        print("#========********========\n")
        '''
        # TraceNo, FrameNo, leakage value
        (tno, fno, l) = ntrc[i]
        print("{:03d}, {:03d}, {}".format(tno, fno, l))
        pass

    return 0


if __name__ == '__main__':
    exit(main(len(sys.argv), sys.argv))
