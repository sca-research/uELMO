#!/usr/bin/python3
import sys

import smurf

FORCE_LINEAR = 0  # force all leakage to be linear

NON_ACTIVE_REG = 1  # Allows leakage for non-active registers
NON_ACTIVE_MEM = 1  # Allows leakage for non-active memory buses

MICROARCHITECTURAL = 1  # Allows leakage from the micro-architecture
CPSR = 1  # Allows leakage from the CPSR register
DECODE_PORT = 1  # Allows leakage from the decoding register access
GLITCHY_DECODE = 1  # Allows for glitchy decoding register access

TRANSITION = 1  # Allows for transition leakage
LSB_NEIGHBOUR = 1  # Allows for LSB based neibouring effect


# Hack of C sprintf
def sprintf(*args):
    formatstr = args[0]
    varargs = args[1:]
    retstr = args[0].format(*varargs)
    return retstr


# Hack of original output.
def Write_Instr(disp):
    print("Instr:", disp)
    return


def Write_leakage_label(disp, ltype):
    print("Label: {:d} {:s}".format(ltype, disp))
    return


def Write_leakage_data(data, dlen, dtype):
    print("{:d}[{:d}]: {}".format(dtype, dlen, data))
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
def Generate_Leakage_Instr(current, header):
    if header:
        disp = sprintf("{:s}\n{:s}\n{:s}\n", current['Execute_instr_disp'],
                       current['Decode_instr_disp'], current['Memory_instr_disp'])
        Write_Instr(disp)
        pass

    return


# Part 1: select the components in each frame as leakage
# each component can be linear or nominal
# header==True--->write out the discription for header
# header==False --->write out leakage state data
def Generate_Leakage_Select(current, header):
    if NON_ACTIVE_REG:  # reg[16]: nominal
        for i in range(16):
            if header:
                disp = sprintf("Reg {:d}", i)
                Write_leakage_label(disp, 0)
                pass
            else:
                Write_leakage_data(current['reg'][i], 32, 0)
                pass
            pass
        pass

    # CPSR, linear
    if CPSR:
        if header:
            Write_leakage_label("CPSR", 1)
            pass
        else:
            Write_leakage_data(current['cpsr'][0], 32, 1)
            pass
        pass

    # 2 pipeline registers, nominal
    if MICROARCHITECTURAL:
        if header:
            Write_leakage_label("Pipeline Reg 1", 0)
            pass
        else:
            Write_leakage_data(current['D2E_reg1'][0], 32, 0)
            pass

        if header:
            Write_leakage_label("Pipeline Reg 2", 0)
            pass
        else:
            Write_leakage_data(current['D2E_reg2'][0], 32, 0)
            pass
        pass

    # pipeline data bus (i.e. D.9 and 10) whether comes from decoding reg ports, or
    # forwarded from current ALUout/memory read output; therefore will be covered later

    # Fetch does not produce data-dependent leakage, ignore

    # Decode
    # Decoding register access, linear
    if MICROARCHITECTURAL and DECODE_PORT:
        for i in range(3):
            if header:
                disp = sprintf("Decoding port {:d}", i)
                Write_leakage_label(disp, 1)
                pass
            else:
                Write_leakage_data(current['Decode_port_data'][i], 32, 1)
                pass
        pass

    # Glitchy decoding register access, linear
    if MICROARCHITECTURAL and DECODE_PORT and GLITCHY_DECODE:
        for i in range(3):
            if header:
                disp = sprintf("Glitchy decoding port {:d}", i)
                Write_leakage_label(disp, 1)
                pass
            else:
                Write_leakage_data(
                    current['glitchy_Decode_port_data'][i], 32, 1)
                pass
            pass
        pass

    # Execute
    # Only ALU output, other captured by decode (pipeline register) or interaction (combinatorial)
    # ALU output, nominal
    if header:
        Write_leakage_label("ALU output", 0)
        pass
    else:
        Write_leakage_data(current['Execute_ALU_result'][0], 32, 0)
        pass

    # Memory subsystem
    if NON_ACTIVE_MEM or (current['Read_valid'][0] == True) or (current['Write_valid'][0] == True):
        # Memory address, nomial
        if header:
            Write_leakage_label("Memory address", 0)
            pass
        else:
            Write_leakage_data(current['Memory_addr'][0], 32, 0)
            pass

        # Memory data, nomial
        if header:
            Write_leakage_label("Memory data", 0)
            pass
        else:
            Write_leakage_data(current['Memory_data'], 32, 0)
            pass

        # Memory write buffer, nomial
        if header:
            Write_leakage_label("Memory write buffer", 0)
            pass
        else:
            Write_leakage_data(current['Memory_writebuf'][0], 32, 0)
            pass

        # Memory write buffer delayed, nomial
        if header:
            Write_leakage_label("Memory write buffer delayed", 0)
        else:
            Write_leakage_data(current['Memory_writebuf_delayed'][0], 32, 0)
            pass

        # Memory read buffer, nomial
        if header:
            Write_leakage_label("Memory read buffer", 0)
            pass
        else:
            Write_leakage_data(current['Memory_readbuf'],  32, 0)
            pass
        pass

    return


