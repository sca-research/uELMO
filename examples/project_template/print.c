#include <stdint.h>

#include "elmoasmfunctionsdef.h"
#include "print.h"

//Nibble to hex.
inline static char ntohex(int nib)
{
    if(0xA > nib)
    {
        return '0' + nib;
    }
    else
    {
        return 'A' + nib - 0xA;
    }
    return 0;
}

//uint8 to hex.
inline static void u8tohex(uint8_t in, char *out)
{
    out[0] = ntohex(in >> 4);
    out[1] = ntohex(in & 0x0F);
    return;
}

//Print a char.
void PrintChar(unsigned char u8)
{
    char bytestr[2] = { 0 };
    u8tohex(u8, bytestr);
    printbyte((unsigned char *)&bytestr[0]);
    printbyte((unsigned char *)&bytestr[1]);
    return;
}

//Print an u32 int.
void PrintInt(uint32_t u32)
{
    int i;
    const uint8_t *u8 = (void *)&u32;

    for (i = 0; i < 4; i++)
    {
        PrintChar(u8[3 - i]);
    }

    return;
}

//Print a string of length len.
void PrintStr(const char *str, int len)
{
    int i;
    const char *c;
    for (c = str, i = 0; i < len; c++, i++)
    {
        printbyte((unsigned char *)c);
    }
    return;
}
