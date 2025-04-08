import sys
import seal
import random
import time
import argparse


SEAL_PORT = None
TERMINATOR = 'exit\n'

# Controlling commands.
CMD_RESERVED = bytes([0x00])
CMD_SET_KEY = bytes([0x01])
CMD_ENCRYPT = bytes([0x02])
CMD_EXIT = bytes([0x03])

# SealPort
port = None

# Number of traces
ntrace = 1

# Flags
userandom = False
usetestvector = False


def Args():
    parser = argparse.ArgumentParser('Masked AES client')

    parser.add_argument('-n', '--ntrace', help='Number of Trace')
    parser.add_argument('-p', '--port', help='Path to SealVirtualPort')
    parser.add_argument(
        '-r', '--random', help='Use random input', action='store_true')
    parser.add_argument(
        '--testvector', help='Use AES test vector', action='store_true')

    return parser.parse_args()


def Getchar():
    global port

    if port == None:
        c = sys.stdin.buffer.read(1)
        pass
    else:
        c = port.Getchar()
        pass

    return c


def ToByte(x) -> bytes:
    if isinstance(x, bytes) or isinstance(x, bytearray):
        return x[:1]
    elif isinstance(x, int):
        return x.to_bytes()

    elif isinstance(x, str):
        return x.encode('ascii')[:1]
    else:
        raise TypeError()
        pass

    return


def Putchar(c):
    global port

    if port == None:
        sys.stdout.buffer.write(ToByte(c))
        pass
    else:
        port.Putchar(c)
        pass

    return


# Read a line from port.
def ReadLine(port):
    line = bytes([])
    while True:
        b = Getchar()
        line += b
        if b == ('\n').encode('ascii'):
            break
            pass

        pass

    return line.decode('ascii')


# Generate an AES key.
def GenKey():
    global usetestvector, userandom
    if usetestvector:
        key = bytes([i for i in range(16)])
        pass
    elif userandom:
        key = random.randbytes(16)
        pass
    else:
        key = bytes([i for i in range(16)])
        pass
    return key


# Set encryption key.
def SetKey(port, key):
    # Command
    print("# Command = {}".format(CMD_SET_KEY))
    Putchar(CMD_SET_KEY)

    # Send key
    for i in range(16):
        Putchar(key[i])
        pass

    ack = ReadLine(port)
    print('(uelmo)', ack, end='')

    return


# Generate inputs for Masked AES
def GenInput():
    global usetestvector
    if usetestvector:
        p = 0x00112233445566778899aabbccddeeff.to_bytes(
            length=16, byteorder='big')
        pass
    else:
        p = random.randbytes(16)
        pass

    u = random.randbytes(1)
    v = random.randbytes(1)

    return (p, u, v)


# Send inputs and receive outputs.
def Encrypt(port, p, u, v):
    c = bytes([])

    # Send plaintext
    for i in range(16):
        Putchar(p[i])
        pass

    # Send u
    Putchar(u)

    # Send v
    Putchar(v)

    # Read ciphertext
    for i in range(16):
        c += Getchar()
        pass

    return c


def main(argc, argv):
    global ntrace, port, usetestvector, userandom

    args = Args()

    if args.ntrace:
        ntrace = int(args.ntrace)
        pass

    if args.port:
        port = seal.VirtualPort(args.port)
        pass

    if args.testvector:
        usetestvector = True
        pass
    elif args.random:  # uservector overwrites userandom
        userandom = True
        pass

    # Set key.
    key = GenKey()
    print("#Key={}".format(key.hex()))
    SetKey(port, key)

    # Encrypt
    while ntrace > 0:
        # Command
        print("#  Command = {}".format(CMD_ENCRYPT))
        Putchar(CMD_ENCRYPT)
        msg = ReadLine(port)
        print('(uelmo)', msg, end='')

        # Generate inputs.
        (p, u, v) = GenInput()
        print("#P={}, U={}, V={}".format(p.hex(), u.hex(), v.hex()))

        # Encrypt.
        c = Encrypt(port, p, u, v)
        print("#Ciphertext:", c.hex())
        ntrace -= 1
        time.sleep(1)
        pass

    # Send exit.
    Putchar(CMD_EXIT)

    del port  # Activly close the port.
    return 0


if __name__ == '__main__':
    exit(main(len(sys.argv), sys.argv))
    pass
