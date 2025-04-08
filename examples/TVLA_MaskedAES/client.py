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
enduelmo = False


def Print(*objects, **kwargs):
    if port != None:
        print(*objects, **kwargs)
        pass
    return


def Args():
    parser = argparse.ArgumentParser('Masked AES client')

    parser.add_argument('-n', '--ntrace', help='Number of Trace')
    parser.add_argument('-p', '--port', help='Path to SealVirtualPort')
    parser.add_argument(
        '-r', '--random', help='Use random input', action='store_true')
    parser.add_argument(
        '--testvector', help='Use AES test vector', action='store_true')
    parser.add_argument('-e', '--enduelmo',
                        help='End uELMO', action='store_true')

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
def ReadLine():
    global port
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
def SetKey(key):
    global port

    # Command
    Print("#Command={}".format(CMD_SET_KEY))
    Putchar(CMD_SET_KEY)

    # Send key
    for i in range(16):
        Putchar(key[i])
        pass

    ack = ReadLine()
    Print('(uelmo)', ack, end='')

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

    # u = random.randbytes(1)
    # v = random.randbytes(1)

    return (p)


# Send inputs and receive outputs.
def Encrypt(p):
    global port

    c = bytes([])

    # Send plaintext
    for i in range(16):
        Putchar(p[i])
        pass

    # Send u
    # Putchar(u)

    # Send v
    # Putchar(v)

    # Read ciphertext
    for i in range(16):
        c += Getchar()
        pass

    return c


def main(argc, argv):
    global ntrace, port, usetestvector, userandom, enduelmo

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

    if args.enduelmo:
        enduelmo = True
        pass

    if not userandom:  # Use a fixed key for all encryptions.
        key = GenKey()
        Print("#Key={}".format(key.hex()))
        SetKey(key)
        pass

    # Encrypt
    while ntrace > 0:
        if userandom:  # Use a random key for each encryption.
            key = GenKey()
            Print("#Key={}".format(key.hex()))
            SetKey(key)
            pass

        # Command
        Print("#Command={}".format(CMD_ENCRYPT))
        Putchar(CMD_ENCRYPT)
        msg = ReadLine()
        Print('(uelmo)', msg, end='')

        # Generate inputs.
        p = GenInput()

        Print("#P={}".format(p.hex()))

        # Encrypt.
        c = Encrypt(p)
        Print("#C={}".format(c.hex()))
        ntrace -= 1
        time.sleep(1)
        pass

    if enduelmo:
        # Send exit.
        Putchar(CMD_EXIT)
        pass

    del port  # Activly close the port.
    return 0


if __name__ == '__main__':
    exit(main(len(sys.argv), sys.argv))
    pass
