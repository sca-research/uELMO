#!/usr/bin/python3
import sys
import smurf

uelmocore = "uelmo.json"
tracefile = None
VERBOSE = False


def PrintComponent(comp):
    print("{:<32s}|{:<8s}|{:3d}| = ".format(
        comp.name, comp.type, comp.len, comp.val), end='')

    # Skip raw bytes output for non OCTET components.
    if VERBOSE or comp.type == 'OCTET':
        print('[', end='')
        for i in range(len(comp.raw)):
            print("{:02X} ".format(comp.raw[i]), end='')
        print(']', end='')
        pass

    elif comp.type == 'STRING':
        print("\"{:s}\" ".format(str(comp.val).strip('\0')), end='')
        pass

    else:
        print('[', end='')
        if comp.type == 'BOOL':
            for i in range(comp.len):
                if comp.val[i]:
                    print('T ', end='')
                    pass
                else:
                    print('F ', end='')
                    pass
                pass
            pass
        elif comp.type in {'INT16', 'UINT16', 'INT32', 'UINT32'}:
            for i in range(comp.len):
                print("{:02X} ".format(comp.val[i]), end='')
                if i != len(comp.val) - 1:
                    print(',', end='')
        else:
            raise("Unknown Component type")
        print("] ", end='')
        pass

    print("~", comp.symid, end='')

    print('')
    return


def main(argc, argv):
    if len(argv) >= 1:
        tracefile = argv[1]
        pass

    # Verbose flag
    if '-v' in argv:
        VERBOSE = True
        pass

    core = smurf.Core.Load(uelmocore)
    st = smurf.Trace(core)
    st.Open(tracefile)
    count = 0
    while True:
        frame = st.NextFrame()
        if frame is None:
            break
        print("======= FRAME {:02} =======".format(count))
        for i in frame.components:
            PrintComponent(frame.components[i])
            pass
        count += 1
        print("========********========\n")

    return


if __name__ == '__main__':
    exit(main(len(sys.argv), sys.argv))
