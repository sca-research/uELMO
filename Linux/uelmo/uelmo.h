#ifndef UELMO_H
#define UELMO_H

#include <stdint.h>
#include <stdbool.h>

#define UELMO_ERROR (-1)
#define MAX_PATH_LAN (255)

#ifdef USE_SMURF
#include "smurf/smurf.h"
#include "smurf/emulator.h"

#define ELMO_CORE "./smurffiles/uelmo.json"
extern SmurfIO *sio;
extern char *smftracepath;
extern char *siopath;
extern Smurf *smurf;
extern const char *scriptpath;
#endif

extern int cyclecount;
extern uint32_t frameno;
extern bool OnTrace;
#endif
