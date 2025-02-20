#!/usr/bin/python3

import os
import sys
import time
import seal

N = 256
N_TRIAL = 10

# Zero matrix.
ZERO_MATRIX = [0 for i in range(N)]


# Encode an i32 to 4 bytes.
def I32ToBytes(i32):
    b = i32.to_bytes(4, 'big')
    return [i.to_bytes(1, 'big') for i in b]


# Encode a NTT input matrix into bytes.
def MtxToBytes(mtx):
    m = list()
    for e in mtx:
        m += I32ToBytes(e)
        pass
    return m


# Write NTT input matrix to stdin.
def WriteMtx(mtx):
    mtx_b = MtxToBytes(mtx)
    for b in mtx_b:
        os.write(1, b)
        pass
    return


def main(argc, argv):
    i = 0

    while True:
        if i >= N_TRIAL:
            WriteMtx(ZERO_MATRIX)
            time.sleep(1)
            break
            pass
        else:
            m = [0x1234abcd for i in range(N)]
            WriteMtx(m)
            pass

        i += 1

        time.sleep(1)
        pass

    return 0


if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
