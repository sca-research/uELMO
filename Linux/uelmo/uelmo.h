#ifndef UELMO_H
#define UELMO_H
#define UELMO_ERROR (-1)

#ifdef USE_SMURF
#include "smurf/smurf.h"
#include "smurf/emulator.h"

#define ELMO_IO_PATH "/tmp/elmoio"
SmurfIO *sio;
#endif

#endif
