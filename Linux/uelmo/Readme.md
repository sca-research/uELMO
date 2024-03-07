
# How to use Sealed-uELMO(=smuelmo)


## 1. Install the SEAL library


Do:
```sh
$ git clone https://github.com/sca-research/Seal
$ cd Seal
$ source setup.sh
```

Note that the above commands would allow you to use SEAL *ONLY* in the current terminal.

## 3. Build smuelmo

Now we can build smuelmo:

```sh
$ cd
$ git clone https://github.com/sca-research/uELMO
$ cd uELMO
$ git checkout Seal
$ cd Linux/uelmo
$ make smuelmo
```
Now you should have the executable binary smuelmo.

## 4. Using smuelmo
The basic usage of smuelmo is:
$ ./smuelmo ${YOUR_BIN_IMAGE} -N ${NUMBER_OF_TRACES} -o ${UELMO_OUTPUT_FILE}  [--st ${SEAL_FORMAT_OUTPUT}]

Note that UELMO output is mandatory and SEAL output is optional. If you wish to only have the SEAL output then you can simply specify UELMO_OUTPUT_FILE to /dev/null.

### Using IO with smuelmo
Serial port simulation, i.e. byte IO, is supported by smuelmo.

For the target image, serial port IO is implemented by readbyte() and printbyte() defined in elmoasmfunctionsdef.h.

```c
//Example: foo.c
#include "elmoasmfunctionsdef.h"

int main()
{
    char c;
    readbyte(&c);   //Read a byte from serial port.
    printbyte(&c);  //Write a byte to the serial port.
    return;
}
//End of foo.c.
```

By default, the simulated serial port IO are directed to STDIN and STDOUT by smuelmo. Additionally smuelmo also allows you to channel the serial port input to a file by using the option -r ${FILE_TO_BE_CHANNELD}.

Alternatively you can also use the SEAL IO system to achieve a more realistic scenario of a real device. To do this, you first need to create a SEAL IO Interface with the --io option:
$ ./smuelmo ${YOUR_BIN_IMAGE} -N ${NUMBER_OF_TRACES} -o ${UELMO_OUTPUT_FILE}  [--st ${SEAL_FORMAT_OUTPUT}] [--io ${PATH_TO_SEAL_IO_INTERFACE}]

This will create a virtual interface specified by the path ${PATH_TO_SEAL_IO_INTERFACE} and the simulation will be blocked until the SEAL IO Interface is connected, which can be done in a python script such as below:

```python
# Example: foo.py
import seal

path = SEAL_IO_IF_PATH     # The path as specified by ${PATH_TO_SEAL_IO_INTERFACE}.
sio = seal.IO(path)        # This connects the SEAL IO Interface.
sio.Putchar(bytes([0]))     # Send a byte (0) to the simulated serial port.
recv = sio.Getchar()        # Receives a byte from the simulated serial port.
# End of foo.py.
```

## 5. Reading a SEAL trace 
You can use the readtracefile.py at uELMO/Linux/uelmo/sealfiles to display a SEAL trace:
```sh
$ python3 readtracefile.py ${SEAL_FORMAT_OUTPUT}
```
The same script also serves as an example of how to use the SEAL python module to interpret a SEAL trace.

## 6. Known issues
1. A potential bug may exist in the forward mechanism that it does not trigger in some code sequences. This has been noticed once in SUB(1) instruction. The temporary patch for SUB(1) is to write back to the target register immediately ignoring the forward mechanism. Such patching results into a memory cycle inconsistency (i.e. the ALU output is written back to the register earlier than it should be).

2. Symbols are annotated to Memory_data and Memory_readbuf in the first cycle of LDR instructions, despite data are physically loaded into the bus in the next cycle.
