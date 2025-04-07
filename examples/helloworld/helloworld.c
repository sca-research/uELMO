#include "helloworld.h"
#include <string.h>
#include <stdbool.h>

#define MAX_LINE_LEN ((256))
#define TERMINATOR (("exit\n"))

static int ReadLine(char *line, int len)
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
            i++;
            break;
        }
    }

    return i;
}

static void PrintLine(char *line, int len)
{
    int i = 0;

    for (i = 0; i < len; i++)
    {
        printbyte((uint8_t *) & line[i]);
        if(line[i] == '\0' || line[i] == '\n')
        {
            break;
        }
    }

    return;
}

int main(void)
{
    int nread = 0;
    char line[MAX_LINE_LEN] = { 0 };

    PrintLine("hello,world\n", MAX_LINE_LEN);

    starttrigger();

    //Echo server.
    while (true)
    {
        memset(line, 0, sizeof(line));
        nread = ReadLine(line, MAX_LINE_LEN - 1);
        if(0 == nread)
        {
            //Connection broke.
            continue;
        }

        //Control commands.
        if(!strncmp(line, "\n", 1))
        {
            PrintLine("ACK\n", MAX_LINE_LEN);
            continue;
        }
        else if(!strncmp(line, TERMINATOR, strlen(TERMINATOR)))
        {
            PrintLine("Server closed.\n", MAX_LINE_LEN);
            break;
        }
        else
        {
            PrintLine(line, MAX_LINE_LEN);
        }
    }

    endtrigger();

    endprogram();
    return 0;
}
