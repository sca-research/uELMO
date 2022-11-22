#define NOTRACES 20000

#define AUTON			//Automaticially decide the number of traces N
#include "byte_mask_aes.h"

#include <stdio.h>
#include <stdlib.h>
#include "elmoasmfunctionsdef.h"

//Trivial implementation of byte-wise AES masking scheme from the DPA Book
//For ELMO: 
//Triggered Perfiod=first round
//Instruction Count=1012
//./elmo ${DIRECTORY}/ELMO/byte_mask_aes.bin -NTrace 10000

/******************************************************************/
//       AES masked encryption                                   //
/******************************************************************/
void aes128(uint8_t * state)
{

    init_masking();

    remask(state, Mask[6], Mask[7], Mask[8], Mask[9], 0, 0, 0, 0);

    starttrigger();
    addRoundKey_masked(state, 0);

    uint8_t i;

    for (i = 1; i < 10; i++)
	{
	    subBytes_masked(state);

	    shiftRows(state);

	    remask(state, Mask[0], Mask[1], Mask[2], Mask[3], Mask[5], Mask[5],
		   Mask[5], Mask[5]);
	    //remask(state,Mask[5],Mask[5],Mask[5],Mask[5],0,0,0,0);
	    //remask(state,Mask[0],Mask[1],Mask[2],Mask[3],0,0,0,0);  

	    mixColumns(state);

	    addRoundKey_masked(state, i);
	    if (i == 1)
		endtrigger();

	}

    subBytes_masked(state);
    shiftRows(state);

    addRoundKey_masked(state, 10);

}

int main()
{

    uint8_t *input, *output, *key;
    uint32_t i, j;
    uint32_t N;
    key = malloc(16 * sizeof(uint8_t));
    input = malloc(16 * sizeof(uint8_t));
    output = malloc(16 * sizeof(uint8_t));

    static const uint8_t fixedkey[16] =
	{ 0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef, 0x12, 0x34, 0x56,
	0x78, 0x9a, 0xbc, 0xde, 0xf0
    };
    static const uint8_t fixedinput[16] =
	{ 0xda, 0x39, 0xa3, 0xee, 0x5e, 0x6b, 0x4b, 0x0d, 0x32, 0x55, 0xbf,
	0xef, 0x95, 0x60, 0x18, 0x90
    };

    KeyExpansion(fixedkey);
    //Plaintext
    for (j = 0; j < 16; j++)
	{
	    readbyte(input + j);
	}
    //Random masks
    for (j = 0; j < 6; j++)
	{
	    randbyte(Mask + j);
	}

    //Encryption
    aes128(input);
    //output
    for (j = 0; j < 16; j++)
	{
	    printbyte(input + j);
	}

    endprogram();

    return 0;
}
