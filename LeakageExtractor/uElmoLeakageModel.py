#!/usr/bin/python3
import os
import sys
import json
import base64

import seal

FORCE_LINEAR = 0  # force all leakage to be linear

NON_ACTIVE_REG = 1  # Allows leakage for non-active registers
NON_ACTIVE_MEM = 1  # Allows leakage for non-active memory buses

MICROARCHITECTURAL = 1  # Allows leakage from the micro-architecture
CPSR = 1  # Allows leakage from the CPSR register
DECODE_PORT = 1  # Allows leakage from the decoding register access
GLITCHY_DECODE = 1  # Allows for glitchy decoding register access

TRANSITION = 1  # Allows for transition leakage
LSB_NEIGHBOUR = 1  # Allows for LSB based neibouring effect


# Load uELMO Source of Leakage
sol = json.load(open('uelmosol.json', 'r'))

# Seal Encoding dictionary for Symbols.
symdict = None

# Leakage functions.
LEAKAGE_FUNC = {0: 'Full', 1: 'Linear', 2: 'Transition', 3: 'Interaction'}


# Output file
outfile = dict()


# Print help message.
def PrintHelp():
    print(
        "Usage:\tpython3 {} {{TARGET_TRACE}} [DICTIONARY_FILE]".format(os.path.basename(__file__)))
    return


# Encode a Symbol ID into string.
def SymToStr(symid):
    global symdict
    if symdict is None:
        return str(symid)
        pass
    else:
        return symdict[symid]
        pass

    return


# Construct expanded expression from a given operand and a list of Symbol IDs.
def ExpandExpr(op, *symids):
    expr = str()

    # Return None string if all args are NULL.
    if all(sym == seal.SYM_ID_NULL for sym in symids):
        return ""
        pass

    # Prepends operand.
    expr += op + '('  # 'op('

    # Add the first argument.
    expr += SymToStr(symids[0])  # 'op(arg0'
    symids = symids[1:]

    # Add other arguments.
    for arg in symids:
        expr += ','+SymToStr(arg)
        pass

    # Enclose bracket.
    expr += ')'

    return expr


# Trim a byte array.
def TrimBytes(origin):
    # Find the last non zero byte.
    for i in reversed(range(len(origin))):
        if 0 != origin[i]:
            i += 1
            break
        pass

    if i == 0:
        return bytes([0])
    else:
        return origin[0: i]


# Encode bytes into utf8 string using base85.
def B2SEncode(data, dlen=None):
    if type(data) is int:
        data = data.to_bytes(dlen, 'little')
        pass
    encstr = base64.b85encode(TrimBytes(data)).decode('utf8')
    return encstr


# Write out leakage.
def WriteLeakage(src, data, frame=None, expr=None):
    global sol, symdict
    datatype = sol[src]['type']
    datalen = sol[src]['len']
    compname = sol[src]['compname']
    compidx = sol[src]['compidx']

    if expr is None:  # Expression not specified.
        # Use default expression.
        # Default expression unavailble.
        if frame is None or compname == 'NULL':
            expr = "EXPRESSION_NOT_AVIALBLE"
            pass

        else:  # Symbol annotated in the trace.
            symid = frame.components[compname].symid[compidx]
            if symid == seal.SYM_ID_NULL:  # Symbol ID is NULL.
                expr = "NO_SYMBOL"
                pass
            else:  # Symbol annotated in uELMO.
                expr = "{:s}({:s})".format(
                    LEAKAGE_FUNC[datatype], SymToStr(symid))
                pass
            pass
        pass
    elif expr == '':  # NULL expression.
        expr = "NO_SYMBOL"
        pass

    print("{:s}({:d}) : [{:d}] {} *{:s}".format(
        src, datatype, datalen, data, expr))
    datablob = {'val': B2SEncode(data, datalen), 'sym': expr}

    return (src, datablob)


