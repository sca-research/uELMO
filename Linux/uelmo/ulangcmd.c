//ULANG commands implementation.
#include <stdio.h>		//DBG

#include "uelmo.h"
#include "symuelmo.h"
#include "ulangcmd.h"

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
