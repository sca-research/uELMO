#ifndef MEMORY_H_
#define MEMORY_H_

#include <stdint.h>
#include <stdbool.h>

#define ROMADDMASK 0xFFFFF
#define RAMADDMASK 0xFFFFF

#define ROMSIZE (ROMADDMASK+1)
#define RAMSIZE (RAMADDMASK+1)

extern unsigned short rom[ROMSIZE >> 1];
extern unsigned short ram[RAMSIZE >> 1];

//Read 16 bits, RAM or ROM
unsigned int fetch16(unsigned int);
//Read 32 bits, RAM or ROM
unsigned int fetch32(unsigned int);

//Write 16 bits, RAM
void write16(unsigned int, unsigned int);
//Write 32 bits, RAM
void write32(unsigned int, unsigned int);

//Read 16 bits, No ELMO functions, only for RAM or ROM
unsigned int read16(unsigned int);
//Read 32 bits, RAM +ROM+ ELMO defined functions (e.g. readbyte, randbyte, etc.)
unsigned int read32(unsigned int);

//Read byte; from read16
uint8_t read8(unsigned int);

unsigned int read32(unsigned int);
//One cycle of memory access
bool Memory_OneCycle();
#endif
