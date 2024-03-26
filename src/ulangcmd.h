#ifndef ULANGCMD_H
#define ULANGCMD_H

#ifdef USE_SEAL
#include "seal/sealscript.h"
#include "symuelmo.h"

#define INVALID_REG (-1)

//ULANG commands implementation.
//
//Initialisation and descrution of all commands.
int InitUlangCmd();
void CleanUlangCmd();

//Remove all pending requests in all queues.
void ResetUlangCmd();

//Handler of src
extern SealQueue *srcqueue;     //Queue for src command.

//Arguments of src command.
struct srcArg {
    int reg;
    uSymbol sym;
};

//Send src requests to src queue.
void RequestSrc(int argc, char **argv);

//Resolve all src requests.
int ResolveSrc();

//Remove all pending requests on srcqueue.
void CleanSrc();

//Handler of dst
extern SealQueue *dstqueue;     //Queue for dst command.

//Arguments of dst command.
struct dstArg {
    int reg;                    //Redundant for annotation.
    uSymbol sym;
};

//Send dst requests to dst queue.
void RequestDst(int argc, char **argv);

//Resolve all dst requests.
typedef struct __DstRet__ {
    int reg;
    uSymbol sym;
} DstRet;

//Returns the last Symbol in dst queue.
DstRet ResolveDst();

//Remove all pending requests on dstqueue.
void CleanDst();

#endif
#endif
