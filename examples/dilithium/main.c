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

static void RandMtx(int32_t *nttarray)
{
    for (int i = 0; i < N; i++)
    {
        Randint32(&nttarray[i]);
    }
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

//Returns 0 when the input is a zero matrix.
static int ReadMtx(int32_t *nttarray)
{
    int ret = 0;
    for (int i = 0; i < N; i++)
    {
        ret |= (nttarray[i] = ReadInt());
    }
    return ret;
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
        RandMtx(nttarray);
#else
        //Read NTT input matrix from GPIO.
        if(0 == ReadMtx(nttarray))
        {
            break;
        }
#endif
        PrintNttArray(nttarray);

        starttrigger();         //Trace start.
        ntt(nttarray);
        endtrigger();           //Trace end.
#if RAND_MTX
        break;
#endif
        PrintNttArray(nttarray);
    }

    endprogram();
    return 0;
}
