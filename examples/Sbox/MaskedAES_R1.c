#include <stdint.h>
#include "MaskedAES_R1.h"

#if 0
void AES_encrypt(uint8_t * m, uint8_t * c)
{
	uint8_t temp[16];
	for (int j = 0; j < 16; j++) {
		m[j] = 0;
		temp[j] = 0;
	}

	MaskingKey(RoundKey, temp);
	MADK(c, temp);
	MSbox(c);
	/*for(int i=0;i<10;i++)
	   {
	   MSbox(c);

	   MShiftRow(c);

	   if(i!=9)
	   {

	   MMixColumn(c, m);

	   MaskingKey(RoundKey+(i+1)*16, temp);

	   MADK(m,temp);

	   SafeCopy(m,c);

	   }
	   else
	   {
	   MaskingKey(RoundKey+(i+1)*16, temp);
	   MADK(c,temp);
	   SafeCopy(c,m);

	   }

	   }
	 */
	SafeCopy(c, m);
	Finalize(m, c);

}

int main()
{
	uint8_t plain[16];
	uint8_t cipher[16];
	uint8_t key[16] = { 0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
		0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
	};

	U = 0;
	V = 0;
	UV = 0;

	for (int i = 0; i < 16; i++) {
		readbyte(plain + i);
		//plain[i]=(plain[i]&0x3)^((plain[i]&0x3)<<2)^((plain[i]&0x3)<<4)^((plain[i]&0x3)<<6);
	}
	randbyte(&U);
	//U=(U&0x3)^((U&0x3)<<2)^((U&0x3)<<4)^((U&0x3)<<6);
	randbyte(&V);
	//V=(V&0x3)^((V&0x3)<<2)^((V&0x3)<<4)^((V&0x3)<<6);
	//SRMask=(target_uart_rd()<<24)|(target_uart_rd()<<16)|(target_uart_rd()<<8)|(target_uart_rd());
	SRMask = 0;
	KeyExpansion(key);
	GenMaskedSbox();
	MaskingPlaintext(plain, cipher);
	AES_encrypt(plain, cipher);

	endprogram();
	return 0;
}
#endif

int main(void)
{
	const unsigned char helloworld[] = "hello,world";

	starttrigger();
	for (int i = 0; i < (int)sizeof(helloworld); i++) {
		printbyte(&helloworld[i]);
	}
	endtrigger();

	endprogram();
	return 0;
}
