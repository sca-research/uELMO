#!/usr/bin/python3

import os
import sys
import subprocess
import argparse
import shlex

# uELMO root folder.
uelmoroot = os.path.dirname(os.path.abspath(__file__))

# uELMO binary folder.
uelmosrc = uelmoroot + "/src/"

# Current working directory.
pwd = os.getcwd()


# Command line args parser.
def CmdArgs():
    parser = argparse.ArgumentParser('Script to run uELMO simulation.')

    parser.add_argument('TargetBin', help='Target binary.')
    parser.add_argument('-t', '--trace', help='Output trace file.')
    parser.add_argument(
        '-N', '--ntrace', help='Number of traces (Default = 1).')
    parser.add_argument('-c', '--client', help='Client executable.')
    parser.add_argument('-le', '--leakageextractor', help='Leakage extractor.')
    parser.add_argument('-lt', '--leakagetrace',
                        help='Extracted leakage trace.')
    parser.add_argument('-p', '--sealport', help='Use SEAL VirtulPort')

    args = parser.parse_args()

    return args


# Run uelmo without a script.
def RunSim(binfile, tracefile="/dev/null", N=1, client=None, port=None):
    global uelmosrc, pwd

    simret = True

    try:
        # Set working directory
        # print("#Switch to: {}".format(uelmosrc))
        os.chdir(uelmosrc)
        uelmocmd = ['./sealuelmo',
                    os.fspath(binfile), '-N', str(N), '--st', tracefile]

        if port is not None:  # Enable SEAL VirtualPort for uELMO.
            uelmocmd += ['--io', port]
            pass

        # No client.
        if client is None:
            print("#uelmo command = '{}'".format(uelmocmd))
            uelmoret = subprocess.run(uelmocmd)
            pass

        elif port is not None:  # Client with VirtualPort.
            # Start uELMO in uelmo/src.
            print("#uelmo command = '{}'".format(uelmocmd))
            puelmo = subprocess.Popen(uelmocmd)
            # Start client in current folder.
            os.chdir(pwd)
            print("#Client command = '{}'".format(client))
            pclient = subprocess.Popen(client)

            # Wait for procedures to end.
            pclient.wait()
            puelmo.wait()

            if puelmo.returncode != 0 or pclient.returncode != 0:
                simret = False
                pass
            else:
                print('#Simulation completed.')
                pass
            pass

        else:  # Client without VirtualPort. Connect via PIPE.
            # Start uELMO and client. Pipe their stdIO.
            print("#Piped command = '{client} | {uelmocmd}'".format(
                client=client, uelmocmd=uelmocmd))

            # Start uELMO in uelmo/src.
            puelmo = subprocess.Popen(uelmocmd, stdin=subprocess.PIPE)
            # Start client in current folder.
            os.chdir(pwd)
            pclient = subprocess.Popen(client, stdout=puelmo.stdin)

            pclient.wait()
            puelmo.wait()

            if puelmo.returncode != 0 or pclient.returncode != 0:
                simret = False
                pass
            else:
                print('#Simulation completed.')
                pass
            pass

    except Exception as e:
        print(e)
        simret = False
        raise e
        pass

    finally:
        os.chdir(pwd)
        pass

    return simret


# Extract leakage from uelmo trace.
def ExtractTrace(extractor, tracefile, outpath=None):
    global pwd
    if outpath is None:  # Use stdout if no output file specified.
        outfile = sys.stdout
        pass
    else:
        try:
            outfile = open(os.fspath(outpath), 'w')
        except Exception as e:
            print("#Error {}".format(e))
            outfile = sys.stdout
            pass
        pass

    try:
        # Change working folder to extractor.
        extractorwd = os.path.dirname(extractor)
        os.chdir(extractorwd)

        # Run extractor.
        extractorcmd = ['python3', os.fspath(extractor), os.fspath(tracefile)]

        print("#Extractor command = {}".format(extractorcmd))
        pextractor = subprocess.Popen(extractorcmd, stdout=outfile)
        pextractor.wait()
        pass
    finally:
        os.chdir(pwd)
        pass

    return


def main(argc, argv):
    global uelmoroot, uelmosrc

    # Default arguments.
    tracefile = os.path.abspath('/dev/null')  # Output trace file
    ntrace = 1   # Number of traces
    client = None  # Client executable
    extractor = None  # Leakage extractor
    leakagetrace = None  # Extracted leakage trace
    port = None  # SEAL VirtualPort

    # Parse command line args.
    args = CmdArgs()
    targetbin = os.path.abspath(args.TargetBin)  # Target binary
    print(targetbin)

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
        client = shlex.split(args.client)
        pass

    if args.sealport:
        port = args.sealport
        pass

    # Run uELMO simulation.
    if not RunSim(targetbin, tracefile=tracefile, N=ntrace, client=client, port=port):
        print('#Simulation error\n')
        return -1

    # Extract leakage.
    if extractor is not None:
        ExtractTrace(extractor, tracefile, leakagetrace)
        pass

    return 0


if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
