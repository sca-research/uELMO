#ifdef USE_SEAL
#include <stdio.h>
#include <string.h>
#include <stdarg.h>

#include "seal/seal.h"
#include "symuelmo.h"
#include "uelmo.h"
#include "ulangcmd.h"
#include "ulang.h"

//Script used in this simulation.
SealScript *script = NULL;

//Flag for first block.
bool firstcmdblock = true;

//Print script log.
void PrintScriptLog(const char *fmt, ...)
{
    va_list args;
    va_start(args, fmt);
    if(verbose && SYM_ENABLED)
    {
        vprintf(fmt, args);
    }
    va_end(args);
    return;
}

//Initialise the script file by path ${scriptpath}.
//Return values: 
//  0   : If a script is intialised.
//  -1  : Error
int InitScript(const char *scriptpath)
{
    //NULL check.
    if(NULL == scriptpath)
    {
        INFO("#No script file specified.\n");
        return -1;
    }

    //Load in a script.
    if(NULL == (script = LoadScript(scriptpath)))
    {
        perror("#Cannot open script file:");
        return -1;
    }

    //Enable skip indent.
    script->skipindent = true;

    //Initialise the supported ULANG commands.
    InitUlangCmd();

    return 0;
}

//Clean resources related to the script.
void CleanScript()
{
    CleanUlangCmd();
    FreeScript(script);
    return;
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
    if('\0' == *c)
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
    if(NULL == (arg = GetNextArg(line, &arglen)))       //A NULL line.
    {
        return 0;
    }
    if(0 == strncmp(arg, ULANG_NOTIFIER, arglen))
    {
        return 1;
    }
    return 0;
}

//Process a line in a command block.
void UlangSed(int linenumber, const char *line, void *arg)
{
    char *nextarg = NULL;
    int arglen = 0;

    //argc and argv for ULANG commands.
    char *argline = NULL;
    int uargc = 0;
    char *uargv[ULANG_MAX_ARGC] = { 0 };

    //Ignore if not enabled.
    if(!SYM_ENABLED)
    {
        return;
    }

    //Check if the line is a Ulang command.
    //Ignore all non command lines.
    if(IsUlangCmd(line))
    {
        //Process the command.
        //printf("[%d(%d)] Command(L%d)\t: %s\n", cyclecount, frameno, linenumber, line);

        //Skip the first ULANG notifier.
        nextarg = (char *)GetNextArg(line, &arglen);
        nextarg += arglen;

        //Create editable copy excluding the notifier.
        argline = CloneString(nextarg);
        nextarg = argline;

        //Construct argc and argv.
        while (ULANG_MAX_ARGC > uargc)
        {
            if(NULL == (nextarg = (char *)GetNextArg(nextarg, &arglen)))        //All args processed.
            {
                break;
            }

            //Parse into argv.
            uargv[uargc] = nextarg;
            uargc++;

            //Advance to the nextarg.
            nextarg += arglen;

            //Swap ' ' bt '\0'
            if(IsBlank(*nextarg))
            {
                *nextarg = '\0';
                nextarg++;
            }
        }

        //Execute the command.
        UlangCbManager(uargv[0], uargc, uargv);
        Free(argline);
    }

    return;
}

//Read in an command block.
int ReadNextCmdBlock()
{
    //Skip the first command block.
    if(firstcmdblock)
    {
        if(verbose)
        {
            printf("# Skip the first command block.\n");
        }
        ProcessSib(script, NULL, NULL);
        firstcmdblock = false;
    }

    if(verbose)
    {
        printf("#Frame %d:\n", frameno);
    }
    ProcessSib(script, UlangSed, NULL);
    return 0;
}

//Reset script cursor.
int ResetScript()
{
    ResetCursor(script);
    ResetUlangCmd();
    return 0;
}

//ULANG callback manager. argc and argv are passed to the handler functions.
void UlangCbManager(const char *op, int argc, char **argv)
{
    //Match instructions.
    if(!strncmp(op, ULANG_SRC, sizeof(ULANG_SRC)))      //src
    {
        RequestSrc(argc, argv);
    }
    else if(!strncmp(op, ULANG_DST, sizeof(ULANG_DST))) //dst
    {
        RequestDst(argc, argv);
    }
    else                        //Unknown instruction.
    {
        fprintf(stderr, "ERROR: unknown command: %s\n", op);
        INFO("Not supported ULANG command:");
        INFO(op);
        INFO("\n");
    }

    return;
}

#endif
