#include "Config.h"
#include "../../uELMO/uELMO/core.h"
#include "FrameReader.h"

//Execution file name
FILE* exefile_fp = NULL;

//open output file
void Open_Exefile(char* filename)
{
	exefile_fp = fopen(filename, "rb");
	if (exefile_fp == NULL)
	{
		printf("Error opening file [%s]\n", filename);
		exit(0);
	}
}
//Close output stream
void Close_Exefile()
{
	if (exefile_fp != NULL)
		fclose(exefile_fp);
};
//Read in one Frame/cycle
//Require space allocation before calling
void Read_Frame(CORE_STATUS* frame)
{
	fread(&(frame->core_valid), sizeof(bool), 1, exefile_fp);
	if (frame->core_valid == false)
		return;//get to end of one trace
	//move back the file pointer
	fseek(exefile_fp, -1*((long)sizeof(bool)), SEEK_CUR);
	//read in 
	fread(frame, sizeof(CORE_STATUS), 1, exefile_fp);
	return;
}

//check if reach the end of execution file, i.e. all traces have been read already
bool IsEof()
{
	char c;
	//printf("place=0x%lX\n", ftell(exefile_fp));
	fread(&c, 1, 1, exefile_fp);
	if (feof(exefile_fp) == 0)
	{
		fseek(exefile_fp, -1L, SEEK_CUR);
		return false;
	}	
	else
	{
		return true;
	}

}

//point back to begining, for print out header
void Rewind()
{
	fseek(exefile_fp, 0L, SEEK_SET);
}