# Part 2: select the components in each frame that produce transition leakage
# each component can be linear or nominal (i.e. combining two nominal state)
# header==True--->write out the discription for header
# header==False --->write out leakage state data
def Generate_Leakage_Transition(prev, current, header):
    # LSB Neighbouring effect
    if TRANSITION and LSB_NEIGHBOUR:
        # no PC, LR or SP
        i = 0
        while i < 13:
            if header:
                disp = sprintf(
                    disp, "LSB Neighbouring Reg {:d} XOR Reg {:d}", i, i ^ 0x1)
                Write_leakage_label(disp, 1)
                pass
            else:
                temp = current['reg'][i] ^ current['reg'][i ^ 0x1]
                Write_leakage_data(temp, 32, 1)
                pass

            i += 2
            pass
        pass

    # Target register HD
    if TRANSITION:  # reg[16]: linear
        for i in range(13):  # no PC, LR or SP
            if header:
                disp = sprintf("Previous Reg {:d}", i)
                Write_leakage_label(disp, 1)
                pass
            else:
                Write_leakage_data(prev['reg'][i], 32, 1)
                pass
            pass

        for i in range(13):
            if header:
                disp = sprintf("Reg {:d} HD", i)
                Write_leakage_label(disp, 1)
                pass
            else:
                temp = prev['reg'][i] ^ current['reg'][i]
                Write_leakage_data(temp, 32, 1)
                pass
            pass
        pass

    if CPSR and TRANSITION:
        #CPSR, linear
        if header:
            Write_leakage_label("Previous CPSR", 1)
            pass
        else:
            Write_leakage_data(prev['cpsr'][0], 32, 1)
            pass

        if header:
            Write_leakage_label("CPSR HD", 1)
            pass
        else:
            temp = prev['cpsr'][0] ^ current['cpsr'][0]
            Write_leakage_data(temp, 32, 1)
            pass
        pass

    # 2 pipeline registers, linear
    if MICROARCHITECTURAL and TRANSITION:
        if header:
            Write_leakage_label("Previous Pipeline Reg 1", 1)
            pass
        else:
            Write_leakage_data(prev['D2E_reg1'][0], 32, 1)
            pass

        if header:
            Write_leakage_label("Previous Pipeline Reg 2", 1)
            pass
        else:
            Write_leakage_data(prev['D2E_reg2'][0], 32, 1)
            pass

        if header:
            Write_leakage_label("Pipeline Reg 1 HD", 1)
            pass
        else:
            temp = prev['D2E_reg1'][0] ^ current['D2E_reg1'][0]
            Write_leakage_data(temp, 32, 1)
            pass

        if header:
            Write_leakage_label("Pipeline Reg 2 HD", 1)
            pass
        else:
            temp = prev['D2E_reg2'][0] ^ current['D2E_reg2'][0]
            Write_leakage_data(temp, 32, 1)
            pass
        pass

    # Decode
    # Decoding register access, linear
    if MICROARCHITECTURAL and DECODE_PORT and TRANSITION:
        for i in range(3):
            if header:
                disp = sprintf("Previous Decoding port {:d}", i)
                Write_leakage_label(disp, 1)
                pass
            else:
                Write_leakage_data(prev['Decode_port_data'][i], 32, 1)
                pass

            if header:
                disp = sprintf("Decoding port {:d} HD", i)
                Write_leakage_label(disp, 1)
                pass
            else:
                temp = prev['Decode_port_data'][i] ^ current['Decode_port_data'][i]
                Write_leakage_data(temp, 32, 1)
                pass
            pass
        pass

    # Glitchy decoding register access, linear
    if MICROARCHITECTURAL and DECODE_PORT and GLITCHY_DECODE and TRANSITION:
        for i in range(3):
            if header:
                disp = sprintf(
                    "Glitchy decoding port {:d} XOR current port {:d}", i, i)
                Write_leakage_label(disp, 1)
                pass
            else:
                temp = current['glitchy_Decode_port_data'][i] ^ current['Decode_port_data'][i]
                Write_leakage_data(temp, 32, 1)
                pass

            if header:
                disp = sprintf(
                    "Glitchy decoding port {:d} XOR previous port {:d}", i, i)
                Write_leakage_label(disp, 1)
                pass
            else:
                temp = current['glitchy_Decode_port_data'][i] ^ prev['Decode_port_data'][i]
                Write_leakage_data(temp, 32, 1)
                pass
            pass
        pass

    # Execute
    # Only ALU output, other captured by decode (pipeline register) or interaction (combinatorial)
    # ALU output, nominal
    if TRANSITION:
        if header:
            Write_leakage_label("Previous ALU output", 1)
            pass
        else:
            Write_leakage_data(prev['Execute_ALU_result'][0], 32, 1)
            pass

        if header:
            Write_leakage_label("ALU output HD", 1)
            pass
        else:
            temp = prev['Execute_ALU_result'][0] ^ current['Execute_ALU_result'][0]
            Write_leakage_data(temp, 32, 1)
            pass
        pass

    # Memory subsystem
    if TRANSITION and (NON_ACTIVE_MEM or (current['Read_valid'][0] == True) or (current['Write_valid'][0] == True) or (current['Write_valid_delayed'][0] == True)):
        # Memory address
        if header:
            Write_leakage_label("Previous Memory address", 0)
            pass
        else:
            Write_leakage_data(prev['Memory_addr'][0], 32, 0)
            pass

        if header:
            Write_leakage_label("Memory address HD", 1)
            pass
        else:
            temp = prev['Memory_addr'][0] ^ current['Memory_addr'][0]
            Write_leakage_data(temp, 32, 1)
            pass

        # Memory data, nomial
        if header:
            Write_leakage_label("Previous Memory data", 0)
            pass
        else:
            Write_leakage_data(prev['Memory_data'][0], 32, 0)
            pass

        if header:
            Write_leakage_label("Memory data HD", 1)
            pass
        else:
            temp = prev['Memory_data'][0] ^ current['Memory_data'][0]
            Write_leakage_data(temp, 32, 1)
            pass

        # Memory write buffer, nomial
        if header:
            Write_leakage_label("Previous Memory write buffer", 0)
            pass
        else:
            Write_leakage_data(prev['Memory_writebuf'][0], 32, 0)
            pass

        if header:
            Write_leakage_label("Memory write buffer HD", 1)
            pass
        else:
            temp = prev['Memory_writebuf'][0] ^ current['Memory_writebuf'][0]
            Write_leakage_data(temp, 32, 1)
            pass

        # Memory write buffer delayed, nomial
        if header:
            Write_leakage_label("Previous Memory write buffer delayed", 0)
            pass
        else:
            Write_leakage_data(prev['Memory_writebuf_delayed'][0], 32, 0)
            pass

        if header:
            Write_leakage_label("Memory write buffer delayed HD", 1)
            pass
        else:
            temp = prev['Memory_writebuf_delayed'][0] ^ current['Memory_writebuf_delayed'][0]
            Write_leakage_data(temp, 32, 1)
            pass

        # Memory read buffer, nomial
        if header:
            Write_leakage_label("Previous Memory read buffer", 0)
            pass
        else:
            Write_leakage_data(prev['Memory_readbuf'][0], 32, 0)
            pass

        if header:
            Write_leakage_label("Memory read buffer HD", 1)
            pass
        else:
            temp = current['Memory_readbuf'][0] ^ prev['Memory_readbuf'][0]
            Write_leakage_data(temp, 32, 1)
            pass

        pass
    return


