

#include "elmoasmfunctionsdef.h"
#include <stdint.h>

extern void ISWd3(uint32_t*,uint32_t*);
extern void ISWd3_leak(uint32_t*,uint32_t*);
int main() {

  uint32_t input[6];
  uint32_t random[3];
  uint8_t plain[6];
  int i;
		for (i=0;i<6;i++)
		{
			randbyte(plain+i);
		}
		for (i=0;i<6;i++)
		{
			input[i]=plain[i];
		}
                for (i=0;i<3;i++)
		    randbyte(plain+i);
		for (i=0;i<3;i++)
		{
			random[i]=plain[i];
		}
		ISWd3(random,input);

    	        plain[0]=0xff&(input[0]^input[1]^input[2]);
		plain[1]=0xff&(input[3]^input[4]^input[5]);
		plain[2]=0xff&(random[0]^random[1]^random[2]);
		plain[3]=plain[0]&plain[1];
		for(i=0;i<4;i++)
			printbyte(plain+i);

  endprogram();

  return 0;
}
