#!/usr/bin/python3
import sys
import seal

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


# Main function.
def main(argc, argv):
    # Initialise
    if len(argv) >= 1:
        TESTTRACE = argv[1]

    # Load core specifications and Seal trace file.
    core = seal.Core.Load(TESTCORE)
    st = seal.Trace(core)
    st.Open(TESTTRACE)
    count = 0

    # Output files.
    asmout = open('./asm.txt', 'w')     # Only assembly.
    infoout = open('./info.txt', 'w')   # Detailed execution trace.

    # Go through the whole trace.
    while True:
        # Get the next frame.
        frame = st.NextFrame()
        if not frame:
            break

        traceno = frame.components["TraceNo"].val[0]  # Trace No
        frameno = frame.components["FrameNo"].val[0]  # Frame No

        # Pipeline infomation.
        fetch = frame.components["Memory_instr_disp"].val.strip(
            'Memory: ').strip("\0")  # Disassembled instruction in the Execution pipe line.
        decode = frame.components["Decode_instr_disp"].val.strip(
            'Decode: ').strip("\0")  # Disassembled instruction in the Execution pipe line.
        execute = frame.components["Execute_instr_disp"].val.strip(
            'Execute: ').strip("\0")  # Disassembled instruction in the Execution pipe line.

        plinfo = "F:{:s}\nD:{:s}\nE:{:s}\n".format(fetch, decode, execute)



        detail = str()  # Detailed infomation to be parsed.

        # Parse each components into strings.
        for c in frame.components:
            detail += '\t' + ParseComponent(frame.components[c]) + '\n'
            pass
        info = "{:s}\n{:s}{:s}\n".format('{', detail, '}')

        # Write into the output files.
        #asmout.write("{:s}\n".format(asm))
        asmout.write("{:s}\n".format(plinfo))

        infoout.write("#{asm:s} ({tn}:{fn})\n{info:s}\n".format(
            asm=plinfo, info=info, tn=traceno, fn=frameno))
        count += 1
        pass

    return 0


# main() entry.
if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
