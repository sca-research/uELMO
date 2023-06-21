#include "uelmo_gadget.h"
#include "elmoasmfunctionsdef.h"
#include "stdbool.h"

int share_n = 2;
int rnd_n = 1;


int main(void)
{

    uint8_t shares_a[4 * share_n];
    uint8_t shares_b[4 * share_n];
    uint8_t shares_ab[4 * share_n];
    uint8_t rnd[4 * rnd_n];
    uint8_t t_a = 0;
    uint8_t t_b = 0;
    int i;

    //Init t_a and t_b.
    //readbyte(&t_a);
    randbyte(&t_a);
    //readbyte(&t_b);
    randbyte(&t_b);


    //randbyte(shares_a);
    randbyte(shares_a + 4);
    shares_a[0] = t_a ^ shares_a[4];
    randbyte(&t_a);		//erase

    //randbyte(shares_b);
    randbyte(shares_b + 4);
    shares_b[0] = t_b ^ shares_b[4];
    randbyte(&t_b);		//erase

    // Receiving shares of a
    for (i = 0; i < share_n; i++)
	{
	    //shares_a[4*i] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
	    shares_a[4 * i + 1] = 0;
	    shares_a[4 * i + 2] = 0;
	    shares_a[4 * i + 3] = 0;
	}

    // Receiving shares of b
    for (i = 0; i < share_n; i++)
	{
	    //shares_b[4*i] = (uint8_t) scale_uart_rd(SCALE_UART_MODE_BLOCKING);
	    shares_b[4 * i + 1] = 0;
	    shares_b[4 * i + 2] = 0;
	    shares_b[4 * i + 3] = 0;
	}

    // Receiving random numbers
    for (i = 0; i < rnd_n; i++)
	{
	    randbyte(rnd + (4 * i));
	}

    //starttrigger(); // in .S file
    Isw_2(shares_a, shares_b, rnd, shares_ab);
    //endtrigger(); // in .S file
    endprogram();

    return 0;
}
