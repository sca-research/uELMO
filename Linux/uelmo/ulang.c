#include <stdio.h>		//DEBUG ONLY

#include "smurf/smurf.h"
#include "symuelmo.h"
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
    char *nextarg = NULL;
    int arglen = 0;

    //argc and argv for ULANG commands.
    char *argline = NULL;
    int uargc = 0;
    char *uargv[ULANG_MAX_ARGC] = { 0 };

    //Check if the line is a Ulang command.
    //Ignore all non command lines.
    if (IsUlangCmd(line))
	{
	    //Process the command.
	    //DBG
	    printf("[%d(%d)] Command(L%d)\t: %s\n", cyclecount, frameno,
		   linenumber, line);

	    //Skip the first ULANG notifier.
	    nextarg = (char *)GetNextArg(line, &arglen);
	    nextarg += arglen;

	    //Create editable copy excluding the notifier.
	    argline = CloneString(nextarg);
	    nextarg = argline;

	    //Construct argc and argv.
	    while (ULANG_MAX_ARGC > uargc)
		{
		    if (NULL == (nextarg = (char *)GetNextArg(nextarg, &arglen)))	//All args processed.
			{
			    break;
			}

		    //Parse into argv.
		    uargv[uargc] = nextarg;
		    uargc++;

		    //Advance to the nextarg.
		    nextarg += arglen;

		    //Swap ' ' bt '\0'
		    if (IsBlank(*nextarg))
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
    ProcessSib(script, UlangSed, NULL);
    return 0;
}

//ULANG callback manager. argc and argv are passed to the handler functions.
void UlangCbManager(const char *op, int argc, char **argv)
{
    //Match instructions.
    if (!strncmp(op, ULANG_SRC, sizeof(ULANG_SRC)))	//src
	{
	    RequestSrc(argc, argv);
	}
    else if (!strncmp(op, ULANG_DST, sizeof(ULANG_DST)))	//dst
	{
	    RequestDst(argc, argv);
	}
    else			//Unknown instruction.
	{
	    printf("ERROR: unknown command: %s\n", op);
	    INFO("Not supported ULANG command:");
	    INFO(op);
	    INFO("\n");
	}

    return;
}

//ULANG commands implementation.
//Initialisation and descrution of all commands.
int InitUlangCmd()
{
    srcqueue = NewSmurfQueue();
    dstqueue = NewSmurfQueue();
    return 0;
}

void CleanUlangCmd()
{
    DelSmurfQueue(dstqueue, NULL);
    DelSmurfQueue(srcqueue, NULL);
    return;
}

//Handler: src REG SYMBOL
SmurfQueue *srcqueue = NULL;	//Initialised in InitUlangCmd().

//Send src requests to src queue.
void RequestSrc(int argc, char **argv)
{
    int reg = 0;
    uSymbol sym = { 0 };
    struct srcArg *arg = NULL;

    //Format check.
    if (3 != argc)
	{
	    printf("#ERROR: Command error (src).\n");
	    return;
	}

    //Scan command arguments for parameters.
    if (!sscanf(argv[1], "r%d", &reg))	//REG
	{
	    printf("#ERROR: Unknown parameter: %s\n", argv[1]);
	    return;
	}

    //Encode SYMBOL
    if (IsSymNull(sym = SymEncode(argv[2])))
	{
	    printf("#ERROR: Symbol encoding failed for %s\n", argv[2]);
	    return;
	}

    //DBG
    printf("[%d(%d)] Request src: REG=%d, SYMBOL=%s(%d)\n", cyclecount, frameno,
	   reg, argv[2], sym.symid);

    //Push the src arguments into src quque.
    arg = (struct srcArg *)Malloc(sizeof(struct srcArg));
    arg->reg = reg;
    arg->sym = sym;
    SqPush(srcqueue, arg);

    return;
}

//Resolve all src requests.
int ResolveSrc()
{
    struct srcArg *sarg = NULL;

    //Pull all existing requests.
    while (NULL != (sarg = SqPop(srcqueue)))
	{
	    //Tag a component.
	    //DBG
	    printf("[%d(%d)] src tagged: REG=%d, SYMBOL=%d\n",
		   cyclecount, frameno, sarg->reg, sarg->sym.symid);

	    //Free the arguments.
	    Free(sarg);
	}

    return 0;
}

//Handler: dst REG SYMBOL
SmurfQueue *dstqueue = NULL;	//Initialise in InitUlangCmd().

//Send dst requests to dst queue.
void RequestDst(int argc, char **argv)
{
    int reg = 0;
    uSymbol sym = { 0 };
    struct dstArg *arg = NULL;

    //Format check.
    if (3 != argc)
	{
	    printf("#ERROR: Command error (dst).\n");
	    return;
	}

    //Scan command arguments for parameters.
    if (!sscanf(argv[1], "r%d", &reg))	//REG
	{
	    printf("#ERROR: Unknown parameter: %s\n", argv[1]);
	    return;
	}

    //Encode SYMBOL
    if (IsSymNull(sym = SymEncode(argv[2])))
	{
	    printf("#ERROR: Symbol encoding failed for %s\n", argv[2]);
	    return;
	}

    //DBG
    printf("[%d(%d)] Request dst: REG=%d, SYMBOL=%s(%d)\n", cyclecount, frameno,
	   reg, argv[2], sym.symid);

    //Push the dst arguments into dst quque.
    arg = (struct dstArg *)Malloc(sizeof(struct dstArg));
    arg->reg = reg;
    arg->sym = sym;
    SqPush(dstqueue, arg);

    return;
}

//Resolve all dst requests.
int ResolveDst()
{
    struct dstArg *darg = NULL;

    //Pull all existing requests.
    while (NULL != (darg = SqPop(dstqueue)))
	{
	    //Tag a component.
	    //DBG
	    printf("[%d(%d)] dst tagged: REG=%d, SYMBOL=%d\n",
		   cyclecount, frameno, darg->reg, darg->sym.symid);

	    //Free the arguments.
	    Free(darg);
	}

    return 0;
}
