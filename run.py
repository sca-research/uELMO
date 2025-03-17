#!/usr/bin/python3

import os
import sys
import subprocess


# Run uelmo without a script.
def RunSim(binfile, tracefile="/dev/null", N=1, client=None):
    global uelmosrc

    # Store current pwd.
    pwd = os.getcwd()

    try:
        # Set working directory
        # print("#Switch to: {}".format(uelmosrc))
        os.chdir(uelmosrc)
        uelmocmd = "./sealuelmo {targetbin} -N {N} --st {tracefile}".format(
            targetbin=binfile, N=N, tracefile=tracefile)

        # Run uelmo without a client.
        if client == None:
            print("#Command = '{}'".format(uelmocmd))
            subprocess.run(uelmocmd.split())
            pass

        # Run uelmo with a client.
        else:
            # Start uELMO and client.
            print("#Command = '{client} | {uelmocmd}'".format(
                client=client, uelmocmd=uelmocmd))
            puelmo = subprocess.Popen(
                uelmocmd.split(), stdin=subprocess.PIPE)

            os.chdir(pwd)
            pclient = subprocess.Popen(
                client.split(), stdout=puelmo.stdin)

            pclient.wait()
            puelmo.wait()

            print('#Simulation completed.')
            pass

    finally:
        os.chdir(pwd)
        pass

    return


def main(argc, argv):
    global uelmoroot, uelmosrc

    # uELMO root folder.
    uelmoroot = os.path.dirname(os.path.abspath(argv[0]))

    # uELMO binary folder.
    uelmosrc = uelmoroot + "/src/"

    # Target binary.
    # tracebin = os.path.abspath(sys.argv[1])
    # targetbin = os.path.abspath("examples/ISW2/uelmo_gadget.bin")
    targetbin = os.path.abspath("examples/dilithium/main.bin")

    # Output trace file.
    # tracefile = os.path.abspath(TRACE_PATH)
    tracefile = os.path.abspath("/dev/null")

    # Number of trace.
    ntrace = 1

    # Client.
    client = None
    # clientscript = sys.argv[2]
    # client = os.path.abspath("./examples/dilithium/dist/nttclient/nttclient")
    client = "python3 ./examples/dilithium/nttclient.py"

    RunSim(targetbin, tracefile=tracefile, N=ntrace, client=client)

    return 0


if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