# Output type of a leakage.
def LeakageType(name, lkgtype):
    print("{:s}: {:d}".format(name, lkgtype))
    return


# Header for leakage handled by the uELMO modeling/detection method.
def UelmoHeader(core):
    print('#uELMO leakage header')
    print('#{Name}: {Type}')
    # Part 1: select components.
    # reg[]
    if NON_ACTIVE_REG:
        for i in range(core.components['reg'].len):
            LeakageType('Reg {:d}'.format(i), 0)
            pass
        pass

    # CPSR
    if CPSR:
        LeakageType('CPSR', 1)
        pass

    # Pipline registers
    if MICROARCHITECTURAL:
        LeakageType("Pipeline Reg 1", 0)
        LeakageType("Pipeline Reg 2", 0)
        pass

    # Decoding register
    if MICROARCHITECTURAL and DECODE_PORT:
        for i in range(core.components['Decode_port_data'].len):
            LeakageType('Decoding port {:d}'.format(i), 1)
            pass

        # Glitchy decoding register
        if GLITCHY_DECODE:
            for i in range(core.components['glitchy_Decode_port_data'].len):
                LeakageType('Glitchy decoding port {:d}'.format(i), 1)
                pass
            pass
        pass

    # ALU output
    LeakageType("ALU output", 0)

    # Memory subsystem
    if NON_ACTIVE_MEM:  # Read and Write valid check removed.
        # Memory address
        LeakageType("Memory address", 0)

        # Memory data
        LeakageType("Memory data", 0)

        # Memory write buffer
        LeakageType("Memory write buffer", 0)

        # Memory write buffer delayed
        LeakageType("Memory write buffer delayed", 0)

        # Memory read buffer
        LeakageType("Memory read buffer", 0)
        pass

    # Part 2: transitional leakage.
    # LSB neibouring effect
    if TRANSITION and LSB_NEIGHBOUR:
        # no PC, LR or SP
        i = 0
        while i < 13:
            LeakageType(
                "LSB Neighbouring Reg {:d} XOR Reg {:d}".format(i, i ^ 0x1), 1)
            i += 2
            pass
        pass

    # Target register HD
    if TRANSITION:  # reg[16]: linear
        for i in range(13):  # no PC, LR or SP
            LeakageType("Previous Reg {:d}".format(i), 1)
            pass

        for i in range(13):
            LeakageType("Reg {:d} HD".format(i), 1)
            pass
        pass

    if CPSR and TRANSITION:
        # CPSR, linear
        LeakageType("Previous CPSR", 1)
        LeakageType("CPSR HD", 1)
        pass

    # 2 pipeline registers, linear
    if MICROARCHITECTURAL and TRANSITION:
        LeakageType("Previous Pipeline Reg 1", 1)
        LeakageType("Previous Pipeline Reg 2", 1)
        LeakageType("Pipeline Reg 1 HD", 1)
        LeakageType("Pipeline Reg 2 HD", 1)
        pass

    # Decode
    # Decoding register access, linear
    if MICROARCHITECTURAL and DECODE_PORT and TRANSITION:
        for i in range(3):
            LeakageType("Previous Decoding port {:d}".format(i), 1)
            LeakageType("Decoding port {:d} HD".format(i), 1)
            pass

        # Glitchy
        if GLITCHY_DECODE:
            for i in range(3):
                LeakageType(
                    "Glitchy decoding port {:d} XOR current port {:d}".format(i, i), 1)
                LeakageType(
                    "Glitchy decoding port {:d} XOR previous port {:d}".format(i, i), 1)
            pass
        pass

    # Execute
    # Only ALU output, other captured by decode (pipeline register) or interaction (combinatorial)
    # ALU output, nominal
    if TRANSITION:
        LeakageType("Previous ALU output", 1)
        LeakageType("ALU output HD", 1)
        pass

    # Memory subsystem
    if TRANSITION and NON_ACTIVE_MEM:
        # Read, Write and delayed Write valid check removed
        # Memory address
        LeakageType("Previous Memory address", 0)
        LeakageType("Memory address HD", 1)

        # Memory data, nomial
        LeakageType("Previous Memory data", 0)
        LeakageType("Memory data HD", 1)

        # Memory write buffer, nomial
        LeakageType("Previous Memory write buffer", 0)
        LeakageType("Memory write buffer HD", 1)

        # Memory write buffer delayed, nomial
        LeakageType("Previous Memory write buffer delayed", 0)
        LeakageType("Memory write buffer delayed HD", 1)

        # Memory read buffer, nomial
        LeakageType("Previous Memory read buffer", 0)
        LeakageType("Memory read buffer HD", 1)
        pass

    # Part 3: interaction leakage.
    # Reg A * Reg B *prev_Reg A * prev_Reg B: Full
    if TRANSITION and MICROARCHITECTURAL:
        LeakageType("Reg A * Reg B * Previous Reg A * Previous Reg B", 0)
        pass

    print('#End of header')

    return


