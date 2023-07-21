//ULANG commands implementation.
#include <stdio.h>              //DBG

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

//Command: 
//  src
//Format: 
//  src REG SYMBOL
//Description:
//  Tag ${REG} with ${SYMBOL} when an instruction is in Decode.
//Example:
//  src r0 Key0
SmurfQueue *srcqueue = NULL;    //Initialised in InitUlangCmd().

//Send src requests to src queue.
void RequestSrc(int argc, char **argv)
{
    int reg = 0;
    uSymbol sym = { 0 };
    struct srcArg *arg = NULL;

    //Format check.
    if(3 != argc)
    {
        printf("#ERROR: Command error (src).\n");
        return;
    }

    //Scan command arguments for parameters.
    if(!sscanf(argv[1], "r%d", &reg))   //REG
    {
        printf("#ERROR: Unknown parameter: %s\n", argv[1]);
        return;
    }

    //Encode SYMBOL
    if(IsSymNull(sym = SymEncode(argv[2])))
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

        //Assign sym to reg.
        SymAssign(sym_core_current.reg[sarg->reg], sarg->sym);

        //Free the arguments.
        Free(sarg);
    }

    return 0;
}

//Command: 
//  dst
//Format: 
//  dst REG SYMBOL
//Description:
//  Tag ${REG} with ${SYMBOL} when an instruction is in Execute.
//Example:
//  dst r0 Key0
SmurfQueue *dstqueue = NULL;    //Initialise in InitUlangCmd().

//Send dst requests to dst queue.
void RequestDst(int argc, char **argv)
{
    int reg = 0;
    uSymbol sym = { 0 };
    struct dstArg *arg = NULL;

    //Format check.
    if(3 != argc)
    {
        printf("#ERROR: Command error (dst).\n");
        return;
    }

    //Scan command arguments for parameters.
    if(!sscanf(argv[1], "r%d", &reg))   //REG
    {
        printf("#ERROR: Unknown parameter: %s\n", argv[1]);
        return;
    }

    //Encode SYMBOL
    if(IsSymNull(sym = SymEncode(argv[2])))
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
//Returns the last Symbol in dst queue.
uSymbol ResolveDst()
{
    uSymbol retsym = SYM_NULL;
    struct dstArg *darg = NULL;

    //Pull all existing requests.
    while (NULL != (darg = SqPop(dstqueue)))
    {
        //Tag a component.
        //DBG
        printf("[%d(%d)] dst tagged: REG=%d, SYMBOL=%d\n",
               cyclecount, frameno, darg->reg, darg->sym.symid);

        //Update the return value with the last Symbol in the queue.
        retsym = darg->sym;

        //Free the arguments.
        Free(darg);
    }

    return retsym;
}
