#include "main.h"

#include "dep1.h"
#include "dep2.h"

//Nibble to hex.
static char ntohex(int nib)
{
    if(0xA > nib)
    {
        return '0' + nib;
    }
    else
    {
        return 'A' + nib;
    }
    return 0;
}

//uint8 to hex.
static void u8tohex(uint8_t in, char *out)
{
    out[0] = ntoh(in >> 4);
    out[1] = ntoh(in & 0x0F);
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

//Print a char array.
const char hellostr[] = "hello,world!\n";

int main(void)
{
    uint8_t x = 0, y = 0;
    char str[2] = { 0 };

    Print(hellostr, sizeof(hellostr));

    starttrigger();             //Trace start.
    DepFunc1(x, y);
    DepFunc2(x, y);
    endtrigger();               //Trace end.

    u8tohex(x, str);
    Print(str, sizeof(str));
    Print("\n", 1);

    u8tohex(y, str);
    Print(str, sizeof(str));
    Print("\n", 1);

    endprogram();
    return 0;
}