def InstExtractor(frame):
    print('#FrameNo: {}'.format(frame['FrameNo'][0]))

    if frame['core_valid'][0]:
        Generate_Leakage_Instr(frame)
        print('')
        pass
    else:
        print("Core invalid.")
        pass

    return


# Combine four unsigned int to a uint8_t array
def Combine4(a, b, c, d):
    # Init a None array.
    arr = bytearray()

    # Concatinate a b c d as bytes.
    arr += a.to_bytes(4, 'little')
    arr += b.to_bytes(4, 'little')
    arr += c.to_bytes(4, 'little')
    arr += d.to_bytes(4, 'little')

    return arr


# print out the instruction discription for current cycle
def Generate_Leakage_Instr(current):
    print("Pipeline:")

    print("E: {:s}\nD: {:s}\nM: {:s}".format(
        current['Execute_instr_disp'],
        current['Decode_instr_disp'],
        current['Memory_instr_disp']))

    return


# Part 1: select the components in each frame as leakage
# each component can be linear or nominal
# header==True--->write out the discription for header
# header==False --->write out leakage state data
def Generate_Leakage_Select(current):
    global outfile, traceno, frameno
    if NON_ACTIVE_REG:  # reg[16]: nominal
        for i in range(16):
            # Reg i -> Reg[i]
            (src, rec) = WriteLeakage(
                "Reg[{:d}]".format(i), current['reg'][i], current)
            outfile[traceno][frameno][src] = rec

        pass

    # CPSR, linear
    if CPSR:
        (src, rec) = WriteLeakage("CPSR", current['cpsr'][0], current)
        outfile[traceno][frameno][src] = rec
        pass

    # 2 pipeline registers, nominal
    if MICROARCHITECTURAL:
        # Pipeline Reg {1,2} -> PipeReg{1,2}
        (src, rec) = WriteLeakage("PipeReg1", current['D2E_reg1'][0], current)
        outfile[traceno][frameno][src] = rec
        (src, rec) = WriteLeakage("PipeReg2", current['D2E_reg2'][0], current)
        outfile[traceno][frameno][src] = rec

        pass

    # pipeline data bus (i.e. D.9 and 10) whether comes from decoding reg ports, or
    # forwarded from current ALUout/memory read output; therefore will be covered later

    # Fetch does not produce data-dependent leakage, ignore

    # Decode
    # Decoding register access, linear
    if MICROARCHITECTURAL and DECODE_PORT:
        for i in range(3):
            # Decoding port i -> DecodePort[i]
            (src, rec) = WriteLeakage("DecodePort[{:d}]".format(
                i), current['Decode_port_data'][i], current)
            outfile[traceno][frameno][src] = rec
        pass

    # Glitchy decoding register access, linear
    if MICROARCHITECTURAL and DECODE_PORT and GLITCHY_DECODE:
        for i in range(3):
            # Glitchy decoding port i -> GlitchyDecodePort[i]
            (src, rec) = WriteLeakage("GlitchyDecodePort[{:d}]".format(i),
                                      current['glitchy_Decode_port_data'][i], current)
            outfile[traceno][frameno][src] = rec
        pass

    # Execute
    # Only ALU output, other captured by decode (pipeline register) or interaction (combinatorial)
    # ALU output, nominal
    # ALU output -> ALU_output
    (src, rec) = WriteLeakage("ALU_output",
                              current['Execute_ALU_result'][0], current)
    outfile[traceno][frameno][src] = rec

    # Memory subsystem
    if NON_ACTIVE_MEM or (current['Read_valid'][0] == True) or (current['Write_valid'][0] == True):
        # Memory address, nomial
        # Memory address -> MemAddr
        (src, rec) = WriteLeakage("MemAddr",
                                  current['Memory_addr'][0], current)
        outfile[traceno][frameno][src] = rec

        # Memory data, nomial
        # Memory data -> MemData
        (src, rec) = WriteLeakage("MemData",
                                  current['Memory_data'][0], current)
        outfile[traceno][frameno][src] = rec

        # Memory write buffer, nomial
        # Memory write buffer -> MemWrBuf
        (src, rec) = WriteLeakage("MemWrBuf",
                                  current['Memory_writebuf'][0], current)
        outfile[traceno][frameno][src] = rec

        # Memory write buffer delayed, nomial
        # Memory write buffer delayed -> MemWrBufDelayed
        (src, rec) = WriteLeakage("MemWrBufDelayed",
                                  current['Memory_writebuf_delayed'][0], current)
        outfile[traceno][frameno][src] = rec

        # Memory read buffer, nomial
        # Memory read buffer -> MemRdBuf
        (src, rec) = WriteLeakage("MemRdBuf",
                                  current['Memory_readbuf'][0], current)
        outfile[traceno][frameno][src] = rec
        pass

    return


