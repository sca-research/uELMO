
#include "Config.h"
#include "Write_LeakageState.h"
#include "LeakageModel.h"
FILE* outfp;
/*
*	Format:
*   Traceheader: len(Instr1)->Instr1->Leakage type:0x0 (full) or 0x1 (linear)->len(leakage_label)->leakage_label->...->Leakage type:0xff (end
of sample)->next instruction->...->len(Instr_n)==0 means the end of trace header
*	Trace: Leakage type:0x0 (full) or 0x1 (linear)->len(leakage_data)->leakage_data->...->Leakage type:0xff (end
of sample)->...->Leakage type 0xfe (end of trace)
*/

void OpenLeakageFile(char* filename)
{
	outfp = fopen(filename, "wb");
	if (outfp == NULL)
		printf("Cannot open leakage file %s!",filename);
}


void CloseLeakageFile()
{
	if (outfp != NULL)
		fclose(outfp);
}

//a string that constains the discription of the leakage node
void Write_string(char* str)
{
	uint8_t len = strlen(str);//length include the `\0`
	fwrite(&len, sizeof(uint8_t), 1, outfp);//write out length
	fwrite(str, sizeof(uint8_t), len, outfp);//write out the string
}
//Type 0: full leakage
//Type 1: linear leakage
//Type 0xfe: end of trace
//Type 0xff: end of sample
void Write_leakage_label(char* str, uint8_t type)
{
	uint8_t len;
	fwrite(&type, sizeof(uint8_t), 1, outfp);
	if ((type == 0xff) || (type == 0xfe))//end of trace or sample
		return;
	len = strlen(str);//length include the `\0`
	fwrite(&len, sizeof(uint8_t), 1, outfp);//write out length
	fwrite(str, sizeof(uint8_t), len, outfp);//write out the label
}
void Write_headender()
{
	uint8_t mark = 0;
	fwrite(&mark, sizeof(uint8_t), 1, outfp);
}
void Write_frameender()
{
	uint8_t mark = 0xff;
	fwrite(&mark, sizeof(uint8_t), 1, outfp);
}
void Write_traceender()
{
	uint8_t mark = 0xfe;
	fwrite(&mark, sizeof(uint8_t), 1, outfp);
}
//Type 0: full leakage
//Type 1: linear leakage
//Type 0xfe: end of trace
//Type 0xff: end of cycle
void Write_leakage_data(uint8_t* data, uint8_t len, uint8_t type)
{

	if ((type != 0) && (type != 1))
	{
		printf("Error! type=%d\n",type);
		return;
	}
	if (FORCE_LINEAR)
		type = 1;
	fwrite(&type, sizeof(uint8_t), 1, outfp);
	fwrite(&len, sizeof(uint8_t), 1, outfp);//write out length
	fwrite(data, sizeof(uint8_t), len, outfp);//write out the label
}
void Write_Instr(char* disp)
{
	Write_string(disp);
}

