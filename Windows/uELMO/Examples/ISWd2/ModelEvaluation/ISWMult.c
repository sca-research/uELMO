

#include "elmoasmfunctionsdef.h"
#include <stdint.h>
extern void ISWd2(uint32_t*,uint32_t*,uint32_t*);
int main() {

  uint8_t plain[5];
  uint32_t input[4];
  uint32_t output[2];
  uint32_t random;
  uint8_t t=0;
  int i;

		for (i=0;i<4;i++)
		{
			readbyte(plain+i);
			plain[i]=(plain[i]&0x3)^((plain[i]&0x3)<<2)^((plain[i]&0x3)<<4)^((plain[i]&0x3)<<6);
			input[i]=plain[i]^(plain[i]<<8)^(plain[i]<<16)^(plain[i]<<24);
		}
                readbyte(plain+4);
		plain[4]=(plain[4]&0x3)^((plain[4]&0x3)<<2)^((plain[4]&0x3)<<4)^((plain[4]&0x3)<<6);
	        random=plain[4]^(plain[4]<<8)^(plain[4]<<16)^(plain[4]<<24);
		readbyte(&t);//clear the interface
		ISWd2(input,&random,output);
    	
  endprogram();
  return 0;
}
