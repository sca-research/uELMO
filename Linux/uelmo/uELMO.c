#include "uelmo.h"

#include "Configure.h"
#include "core.h"
#include "EmuIO.h"
#include "Emulator.h"
#include "Memory.h"
#include <time.h>

//Print help message.
void PrintHelp()
{
    printf("uelmo ${TargetBinary} [OPTIONS]");
    printf("OPTIONS:\n");
    printf("\t-h : Print this message.\n");
    printf("\t-N ${n} : Set number of traces to ${n}.\n");
    printf("\t-o ${output} : Output into ${output}.\n");
    printf("\t--io : Enable IO support.\n");
    return;
}

//Read the arm binary file to ROM
void Read_Binary(char *filename)
{
    FILE *fp = fopen(filename, "rb");
    if (fp == NULL)
	{
	    printf("Error opening file [%s]\n", filename);
	    return;
	}
    memset(rom, 0xFF, sizeof(rom));
    memset(ram, 0x00, sizeof(ram));
    if (0 != fread(rom, 1, sizeof(rom), fp))
	{
	    perror(NULL);
	}
    fclose(fp);

    return;
}

//main function: dealing with command line input/output
//argv[0]=uELMO
//argv[1]=xxx.bin  -- target binary arm code 
// -o xxxx.dat --- output frame to xxxxx.dat
// -N xxxx --- generate xxxx traces
// -r xxxx.txt --- use randomness from xxxx.txt
int main(int argc, char *argv[])
{
    time_t timet;
    int ra = 0;
    int oindex = argc;
    int rindex = argc;

    fvr = false;
    ioSupported = false;
    N = 1;
    N_ind = 0;
    srand((unsigned)time(&timet));

    if (argc < 2)
	{
	    printf("bin file not specified\n");
	    PrintHelp();
	    return (1);
	}

    for (ra = 0; ra < argc; ra++)
	{
	    if (strcmp(argv[ra], "-h") == 0)
		{
		    PrintHelp();
		    exit(0);
		}
	    else if (strcmp(argv[ra], "-N") == 0)
		{
		    sscanf(argv[ra + 1], "%d", &N);
		}
	    else if (strcmp(argv[ra], "-o") == 0)
		{
		    oindex = ra + 1;
		}
	    else if (strcmp(argv[ra], "-r") == 0)
		{
		    rindex = ra + 1;
		}
	    else if (strcmp(argv[ra], "-fvr") == 0)
		{
		    fvr = true;
		}
	    else if (strcmp(argv[ra], "--io") == 0)
		{
		    ioSupported = true;
		}
	}

    //Load binary files to rom
    Read_Binary(argv[1]);
    //Open output file
    if (oindex < argc)
	Open_OutputFile(argv[oindex]);
    //Open data file
    if (rindex < argc)
	Open_DataFile(argv[rindex]);
#ifdef USE_SMURF
    if (ioSupported)
	{
	    sio = SioOpen(ELMO_IO_PATH);
	    SioWaitConn(sio);
	}
    else
	{
	    sio = NULL;
	}
#endif

    printf
	("########################################\n\nGENERATING TRACES...\n\n");
    for (N_ind = 0; N_ind < N; N_ind++)
	{
	    if (N_ind % 100 == 0)
		printf("########## TRACE %d\n", N_ind);
	    run();		//run one trace
	}

#ifdef USE_SMURF
    if (ioSupported)
	{
	    SioClose(sio);
	}
#endif
    //Close output file
    if (oindex < argc)
	Close_Output();
    //Open data file
    if (rindex < argc)
	Close_DataFile();

    //system("pause");
    return (0);
}
