import sys
import seal


SEAL_PORT = None
TERMINATOR = 'exit\n'


# Read a line from port.
def ReadLine(port):
    line = bytes([])
    while True:
        b = port.Getchar()
        line += b
        if b == ('\n').encode('ascii'):
            break
            pass

        pass

    return line.decode('ascii')


def main(argc, argv):
    SEAL_TEST_PORT = argv[1]
    port = seal.VirtualPort(SEAL_TEST_PORT)

    # Client
    while True:
        # Read from stdin.
        l = sys.stdin.readline()

        # Write to port and read ACK.
        port.Wr(l)

        response = ReadLine(port)
        print(response, end='')

        if l == TERMINATOR:
            break
            pass

        pass

    del port  # Activly close the port.
    return 0


if __name__ == '__main__':
    exit(main(len(sys.argv), sys.argv))
    pass
