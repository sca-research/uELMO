#ifndef EMUIO_H_
#define EMUIO_H_
#include <stdint.h>

//open output file
void Open_OutputFile(char *);
//open input data file
void Open_DataFile(char *);
//Write out current cycle to Frame
void Write_Frame();
//Write out a flag that terminate the current trace
void Write_EndofTrace();

//Close output stream
void Close_Output();
//Close input data stream
void Close_DataFile();
//Get input from IO 
unsigned int Read_Byte();
void Write_Byte(uint8_t);

//Get randomised input from IO (SEAL should not have this!!!)
#ifndef SEAL
unsigned int Rand_Byte();
#endif
#endif
