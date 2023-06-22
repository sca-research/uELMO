#ifdef USE_SMURF

#include <stdio.h>		//DEBUG ONLY

#include "smurf/smurf.h"
#include "uelmo.h"
#include "ulang.h"

//Script used in this simulation.
SmurfScript *script = NULL;

//Initialise the script file by path ${scriptpath}.
//Return values: 
//  0   : If a script is intialised.
//  -1  : Error
int InitScript(const char *scriptpath)
{
    //NULL check.
    if (NULL == scriptpath)
	{
	    INFO("");
	    return -1;
	}

    //Load in a script.
    if (NULL == (script = LoadScript(scriptpath)))
	{
	    return -1;
	}

    //Enable skip indent.
    script->skipindent = true;

    return 0;
}

//Check if a char is in the blank set.
//blank set: {' ', '\t', '\n'}
static int IsBlank(const char c)
{
    switch (c)
	{
	case ' ':
	case '\t':
	case '\n':
	    return 1;
	    break;

	default:
	    return 0;
	    break;
	}

    return 0;
}

//Get the position of next argument in $(cmdline). ${arglen} is set to the length of this argument (excluding '\0')
//Return value:
//  NULL : The cmdline has no arg.
//  Otherwise : the starting point of the first argument.
static const char *GetNextArg(const char *cmdline, int *arglen)
{
    const char *argpos = NULL;
    const char *c = NULL;

    //Initialise arglen.
    *arglen = 0;

    //Skip beginning blank chars.
    for (c = cmdline; IsBlank(*c); c++) ;

    //Check EOL.
    if ('\0' == *c)
	{
	    return NULL;
	}

    //Record starting position of next arg.
    argpos = c;

    //Count the length of arg.
    while (!IsBlank(*c) && *c != '\0')
	{
	    c++;
	    (*arglen)++;
	}

    return argpos;
}

//Check if the line is a Ulang command.
static int IsUlangCmd(const char *line)
{
    const char *arg;
    int arglen;

    //Check if the first arg is ULang notifier.
    if (NULL == (arg = GetNextArg(line, &arglen)))	//A NULL line.
	{
	    return 0;
	}
    if (0 == strncmp(arg, ULANG_NOTIFIER, arglen))
	{
	    return 1;
	}
    return 0;
}

//Process a line in a command block.
void UlangSed(int linenumber, const char *line, void *arg)
{
    const char *nextarg;

    //Check if the line is a Ulang command.
    //Ignore all non command lines.
    if (IsUlangCmd(line))
	{
	    //Process the command.

	    //DBG
	    printf("%d(%d) - %d\t: %s\n", cyclecount, frameno, linenumber,
		   line);
	}

    return;
}

//Read in an command block.
int ReadNextCmdBlock()
{
    ProcessSib(script, UlangSed, NULL);
    return 0;
}

#endif