# Part 2: select the components in each frame that produce transition leakage
# each component can be linear or nominal (i.e. combining two nominal state)

# header==False --->write out leakage state data
def Generate_Leakage_Transition(prev, current, header):
    # Paired LSB Neighbouring effect (detail in COCO paper)
    if TRANSITION and LSB_NEIGHBOUR:
        # no PC, LR or SP
        i = 0
        while i < 13:
            # LSB Neighbouring Reg i XOR Reg j -> Reg[i]^Reg[j]
            src = "Reg[{:d}]^Reg[{:d}]".format(i, i ^ 0x1)
            temp = current['reg'][i] ^ current['reg'][i ^ 0x1]

            expr = ExpandExpr(LEAKAGE_FUNC[2], current.components['reg'].symid[i],
                              current.components['reg'].symid[i ^ 0x1])
            (src, rec) = WriteLeakage(src, temp, expr=expr)
            outfile[traceno][frameno][src] = rec

            i += 2
            pass
        pass

    # Target register HD
    if TRANSITION:  # reg[16]: linear
        for i in range(13):  # no PC, LR or SP
            # Previous Reg i -> PrevReg[i]
            (src, rec) = WriteLeakage(
                "PrevReg[{:d}]".format(i), prev['reg'][i], prev)
            outfile[traceno][frameno][src] = rec
            pass

        for i in range(13):
            temp = prev['reg'][i] ^ current['reg'][i]
            expr = ExpandExpr(
                LEAKAGE_FUNC[2], prev.components['reg'].symid[i], current.components['reg'].symid[i])

            # Reg i HD -> HD_Reg[i]
            (src, rec) = WriteLeakage(
                "HD_Reg[{:d}]".format(i), temp, expr=expr)
            outfile[traceno][frameno][src] = rec
            pass
        pass

    if CPSR and TRANSITION:
        # CPSR, linear
        # Previous CPSR -> PrevCPSR
        (src, rec) = WriteLeakage("PrevCPSR", prev['cpsr'][0], prev)
        outfile[traceno][frameno][src] = rec

        # CPSR HD -> HD_CPSR
        temp = prev['cpsr'][0] ^ current['cpsr'][0]
        expr = ExpandExpr(
            LEAKAGE_FUNC[2], prev.components['cpsr'].symid[0], current.components['cpsr'].symid[0])
        (src, rec) = WriteLeakage("HD_CPSR", temp, expr=expr)
        outfile[traceno][frameno][src] = rec
        pass

    # 2 pipeline registers, linear
    if MICROARCHITECTURAL and TRANSITION:
        # Previous Pipeine Reg {1,2} -> PrevPipeReg{1,2}
        (src, rec) = WriteLeakage("PrevPipeReg1", prev['D2E_reg1'][0], prev)
        outfile[traceno][frameno][src] = rec
        (src, rec) = WriteLeakage("PrevPipeReg2", prev['D2E_reg2'][0], prev)
        outfile[traceno][frameno][src] = rec

        # Pipeline Reg {1,2} HD -> HD_PipeReg{1,2}
        temp = prev['D2E_reg1'][0] ^ current['D2E_reg1'][0]
        expr = ExpandExpr(
            LEAKAGE_FUNC[2], prev.components['D2E_reg1'].symid[0], current.components['D2E_reg1'].symid[0])
        (src, rec) = WriteLeakage("HD_PipeReg1", temp, expr=expr)
        outfile[traceno][frameno][src] = rec

        temp = prev['D2E_reg2'][0] ^ current['D2E_reg2'][0]
        expr = ExpandExpr(
            LEAKAGE_FUNC[2], prev.components['D2E_reg2'].symid[0], current.components['D2E_reg2'].symid[0])
        (src, rec) = WriteLeakage("HD_PipeReg2", temp, expr=expr)
        outfile[traceno][frameno][src] = rec
        pass

    # Decode
    # Decoding register access, linear
    if MICROARCHITECTURAL and DECODE_PORT and TRANSITION:
        for i in range(3):
            # Previous Decodeing port i -> PrevDecodePort[i]
            (src, rec) = WriteLeakage("PrevDecodePort[{:d}]".format(i),
                                      prev['Decode_port_data'][i], prev)
            outfile[traceno][frameno][src] = rec

            # Decoding port i HD -> HD_DecodePort[i]
            temp = prev['Decode_port_data'][i] ^ current['Decode_port_data'][i]
            expr = ExpandExpr(LEAKAGE_FUNC[2], prev.components['Decode_port_data'].symid[i],
                              current.components['Decode_port_data'].symid[i])
            (src, rec) = WriteLeakage(
                "HD_DecodePort[{:d}]".format(i), temp, expr=expr)
            outfile[traceno][frameno][src] = rec
            pass
        pass

    # Glitchy decoding register access, linear
    if MICROARCHITECTURAL and DECODE_PORT and GLITCHY_DECODE and TRANSITION:
        for i in range(3):
            # Glitchy decoding port i XOR current port i -> HD_Glitchy_DecodePort[i]^DecodePort[i]
            temp = current['glitchy_Decode_port_data'][i] ^ current['Decode_port_data'][i]
            expr = ExpandExpr(LEAKAGE_FUNC[2], current.components['glitchy_Decode_port_data'].symid[i],
                              current.components['Decode_port_data'].symid[i])
            (src, rec) = WriteLeakage("GlitchyDecodePort[{:d}]^DecodePort{:d}".format(i, i),
                                      temp, expr=expr)
            outfile[traceno][frameno][src] = rec

            # Glitchy decoding port i XOR previous port i
            temp = current['glitchy_Decode_port_data'][i] ^ prev['Decode_port_data'][i]
            expr = ExpandExpr(
                LEAKAGE_FUNC[2], current.components['glitchy_Decode_port_data'].symid[i], prev.components['Decode_port_data'].symid[i])
            (src, rec) = WriteLeakage("GlitchyDecodePort[{:d}]^PrevDecodePort[{:d}]".format(i, i),
                                      temp, expr=expr)
            outfile[traceno][frameno][src] = rec
            pass
        pass

    # Execute
    # Only ALU output, other captured by decode (pipeline register) or interaction (combinatorial)
    # ALU output, nominal
    if TRANSITION:
        # Previous ALU output -> Prev_ALU_output
        (src, rec) = WriteLeakage("Prev_ALU_output",
                                  prev['Execute_ALU_result'][0], prev)
        outfile[traceno][frameno][src] = rec

        # ALU output HD -> HD_ALU_output
        temp = prev['Execute_ALU_result'][0] ^ current['Execute_ALU_result'][0]
        expr = ExpandExpr(LEAKAGE_FUNC[2], prev.components['Execute_ALU_result'].symid[0],
                          current.components['Execute_ALU_result'].symid[0])
        (src, rec) = WriteLeakage("HD_ALU_output", temp, expr=expr)
        outfile[traceno][frameno][src] = rec
        pass

    # Memory subsystem
    if TRANSITION and (NON_ACTIVE_MEM or (current['Read_valid'][0] == True) or (current['Write_valid'][0] == True) or (current['Write_valid_delayed'][0] == True)):
        # Memory address
        # Previous Memory address -> PrevMemAddr
        (src, rec) = WriteLeakage("PrevMemAddr", prev['Memory_addr'][0], prev)
        outfile[traceno][frameno][src] = rec

        # Memory address HD -> HD_MemAddr
        temp = prev['Memory_addr'][0] ^ current['Memory_addr'][0]
        expr = ExpandExpr(LEAKAGE_FUNC[2], prev.components['Memory_addr'].symid[0],
                          current.components['Memory_addr'].symid[0])
        (src, rec) = WriteLeakage("HD_MemAddr", temp, expr=expr)
        outfile[traceno][frameno][src] = rec

        # Memory data, nomial
        # Previous Memory data -> PrevMemData
        (src, rec) = WriteLeakage("PrevMemData", prev['Memory_data'][0], prev)
        outfile[traceno][frameno][src] = rec

        # Memory data HD -> HD_MemData
        temp = prev['Memory_data'][0] ^ current['Memory_data'][0]
        expr = ExpandExpr(LEAKAGE_FUNC[2], prev.components['Memory_data'].symid[0],
                          current.components['Memory_data'].symid[0])
        (src, rec) = WriteLeakage("HD_MemData", temp, expr=expr)
        outfile[traceno][frameno][src] = rec

        # Memory write buffer, nomial
        # Previous Memory write buffer -> PrevMemWrBuf
        (src, rec) = WriteLeakage(
            "PrevMemWrBuf", prev['Memory_writebuf'][0], prev)
        outfile[traceno][frameno][src] = rec

        # Memory write buffer HD -> HD_MemWrBuf
        temp = prev['Memory_writebuf'][0] ^ current['Memory_writebuf'][0]
        expr = ExpandExpr(LEAKAGE_FUNC[2], prev.components['Memory_writebuf'].symid[0],
                          current.components['Memory_writebuf'].symid[0])
        (src, rec) = WriteLeakage("HD_MemWrBuf", temp, expr=expr)
        outfile[traceno][frameno][src] = rec

        # Memory write buffer delayed, nomial
        # Previous Memory Write buffer delayed -> PrevMemWrBufDelayed
        (src, rec) = WriteLeakage("PrevMemWrBufDelayed",
                                  prev['Memory_writebuf_delayed'][0], prev)
        outfile[traceno][frameno][src] = rec

        # Memory write buffer delayed HD -> HD_MemWrBufDelayed
        temp = prev['Memory_writebuf_delayed'][0] ^ current['Memory_writebuf_delayed'][0]
        expr = ExpandExpr(LEAKAGE_FUNC[2], prev.components['Memory_writebuf_delayed'].symid[0],
                          current.components['Memory_writebuf_delayed'].symid[0])
        (src, rec) = WriteLeakage("HD_MemWrBufDelayed", temp, expr=expr)
        outfile[traceno][frameno][src] = rec

        # Memory read buffer, nomial
        # Previous Memory read buffer -> PrevMemRdBuf
        (src, rec) = WriteLeakage(
            "PrevMemRdBuf", prev['Memory_readbuf'][0], prev)
        outfile[traceno][frameno][src] = rec

        # Memory read buffer HD -> HD_MemRdBuf
        temp = current['Memory_readbuf'][0] ^ prev['Memory_readbuf'][0]
        expr = ExpandExpr(LEAKAGE_FUNC[2], prev.components['Memory_readbuf'].symid[0],
                          current.components['Memory_readbuf'].symid[0])
        (src, rec) = WriteLeakage("HD_MemRdBuf", temp, expr=expr)
        outfile[traceno][frameno][src] = rec
        pass

    return


