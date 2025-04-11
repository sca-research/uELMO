#!/usr/bin/python3
import sys
import os
import argparse
import tempfile
import shutil
import numpy as np
import shlex
# import scalib

import runsim


# Parse command line arguments.
def ParseArgs():
    parser = argparse.ArgumentParser('Script to run TVLA')
    parser.add_argument('TargetBin', help='Target Binary')
    parser.add_argument('-f', '--fixed',
                        help='Client for fixed input.')
    parser.add_argument('-r', '--random',
                        help='Client for random input.')
    parser.add_argument('-le', '--leakageextractor', help='Leakage extractor.')
    parser.add_argument('-n', '--ntrace', default=1,
                        type=int, help='Number of trace')
    parser.add_argument('-p', '--port', help='Seal Virtualport.')
    parser.add_argument('-d', '--dir', help='Directory for the output.')

    args = parser.parse_args()
    return args


# Sort traces into a matrix of (#Number of traces, #Number of points).
def SortTrace(T):
    # Get number of traces.
    nt = int(max(T[:, 0])) + 1

    # Get number of Frames.
    nf = int(max(T[:, 1])) + 1

    # Sort by TraceNo and remove FrameNo
    T_sorted = np.zeros([nt, nf])

    for i in range(nt):
        mask = T[:, 0] == i
        x = T[mask][:, 2]
        padwidth = nf - len(x)
        x = np.pad(x, (0, padwidth), mode='constant', constant_values=0)
        T_sorted[i] = x
        pass

    return T_sorted


# Run t-test of fixed and random traces.
def Test(fixed, random):

    return


def main(argc, argv):
    args = ParseArgs()

    targetbin = os.path.abspath(args.TargetBin)

    if args.fixed is None:
        print("#Command for fixed client:")
        fixedclient = shlex.split(sys.stdin.readline())
        pass
    else:
        fixedclient = shlex.split(args.fixed)
        pass

    if args.random is None:
        print("#Command for random client:")
        randomclient = shlex.split(sys.stdin.readline())
        pass
    else:
        randomclient = shlex.split(args.random)
        pass

    if args.dir is None:
        outdir = os.path.abspath(os.getcwd()+'/tvla')
        pass
    else:
        outdir = os.path.abspath(args.dir)
        pass

    if args.leakageextractor is None:
        print("#Leakage Extractor:")
        extractor = os.path.abspath(sys.stdin.readline())
        pass
    else:
        extractor = os.path.abspath(args.leakageextractor)
        pass

    ntrace = args.ntrace
    port = args.port

    # Output files.
    # Execution Traces.
    fixedet = os.path.abspath(outdir + '/fixed.et')
    randomet = os.path.abspath(outdir + '/random.et')
    # Leakage Traces.
    fixedlt = os.path.abspath(outdir + '/fixed.lt')
    randomlt = os.path.abspath(outdir + '/random.lt')

    # Set up output folder.
    try:
        os.mkdir(outdir)
    except FileExistsError:
        print("#Folder exists. Remake.")
        shutil.rmtree(outdir)
        os.mkdir(outdir)
        pass

    # Generate Execution Traces.
    runsim.RunSim(targetbin, tracefile=fixedet, client=fixedclient, port=port)
    runsim.RunSim(targetbin, tracefile=randomet,
                  client=randomclient, port=port)

    # Extract leakages.
    runsim.ExtractTrace(extractor, fixedet, fixedlt)
    runsim.ExtractTrace(extractor, randomet, randomlt)

    # Load extracted leakages.
    fixedraw = np.loadtxt(fixedlt, delimiter=',').astype(np.int64)
    randomraw = np.loadtxt(randomlt, delimiter=',').astype(np.int64)

    # Sort the traces and save as csv files.
    fixedtrace = SortTrace(fixedraw)
    randomtrace = SortTrace(randomraw)

    np.savetxt(outdir+'/fixed.csv', fixedtrace, fmt="%d")
    np.savetxt(outdir+'/random.csv', randomtrace, fmt="%d")

    # TODO: use SCALib to perform t-test over fixedtrace and randomtrace
    testresult = Test(fixedtrace, randomtrace)
    print(testresult)

    return 0


if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
