#ifndef MASKEDAES_FULL_H
#define MASKEDAES_FULL_H
#include "elmoasmfunctionsdef.h"

#include  <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define Nb 4
#define keyExpSize 176
#define Nk 4                    // The number of 32 bit words in a key.
#define KEYLEN 16               // Key length in bytes
#define Nr 10                   // The number of rounds in AES Cipher.

extern unsigned char S[256];

extern unsigned char MaskedS[256];

extern unsigned char xtime[256];

extern unsigned char rcon[30];

// The round constant word array, Rcon[i], contains the values given by 
// x to th e power (i-1) being powers of x (x is denoted as {02}) in the field GF(2^8)
extern uint8_t Rcon[11];

extern unsigned char xtime_8bconst[2];
extern unsigned long xtime_const[3];

extern unsigned char U, V, UV;
extern unsigned long SRMask;
extern uint8_t RoundKey[keyExpSize];

uint8_t getSBoxValue(uint8_t);
void GenMaskedSbox(void);
void MaskingPlaintext(unsigned char *input, unsigned char *output);
void MaskingKey(unsigned char *input, unsigned char *output);
void MSbox(unsigned char *input);
void MADK(unsigned char *input, unsigned char *key);
void MShiftRow(unsigned char *input);
void MMixColumn(unsigned char *input, unsigned char *output);
void Finalize(unsigned char *input, unsigned char *output);
void SafeCopy(unsigned char *input, unsigned char *output);
void KeyExpansion(uint8_t * Key);
void AES_encrypt(uint8_t * m, uint8_t * c);

#endif
