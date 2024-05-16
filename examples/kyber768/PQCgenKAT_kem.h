#ifndef PQCGENKAT_KEM_H
#define PQCGENKAT_KEM_H
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

#endif