# Part 3: select the components in each frame that produce interaction leakage
# all nominal
# header==True--->write out the discription for header
# header==False --->write out leakage state data
def Generate_Leakage_Interaction(prev, current):
    if TRANSITION and MICROARCHITECTURAL:
        combine = Combine4(
            current['D2E_reg1'][0], current['D2E_reg2'][0], prev['D2E_reg1'][0], prev['D2E_reg2'][0])

        # Reg A * Reg B *prev_Reg A * prev_Reg B: Full
        # Reg A * Reg B * Previous Reg A * Previous Reg B -> PipeReg1*PipeReg2*PrevPipeReg1*PrevPipeReg2
        expr = ExpandExpr(LEAKAGE_FUNC[3], current.components['D2E_reg1'].symid[0], current.components['D2E_reg2'].symid[0],
                          prev.components['D2E_reg1'].symid[0], prev.components['D2E_reg2'].symid[0])
        (src, rec) = WriteLeakage("PipeReg1*PipeReg2*PrevPipeReg1*PrevPipeReg2",
                                  combine, expr=expr)
        outfile[traceno][frameno][src] = rec
        pass

    return


def TestExtractorBody(frame):
    global outfile, traceno, frameno
    print('FrameNo: {}'.format(frame[1]['FrameNo'][0]))

    # Update traceno and frameno
    traceno = frame[1]["TraceNo"][0]
    frameno = frame[1]["FrameNo"][0]

    if traceno not in outfile:
        outfile[traceno] = dict()
        pass

    outfile[traceno][frameno] = dict()

    if frame[1]['core_valid'][0]:
        header = False
        # Generate_Leakage_Instr(frame[1], header)
        Generate_Leakage_Select(frame[1])
        Generate_Leakage_Transition(frame[0], frame[1], header)
        Generate_Leakage_Interaction(frame[0], frame[1])
        print('')
        pass
    else:
        print("Core invalid.")
        pass
    return


def main(argc, argv):
    global sol, symdict

    # Print help message.
    if 1 >= argc:
        PrintHelp()
        return 0
        pass

    testtrace = argv[1]
    core = seal.Core.Load('uelmo.json')
    trace = seal.Trace(core)
    trace.Open(testtrace)

    if argc >= 3:
        symdict = seal.EncodeDict()
        symdict.Import(argv[2])
        pass

    # uELMO leakage header.
    # UelmoHeader(core)
    # print('')

    # Instrctions of trace.
    # trace.Extract(InstExtractor)
    # trace.Reset()

    # TODO: First Frame skipped with windowsize of 2.
    # Data
    trace.Extract(TestExtractorBody, 2)

    # Save extraced leakage as a json file.
    outfilename = "{:s}.lkg.json".format(testtrace)
    json.dump(outfile, open(outfilename, 'w'), indent=2)
    print("#Extracted leakage saved as: {:s}".format(outfilename))

    return 0


if __name__ == '__main__':
    exit(main(len(sys.argv), sys.argv))
