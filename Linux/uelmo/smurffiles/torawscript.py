#!/usr/bin/python3
import sys
import smurf

TESTCORE = "uelmo.json"
TESTTRACE = None
ASM_OUT = None
INFO_OUT = None

# Print help message.


def PrintHelp():
    print("Usage:\n\tpython3 {} TRACE_FILE".format(sys.argv[0]))
    return

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
        compval = "\'" + comp.val.strip("\0") + "\'"
        pass

    elif comp.type in {'INT16', 'UINT16'}:
        for i in range(comp.len):
            compval += "{v:04X}({v:d}) ".format(v=comp.val[i])
            pass
    elif comp.type in {'INT32', 'UINT32'}:
        for i in range(comp.len):
            compval += "{v:08X} ".format(v=comp.val[i])
            pass
    else:
        raise("Unknown Component type")

    return "{n}{sep}{t}{sep}{l} = {v}".format(n=compname, t=comptype, l=complen, v=compval.strip(" "), sep=seperator)


# Main function.
def main(argc, argv):
    # Initialise
    if argc < 2 or '-h' in argv:
        PrintHelp()
        exit(0)
        pass

    # Set file names
    TESTTRACE = argv[1]
    ASM_OUT = "{}.asm".format(TESTTRACE)
    INFO_OUT = "{}.info".format(TESTTRACE)

    # Load core specifications and Smurf trace file.
    core = smurf.Core.Load(TESTCORE)
    st = smurf.Trace(core)
    st.Open(TESTTRACE)
    count = 0

    # Output files.
    asmout = open(ASM_OUT, 'w')     # Only assembly.
    infoout = open(INFO_OUT, 'w')   # Detailed execution trace.

    # Go through the whole trace.
    while True:
        # Get the next frame.
        frame = st.NextFrame()
        if not frame:
            break

        traceno = frame.components["TraceNo"].val[0]  # Trace No
        frameno = frame.components["FrameNo"].val[0]  # Frame No
        # Disassembled instruction in the Execution pipe line.
        asm = frame.components["Execute_instr_disp"].val.replace(
            'Execute: ', '').strip("\0")
        detail = str()  # Detailed infomation to be parsed.

        # Parse each components into strings.
        for c in frame.components:
            detail += '\t' + ParseComponent(frame.components[c]) + '\n'
            pass
        info = "{:s}\n{:s}{:s}\n".format('{', detail, '}')

        # Write into the output files.
        asmout.write("{:20s} \t//{:}:{:}\n\n".format(asm, traceno, frameno))
        infoout.write("#{asm:s} //{tn}:{fn}\n{info:s}\n".format(
            asm=asm, info=info, tn=traceno, fn=frameno))
        count += 1
        pass

    print("Output generated:")
    print("ASM: {}".format(ASM_OUT))
    print("Info: {}".format(INFO_OUT))

    return 0


# main() entry.
if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