# Part 3: select the components in each frame that produce interaction leakage
# all nominal
# header==True--->write out the discription for header
# header==False --->write out leakage state data
def Generate_Leakage_Interaction(prev, current, header):
    if TRANSITION and MICROARCHITECTURAL:
        if header:
            # Reg A * Reg B *prev_Reg A * prev_Reg B: Full
            Write_leakage_label(
                "Reg A * Reg B * Previous Reg A * Previous Reg B", 0)
            pass

        else:
            combine = Combine4(
                current['D2E_reg1'][0], current['D2E_reg2'][0], prev['D2E_reg1'][0], prev['D2E_reg2'][0])

            # Reg A * Reg B *prev_Reg A * prev_Reg B: Full
            Write_leakage_data(combine, 4 * 32, 0)
            pass
        pass

    return


def TestExtractor(frame):
    header = False
    print('FrameNo: {}'.format(frame[1]['FrameNo'][0]))
    Generate_Leakage_Instr(frame[1], header)
    Generate_Leakage_Select(frame[1], header)
    Generate_Leakage_Transition(frame[0], frame[1], header)
    Generate_Leakage_Interaction(frame[0], frame[1], header)
    print('')
    return


def main(argc, argv):
    testtrace = argv[1]
    core = smurf.Core.Load('uelmo.json')
    trace = smurf.Trace(core)
    trace.Open(testtrace)
    trace.Extract(TestExtractor, 2)
    return


if __name__ == '__main__':
    exit(main(len(sys.argv), sys.argv))
