

#include "elmoasmfunctionsdef.h"
#include <stdint.h>
extern void ISWd2(uint32_t*,uint32_t*,uint32_t*);
int main() {

  uint8_t plain[16];
  uint32_t input[4];
  uint32_t output[2];
  uint32_t random;
  uint8_t t=0;
  int i;
  long j;
  long N=1000;
  for(j=0;j<N;j++) 
  {
		for (i=0;i<16;i++)
		{
			randbyte(plain+i);
		}
		for (i=0;i<4;i++)
		{
			input[i]=plain[4*i]^(plain[4*i+1]<<8)^(plain[4*i+2]<<16)^(plain[4*i+3]<<24);
		}
		if(j>N/2)
                    input[0]=input[1];
                for (i=0;i<4;i++)
		    randbyte(plain+i);
		random=plain[0]^(plain[1]<<8)^(plain[2]<<16)^(plain[3]<<24);
		ISWd2(input,&random,output);
    	
  }
  endprogram();
  return 0;
}
