#!/usr/bin/python3

import sys
import json


NO_SYM = 'NO_SYMBOL'


def PrintHelp():
    print("Usage:")
    print("\tpython3 printlkg.py {EXTRACTED_LEAKAGE_TRACE}")
    return

# Print leakage of a source.


def PrintLeakage(name, leakage):
    global NO_SYM
    sym = leakage['sym']

    # Ignore sources without an expression.
    if sym == NO_SYM:
        # print("Skipped {}".format(name))
        return
        pass

    # Print leakages
    print("{:50s} {:s}".format(name+':', sym))

    return


def main(argc, argv):
    if argc < 2:
        PrintHelp()
        return 0

    lkgfile = argv[1]

    # Load JSON leakage file.
    lkg = json.load(open(lkgfile, 'r'))

    # Loop over all traces.
    for traceno in lkg:  # First dimension: TraceNo.
        # Loop over all Frames.
        for frameno in lkg[traceno]:  # Second dimension: FrameNo
            print("#Trace {}, Frame {}".format(traceno, frameno))
            # Loop over all sources.
            for srcname in lkg[traceno][frameno]:
                leakage = lkg[traceno][frameno][srcname]
                PrintLeakage(srcname, leakage)
                pass
            print("#End of Trace {}, Frame {}\n".format(traceno, frameno))
            pass

        pass

    return 0


if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
