#ifndef _ULANG_H
#define _ULANG_H

#ifdef USE_SMURF

#include "smurf/smurfscript.h"

#define ULANG_NOTIFIER (("@@$ "))

extern SmurfScript *script;

//Initialise the script file by path ${scriptpath}.
//Return values: 
//  0   : If a script is intialised.
//  -1  : Error
int InitScript(const char *scriptpath);

//Process a line in a command block.
void UlangSed(int linenumber, const char *line, void *arg);

//Read in the next command block.
int ReadNextCmdBlock();

#endif
#endif
