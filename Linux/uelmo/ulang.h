#ifndef _ULANG_H
#define _ULANG_H

#ifdef USE_SEAL

#include "seal/sealscript.h"
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
extern SealScript *script;

//Flag for first block.
extern bool firstcmdblock;

//Print script log.
void PrintScriptLog(const char *fmt, ...);

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

//Reset script cursoe.
int ResetScript();

//ULANG callback manager. argc and argv are passed to the handler functions.
void UlangCbManager(const char *op, int argc, char *argv[]);

#endif
#endif
