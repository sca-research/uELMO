#ifndef _ULANG_H
#define _ULANG_H

#ifdef USE_SMURF

#include "smurf/smurfscript.h"
#include "symuelmo.h"

#define ULANG_NOTIFIER (("@@$ "))
#define ULANG_MAX_ARGC ((16))
#define ULANG_MAX_ARGLEN ((255))

//Supported command strings.
#define ULANG_SRC (("src"))
#define ULANG_DST (("dst"))

//Prototype for each ULANG command callback.
typedef void (*UlangCmd)(int argc, char **argv);

//The ULANG script.
extern SmurfScript *script;

//Initialise the script file by path ${scriptpath}.
//Return values: 
//  0   : If a script is intialised.
//  -1  : Error
int InitScript(const char *scriptpath);

//Clean resources related to the script.
void CleanScript();

//Process a line in a command block.
void UlangSed(int linenumber, const char *line, void *arg);

//Read in the next command block.
int ReadNextCmdBlock();

//ULANG callback manager. argc and argv are passed to the handler functions.
void UlangCbManager(const char *op, int argc, char *argv[]);

//ULANG commands implementation.
//Initialisation and descrution of all commands.
int InitUlangCmd();
void CleanUlangCmd();

//Handler of src
extern SmurfQueue *srcqueue;	//Queue for src command.

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
extern SmurfQueue *dstqueue;	//Queue for dst command.

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
#endif
