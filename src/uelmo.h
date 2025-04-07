#ifndef UELMO_H
#define UELMO_H

#include <stdint.h>
#include <stdbool.h>

#define UELMO_ERROR (-1)
#define MAX_PATH_LAN (255)

#ifdef USE_SEAL
#include "seal/seal.h"
#include "seal/emulator.h"

#define ELMO_CORE "./sealfiles/uelmo.json"
extern SealVirtualPort *sealport;
extern char *sealtracepath;
extern char *portpath;
extern Seal *seal;
extern const char *scriptpath;
#endif

extern int cyclecount;
extern uint32_t frameno;
extern bool OnTrace;
extern bool verbose;
#endif
