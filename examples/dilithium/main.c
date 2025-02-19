#include "main.h"

#include "config.h"
#include "ntt.h"

const char hellostr[] = "hello,world!\n";

//Nibble to hex.
static void PrintNttArray(int32_t *nttarray)
{
    int i;
    for (i = 0; i < N; i++)
    {
        PrintInt(nttarray[i]);
        PrintStr(" ", 1);
    }
    PrintStr("\n", 1);

    return;
}

static void Randint32(int32_t *rint)
{
    int i;
    unsigned char r;

    for (i = 0; i < 3; i++)
    {
        randbyte(&r);
        *rint ^= r;
        *rint <<= 8;
    }
    randbyte(&r);
    *rint ^= r;

    return;
}

int main(void)
{
    int i;
    int32_t nttarray[N] = { 0 };
    int32_t r = 0;

    PrintStr(hellostr, sizeof(hellostr));

    //Randomise input.
    for (i = 0; i < N; i++)
    {
        Randint32(&r);
        nttarray[i] = r;
    }
    PrintNttArray(nttarray);

    starttrigger();             //Trace start.
    ntt(nttarray);
    endtrigger();               //Trace end.

    PrintNttArray(nttarray);

    endprogram();
    return 0;
}
