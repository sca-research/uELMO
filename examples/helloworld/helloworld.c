#include "helloworld.h"

#define MAX_LINE_LEN ((256))
#define TERMINATOR (('\0'))

static int ReadLine(unsigned char *line, int len)
{
    int i = 0;
    unsigned char c = 0;

    memset(line, 0, len);
    for (i = 0; i < len - 1; i++)
    {
        readbyte(&c);
        line[i] = c;

        //EOL
        if(('\n' == c) || ('\0' == c) || (0x04 == c))
        {
            break;
        }
    }

    return i;
}

static void PrintLine(unsigned char *line, int len)
{
    int i = 0;

    for (i = 0; i < len; i++)
    {
        printbyte(&line[i]);
    }

    return;
}

int main(void)
{
    const unsigned char helloworld[] = "hello,world\n";
    unsigned char line[MAX_LINE_LEN] = { 0 };

    starttrigger();

    //Helloworld.
    for (int i = 0; i < (int)sizeof(helloworld); i++)
    {
        printbyte(&helloworld[i]);
    }

    //Echo server.
    while (0 != ReadLine(line, MAX_LINE_LEN - 1))
    {
        if('\0' == line[0] || '\n' == line[0])
        {
            break;
        }
        PrintLine(line, MAX_LINE_LEN);
    }

    endtrigger();

    endprogram();
    return 0;
}
