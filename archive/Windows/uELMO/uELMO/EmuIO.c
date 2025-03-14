//This file describe the inpuut-output functions for the emulator
//i.e. need to be rewritten for SMURF
#include "Configure.h"
#include "core.h"
#include "EmuIO.h"
//global output file pointer
FILE* outfp=NULL;
//global input file pointer
FILE* datafp=NULL;
//Close output stream, executiong trace file
void Close_Output()//SMURF_ADAPTING, change this
{
	if(outfp!=NULL)
		fclose(outfp);
};
//Close input data stream, emulated input
void Close_DataFile()//SMURF_ADAPTING, change this
{
	if(outfp!=NULL)
		fclose(datafp);
}
//open output file, executiong trace file
void Open_OutputFile(char* filename)//SMURF_ADAPTING, change this
{
	outfp=fopen(filename,"wb+");
    if(outfp==NULL)
    {
        printf("Error opening file [%s]\n",outfp);
        return;
    }
}
//open input data file, emulated input
void Open_DataFile(char* filename)//SMURF_ADAPTING, change this
{
	datafp=fopen(filename,"r");
    if(outfp==NULL)
    {
        printf("Error opening file [%s]\n",datafp);
        return;
    }
}
//Get input from IO , emulated input
//SMURF_ADAPTING, change this
unsigned int Read_Byte()
{
	char *str;
	unsigned int data;
	size_t len = 20;
    str = (char *)malloc(len);
	//getline(&str, &len, datafile);//TEMP: get it back after moving back to Linux
	fgets(str,len,datafp);
    data = (int)strtol(str, NULL, 16);
    //printf("%x\n", data);
    free(str);
	return data;
}
//Get randomised input from IO (SMURF should not have this!!!)
//SMURF_ADAPTING, delete this!
unsigned int Rand_Byte()
{
	return rand()&0xff;
}

//Write out current cycle to Frame
//SMURF_ADAPTING, rewrite this
//Frame data in CORE_STATUS core_current
void Write_Frame()
{
	if(OnTrace==true)
	  fwrite(&core_current,sizeof(CORE_STATUS),1,outfp);
}
//Write out a flag that terminate the current trace
//SMURF_ADAPTING, rewrite this
void Write_EndofTrace()
{
	bool flag=false;
	fwrite(&flag,sizeof(bool),1,outfp);
}
