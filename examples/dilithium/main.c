#include "main.h"

#include "config.h"
#include "ntt.h"

const char hellostr[] = "hello,world!\n";

//Nibble to hex.
static char ntohex(int nib)
{
    if(0xA > nib)
    {
        return '0' + nib;
    }
    else
    {
        return 'A' + nib - 0x0A;
    }
    return 0;
}

//uint8 to hex.
static void u8tohex(uint8_t in, char *out)
{
    out[0] = ntohex(in >> 4);
    out[1] = ntohex(in & 0x0F);
    return;
}

static void Print(const char *str, int len)
{
    int i;
    const char *c;
    for (c = str, i = 0; i < len; c++, i++)
    {
        printbyte((unsigned char *)c);
    }
    return;
}

static void PrintByte(uint8_t i)
{
    char out[2];

    u8tohex(i, out);

    Print(out, 2);

    return;
}

static void PrintInt(uint32_t i32)
{
    unsigned int i;
    char c[4] = { 0 };

    for (i = 0; i < 4; i++)
    {
        c[i] = i32 >> (i * 8);
    }

    for (i = 0; i < 4; i++)
    {
        PrintByte(c[3 - i]);
    }

    return;
}

static void PrintNttArray(int32_t *nttarray)
{
    int i;
    for (i = 0; i < N; i++)
    {
        PrintInt(nttarray[i]);
        Print(" ", 1);
    }
    Print("\n", 1);

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

    Print(hellostr, sizeof(hellostr));

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
