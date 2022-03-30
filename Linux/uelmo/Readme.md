*How to use Smurfed-uELMO(=smuelmo)*

** 1. Install the SMURF library **
Do:
$ git clone https://github.com/sca-research/Smurf

** 2. Configure the SMURF library **
Do:
$ cd Smurf
$ source setup.sh

Note that the above commands would allow you to use SMURF *ONLY* in the current terminal.

** 3. Build smuelmo **
Now we can build smuelmo:
$ cd
$ git clone https://github.com/sca-research/uELMO
$ cd uELMO
$ git checkout Smurf
$ cd Linux/uelmo
$ make smuelmo

Now you should have the executable binary smuelmo.

** 4. Using smuelmo **
The basic usage of smuelmo is:
$ ./smuelmo ${YOUR_BIN_IMAGE} -N ${NUMBER_OF_TRACES} -o ${UELMO_OUTPUT_FILE}  [--st ${SMURF_FORMAT_OUTPUT}]

Note that UELMO output is mandatory and SMURF output is optional. If you wish to only have the SMURF output then you can simply specify UELMO_OUTPUT_FILE to /dev/null.

***Using IO with smuelmo***
Serial port simulation, i.e. byte IO, is supported by smuelmo.

For the target image, serial port IO is implemented by readbyte() and printbyte() defined in elmoasmfunctionsdef.h.

----------------
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
----------------

By default, the simulated serial port IO are directed to STDIN and STDOUT by smuelmo. Additionally smuelmo also allows you to channel the serial port input to a file by using the option -r ${FILE_TO_BE_CHANNELD}.

Alternatively you can also use the SMURF IO system to achieve a more realistic scenario of a real device. To do this, you first need to create a SMURF IO Interface with the --io option:
$ ./smuelmo ${YOUR_BIN_IMAGE} -N ${NUMBER_OF_TRACES} -o ${UELMO_OUTPUT_FILE}  [--st ${SMURF_FORMAT_OUTPUT}] [--io ${PATH_TO_SMURF_IO_INTERFACE}]

This will create a virtual interface specified by the path ${PATH_TO_SMURF_IO_INTERFACE} and the simulation will be blocked until the SMURF IO Interface is connected, which can be done in a python script such as below:

----------------
\# Example: foo.py
import smurf

path = SMURF_IO_IF_PATH     # The path as specified by ${PATH_TO_SMURF_IO_INTERFACE}.
sio = smurf.IO(path)        # This connects the SMURF IO Interface.
sio.Putchar(bytes([0]))     # Send a byte (0) to the simulated serial port.
recv = sio.Getchar()        # Receives a byte from the simulated serial port.
\# End of foo.py.
----------------

** 5. Reading a SMURF trace **
You can use the readtracefile.py at uELMO/Linux/uelmo/smurffiles to display a SMURF trace:
$ python3 readtracefile.py ${SMURF_FORMAT_OUTPUT}

The same script also serves as an example of how to use the SMURF python module to interpret a SMURF trace.
