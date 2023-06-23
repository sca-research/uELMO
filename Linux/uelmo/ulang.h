#ifndef _ULANG_H
#define _ULANG_H

#ifdef USE_SMURF

#include "smurf/smurfscript.h"

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

//ULANG commands.
int InitUlangCmd();
void CleanUlangCmd();

//Handler of src
extern SmurfQueue *srcqueue;
struct srcarg {
    int reg;
    int sym;
};
void RequestSrc(int argc, char **argv);

//Handler of dst
extern SmurfQueue *dstqueue;
struct dstarg {
    int reg;
    int sym;
};
void RequestDst(int argc, char **argv);
#endif
#endif
