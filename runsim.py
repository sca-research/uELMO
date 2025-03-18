#!/usr/bin/python3

import os
import sys
import subprocess
import argparse


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
            # Start uELMO and client. Pipe their stdIO.
            print("#Command = '{client} | {uelmocmd}'".format(
                client=client, uelmocmd=uelmocmd))

            puelmo = subprocess.Popen(uelmocmd.split(), stdin=subprocess.PIPE)

            os.chdir(pwd)
            pclient = subprocess.Popen(client.split(), stdout=puelmo.stdin)

            pclient.wait()
            puelmo.wait()

            print('#Simulation completed.')
            pass

    finally:
        os.chdir(pwd)
        pass

    return


def CmdArgs():
    parser = argparse.ArgumentParser('Script to run uELMO simulation.')

    parser.add_argument('TargetBin', help='Target binary.')
    parser.add_argument('-t', '--trace', help='Specify output trace file.')
    parser.add_argument('-N', '--ntrace', help='Number of traces.')
    parser.add_argument('-c', '--client', help='Specify client executable.')

    args = parser.parse_args()

    return args


def main(argc, argv):
    global uelmoroot, uelmosrc

    # Default
    tracefile = os.path.abspath('/dev/null')  # Output trace file
    ntrace = 1   # Number of traces
    client = None  # Client executable

    # Parse command line args.
    args = CmdArgs()
    targetbin = os.path.abspath(args.TargetBin)  # Target binary

    if args.trace:
        tracefile = os.path.abspath(args.trace)
        pass

    if args.ntrace:
        ntrace = args.ntrace
        pass

    if args.client:
        client = args.client
        pass

    # uELMO root folder.
    uelmoroot = os.path.dirname(os.path.abspath(argv[0]))

    # uELMO binary folder.
    uelmosrc = uelmoroot + "/src/"

    # Run uELMO simulation.
    RunSim(targetbin, tracefile=tracefile, N=ntrace, client=client)

    return 0


if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
