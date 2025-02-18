#include "main.h"
#include "print.h"

#include "MaskedAES_R1.h"

int main(void)
{
    const char hellostr[] = "hello,world!\n";
    uint8_t m[16] = { 0 }, c[16] = { 0 };

    starttrigger();             //Trace start.

    PrintStr(hellostr, sizeof(hellostr));
    PrintInt(0x0123ABCD);
    PrintStr("\n", 1);
    AES_encrypt(m, c);

    endtrigger();               //Trace end.

    endprogram();
    return 0;
}
