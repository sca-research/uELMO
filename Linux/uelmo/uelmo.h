#ifndef UELMO_H
#define UELMO_H
#define UELMO_ERROR (-1)

#ifdef USE_SMURF
#include "smurf/smurf.h"
#include "smurf/emulator.h"

#define ELMO_CORE "./smurffiles/uelmo.json"
extern SmurfIO *sio;
extern char *smftracepath;
extern char *siopath;
extern Smurf *smurf;
#endif

extern uint32_t frameno;

#endif
