#include "main.h"
#include "print.h"

int main(void)
{
    const char hellostr[] = "hello,world!\n";

    starttrigger();             //Trace start.
    PrintStr(hellostr, sizeof(hellostr));
    PrintInt(0x0123ABCD);
    PrintStr("\n", 1);
    endtrigger();               //Trace end.
                                
    endprogram();
    return 0;
}
