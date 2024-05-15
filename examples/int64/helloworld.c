#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "elmoasmfunctionsdef.h"

const char start[] = "start\n";
const char end[] = "\nend\n";

static void PrintLine(const char *line, int len)
{
    int i = 0;

    for (i = 0; i < len; i++)
    {
        printbyte((unsigned char *)&line[i]);
    }

    return;
}

static char NibToHex(const char x)
{
    char h;

    if(x < 10)
    {
        h = x + '0';
    }
    else
    {
        h = x + 'A';
    }

    return h;
}

static void PrintHex(const char x)
{
    unsigned char xl, xh;

    xl = NibToHex(x & 0x0F);
    xh = NibToHex((x & 0xF0) >> 4);

    printbyte(&xh);
    printbyte(&xl);

    return;
}

static void br_aes_ct64_interleave_in1(uint64_t * q0, uint64_t * q1,
                                       uint32_t * w)
{
    uint64_t x0, x1, x2, x3;
    uint8_t temp[8];
    x0 = w[0];
    x1 = w[1];
    x2 = w[2];
    x3 = w[3];

    x0 |= (x0 << 16);
    x1 |= (x1 << 16);
    x2 |= (x2 << 16);
    x3 |= (x3 << 16);
    x0 &= (uint64_t) 0x0000FFFF0000FFFF;
    x1 &= (uint64_t) 0x0000FFFF0000FFFF;
    x2 &= (uint64_t) 0x0000FFFF0000FFFF;
    x3 &= (uint64_t) 0x0000FFFF0000FFFF;

    x0 |= (x0 << 8);
    x1 |= (x1 << 8);
    x2 |= (x2 << 8);
    x3 |= (x3 << 8);
    x0 &= (uint64_t) 0x00FF00FF00FF00FF;
    x1 &= (uint64_t) 0x00FF00FF00FF00FF;
    x2 &= (uint64_t) 0x00FF00FF00FF00FF;
    x3 &= (uint64_t) 0x00FF00FF00FF00FF;

    *q0 = x0 | (x2 << 8);
    *q1 = x1 | (x3 << 8);

    memcpy(temp, &x2, 8);
    for (int i = 0; i < 8; i++)
    {
        //printbyte(((uint8_t *) (temp)) + i);
        PrintHex(temp[i]);
    }
}

int main(void)
{
    uint64_t q0, q1;
    uint32_t zeros[4];

    PrintLine(start, sizeof(start));

    for (int i = 0; i < 4; i++)
        zeros[i] = 0;
    br_aes_ct64_interleave_in1(&q0, &q1, zeros);
    PrintLine(end, sizeof(end));
    endprogram();
    return 0;
}
