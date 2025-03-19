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


# Extract leakage from uelmo trace.
def ExtractTrace(extractor, tracefile, outpath=None):
    pwd = os.getcwd()
    if outpath is None:  # Use stdout if no output file specified.
        outfile = sys.stdout
        pass
    else:
        try:
            outfile = open(outpath, 'w')
        except Exception as e:
            print("Error {}".format(e))
            outfile = sys.stdout
            pass
        pass

    try:
        # Change working folder to extractor.
        extractorwd = os.path.dirname(extractor)
        os.chdir(extractorwd)

        # Run extractor.
        cmd = "python3 {extractor} {tracefile}".format(
            extractor=extractor, tracefile=tracefile)
        print("Command = {}".format(cmd))
        pextractor = subprocess.Popen(cmd.split(), stdout=outfile)
        pextractor.wait()
        pass
    finally:
        os.chdir(pwd)
        pass

    return


# Command line args parser.
def CmdArgs():
    parser = argparse.ArgumentParser('Script to run uELMO simulation.')

    parser.add_argument('TargetBin', help='Target binary.')
    parser.add_argument('-t', '--trace', help='Output trace file.')
    parser.add_argument('-N', '--ntrace', help='Number of traces.')
    parser.add_argument('-c', '--client', help='Client executable.')
    parser.add_argument('-le', '--leakageextractor', help='Leakage extractor.')
    parser.add_argument('-lt', '--leakagetrace',
                        help='Extracted leakage trace.')

    args = parser.parse_args()

    return args


def main(argc, argv):
    global uelmoroot, uelmosrc

    # uELMO root folder.
    uelmoroot = os.path.dirname(os.path.abspath(__file__))

    # uELMO binary folder.
    uelmosrc = uelmoroot + "/src/"

    # Default arguments.
    tracefile = os.path.abspath('/dev/null')  # Output trace file
    ntrace = 1   # Number of traces
    client = None  # Client executable
    extractor = None  # Leakage extractor
    leakagetrace = None  # Extracted leakage trace

    # Parse command line args.
    args = CmdArgs()
    targetbin = os.path.abspath(args.TargetBin)  # Target binary

    if args.trace:
        tracefile = os.path.abspath(args.trace)
        if args.leakageextractor:
            extractor = os.path.abspath(args.leakageextractor)

            if args.leakagetrace:
                leakagetrace = os.path.abspath(args.leakagetrace)
                pass

            pass

        pass

    if args.ntrace:
        ntrace = args.ntrace
        pass

    if args.client:
        client = args.client
        pass

    # Run uELMO simulation.
    RunSim(targetbin, tracefile=tracefile, N=ntrace, client=client)

    # Extract leakage.
    if extractor is not None:
        ExtractTrace(extractor, tracefile, leakagetrace)
        pass

    return 0


if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
