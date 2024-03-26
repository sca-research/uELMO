#ifndef EMUIO_H_
#define EMUIO_H_
#include <stdint.h>

void Write_Frame();

unsigned int Read_Byte();
void Write_Byte(uint8_t);

//Get randomised input from IO (SEAL should not have this!!!)
#ifndef SEAL
unsigned int Rand_Byte();
#endif
#endif
