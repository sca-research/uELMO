
//
//  PQCgenKAT_kem.c
//
//  Created by Bassham, Lawrence E (Fed) on 8/29/17.
//  Copyright © 2017 Bassham, Lawrence E (Fed). All rights reserved.
//
#include <stdio.h>
#include <stdlib.h>
//#include <string.h>
//#include <ctype.h>
#include "rng.h"
#include "api.h"

#include "elmoasmfunctionsdef.h"

#define	MAX_MARKER_LEN		50
#define KAT_SUCCESS          0
#define KAT_FILE_OPEN_ERROR -1
#define KAT_DATA_ERROR      -3
#define KAT_CRYPTO_FAILURE  -4

void PrintLine(const char *line, int len)
{
    int i = 0;

    for (i = 0; i < len; i++)
    {
        printbyte((unsigned char *)&line[i]);
    }

    return;
}

char NibToHex(const char x)
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

void PrintHex(const char x)
{
    unsigned char xl, xh;

    xl = NibToHex(x & 0x0F);
    xh = NibToHex((x & 0xF0) >> 4);

    printbyte(&xh);
    printbyte(&xl);

    return;
}

//#include "aes.h"
void br_aes_ct64_interleave_in1(uint64_t * q0, uint64_t * q1,
                                const uint32_t * w)
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
        PrintHex(temp[i]);
    }

}

int main()
{
    //char                fn_req[32], fn_rsp[32];
    //FILE                *fp_req, *fp_rsp;
    uint8_t entropy_input[48];
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES],
        ss1[CRYPTO_BYTES];
    //int                 count;
    //int                 done;
    unsigned char pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
    int ret_val;
    uint8_t res;

    for (int i = 0; i < 48; i++)
        readbyte(entropy_input + i);
    //entropy_input[i]=i;
    randombytes_init(entropy_input, NULL, 256);

    //randombytes(seed,48);
    //randombytes_init(seed,NULL,256);
    //printf("# %s\n\n", CRYPTO_ALGNAME);
    // Generate the public/private keypair
    if((ret_val = crypto_kem_keypair(pk, sk)) != 0)
    {
        //printf("crypto_kem_keypair returned <%d>\n", ret_val);
        return KAT_CRYPTO_FAILURE;
    }
    //for(int i=0;i<CRYPTO_BYTES;i++)
    //  printbyte(sk+i);
    //printBstr("pk = ", pk, CRYPTO_PUBLICKEYBYTES);
    //printBstr("sk = ", sk, CRYPTO_SECRETKEYBYTES);
    if((ret_val = crypto_kem_enc(ct, ss, pk)) != 0)
    {
        //printf("crypto_kem_enc returned <%d>\n", ret_val);
        return KAT_CRYPTO_FAILURE;
    }

    //printBstr( "ct = ", ct, CRYPTO_CIPHERTEXTBYTES);
    //printBstr("ss = ", ss, CRYPTO_BYTES);

    //printf("\n");
/*
    if ( (ret_val = crypto_kem_dec(ss1, ct, sk)) != 0) {
          //printf("crypto_kem_dec returned <%d>\n", ret_val);
          //return KAT_CRYPTO_FAILURE;
           endprogram();
    }
;
    if ( memcmp(ss, ss1, CRYPTO_BYTES) ) {
          //printf("crypto_kem_dec returned bad 'ss' value\n");
              endprogram();
          //return KAT_CRYPTO_FAILURE;
    }
    */

    printbyte("\n");

    endprogram();
    return 0;

}
