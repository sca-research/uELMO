#include "main.h"

#include <stdbool.h>
#include "config.h"
#include "ntt.h"

#define RAND_MTX ((0))

const char hellostr[] = "hello,world!\n";

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

#if RAND_MTX
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
#else
static int32_t ReadInt(void)
{
    int32_t ri = 0;
    int nshift = 24;

    //Read from big endian and store in little endian.
    for (int i = 0; i < 4; i++, nshift -= 8)
    {
        unsigned char b = 0;
        readbyte(&b);
        ri ^= (b << nshift);
    }

    return ri;
}

static void ReadMtx(int32_t *nttarray)
{
    for (int i = 0; i < N; i++)
    {
        nttarray[i] = ReadInt();
    }
    return;
}
#endif

int main(void)
{
    int32_t nttarray[N] = { 0 };

    PrintStr(hellostr, sizeof(hellostr));

    while (true)
    {
#if RAND_MTX
        //Randomise NTT input matrix.
        for (int i = 0; i < N; i++)
        {
            Randint32(&nttarray[i]);
        }
#else
        //Read NTT input matrix from GPIO.
        ReadMtx(nttarray);
#endif
        PrintNttArray(nttarray);

        starttrigger();         //Trace start.
        ntt(nttarray);
        endtrigger();           //Trace end.

        PrintNttArray(nttarray);
    }

    endprogram();
    return 0;
}
