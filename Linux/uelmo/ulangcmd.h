#ifndef ULANGCMD_H
#define ULANGCMD_H

#include "smurf/smurfscript.h"
#include "symuelmo.h"

//ULANG commands implementation.
//
//Initialisation and descrution of all commands.
int InitUlangCmd();
void CleanUlangCmd();

//Handler of src
extern SmurfQueue *srcqueue;    //Queue for src command.

//Arguments of src command.
struct srcArg {
    int reg;
    uSymbol sym;
};

//Send src requests to src queue.
void RequestSrc(int argc, char **argv);

//Resolve all src requests.
int ResolveSrc();

//Handler of dst
extern SmurfQueue *dstqueue;    //Queue for dst command.

//Arguments of dst command.
struct dstArg {
    int reg;
    uSymbol sym;
};

//Send dst requests to dst queue.
void RequestDst(int argc, char **argv);

//Resolve all dst requests.
int ResolveDst();
#endif
