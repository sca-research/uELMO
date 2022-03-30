#include "uelmo.h"

#include "Configure.h"
#include "core.h"
#include "EmuIO.h"
#include "Emulator.h"
#include "Memory.h"
#include <time.h>
#include <stdbool.h>

bool ioSupported = false;
bool useSmurfTrace = false;
bool useInputFile = false;

SmurfIO *sio = NULL;
SmurfCore *smfcore = NULL;
SmurfTrace *smftrace = NULL;
SmurfTraceFrame *smfframe = NULL;
char *smftracepath = NULL;
char *siopath = NULL;

//Print help message.
void PrintHelp()
{
#ifdef USE_SMURF
    printf("smuelmo ${TargetBinary} [OPTIONS]");
#else
    printf("uelmo ${TargetBinary} [OPTIONS]");
#endif
    printf("OPTIONS:\n");
    printf("\t-h : Print this message.\n");
    printf("\t-N ${n} : Set number of traces to ${n}.\n");
    printf("\t-o ${output} : Output into ${output}.\n");
#ifdef USE_SMURF
    printf("Smurf Extensions:\n");
    printf
	("\t--io ${IFPATH}: Enable IO support at the path given by ${IFPATH}.\n");
    printf
	("\t--st ${SMURF_TRACE_PATH}: Smurf trace output at ${SMURF_TRACE_PATH}.\n");
#endif
    return;
}

#ifdef USE_SMURF
//Print Core info.
void PrintCoreInfo(SmurfCore * core)
{
    int i = 0;
    SmurfCoreComponent *scc = NULL;

    printf("Core version: %s\n", core->version);
    for (i = 0; i < core->ncomponents; i++)
	{
	    scc = core->components[i];
	    printf("Component [%02d]: %s\n", i, scc->name);
	    printf("\t Type: %s\n", SccGetTypeStr(scc->type));
	    printf("\t Length: %lu\n", scc->len);
	}

    return;
}

//Initialise Smurf data structures.
static void InitSmurf()
{
    if (useSmurfTrace)
	{
	    //Read Smurf Core Specification.
	    smfcore = ScLoadCore("./smurffiles/uelmo.json");
#if DBG
	    PrintCoreInfo(smfcore);
#endif

	    //Init Smurf Trace output.
	    smftrace = StOpen(smftracepath, smfcore, SMURF_TRACE_MODE_CREATE);

	    //Init Smurf Trace Frame.
	    smfframe = StNewFrame(smfcore);

	    //Init Smurf Frame Indexes.
	    StfGetFrameIndex(smfframe, &smftidx.traceno, "TraceNo");
#define GetIndex(x) StfGetFrameIndex(smfframe, &smftidx.x, #x)
	    {
		GetIndex(core_valid);
		GetIndex(reg);
		GetIndex(cpsr);
		GetIndex(F2D_instrreg);
		GetIndex(D2E_reg1);
		GetIndex(D2E_reg2);
		GetIndex(D2E_instrreg);
		GetIndex(cpsr_valid);
		GetIndex(cpsr_data);
		GetIndex(D2E_reg1_valid);
		GetIndex(D2E_reg2_valid);
		GetIndex(Fetch_instruction_new);
		GetIndex(Fetch_valid);
		GetIndex(Decode_port_regindex);
		GetIndex(Decode_port_data);
		GetIndex(Decode_destination_regindex);
		GetIndex(Decode_valid);
		GetIndex(glitchy_Decode_port_regindex);
		GetIndex(glitchy_Decode_port_data);
		GetIndex(Execute_Imm);
		GetIndex(Execute_ALU_result);
		GetIndex(Execute_destination_regindex);
		GetIndex(Execute_multicycle_regindex);
		GetIndex(Execute_valid);
		GetIndex(Read_valid);
		GetIndex(Read_type);
		GetIndex(Write_valid);
		GetIndex(Write_type);
		GetIndex(SignExtend_byte_valid);
		GetIndex(SignExtend_halfbyte_valid);
		GetIndex(Memory_read_targetreg);
		GetIndex(Memory_addr);
		GetIndex(Memory_data);
		GetIndex(Write_valid_delayed);
		GetIndex(Memory_writebuf_delayed);
		GetIndex(Memory_writebuf);
		GetIndex(Memory_readbuf);
		GetIndex(Read_reg_update);
		GetIndex(Memory_read_targetreg_buf);
		GetIndex(Memory_instr_disp);
		GetIndex(Decode_instr_disp);
		GetIndex(Execute_instr_disp);
	    }
#undef GetIndex
	}

    //Smurf IO init.
    if (ioSupported)
	{
	    sio = SioOpen(siopath);
	    INFO("#Waiting for connection...\n");
	    SioWaitConn(sio);
	}
    else
	{
	    sio = NULL;
	}

    return;
}

//Clean Smurf data structures.
static void CleanSmurf()
{
    if (ioSupported)
	{
	    SioClose(sio);
	}
    if (useSmurfTrace)
	{
	    StDeleteFrame(smfframe);
	    StClose(smftrace);
	    ScDeleteCore(smfcore);
	}
    return;
}
#endif

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
		    ra++;
		}
	    else if (strcmp(argv[ra], "-o") == 0)
		{
		    oindex = ra + 1;
		}
	    else if (strcmp(argv[ra], "-r") == 0)
		{
		    rindex = ra + 1;
		    useInputFile = true;
		}
	    else if (strcmp(argv[ra], "-fvr") == 0)
		{
		    fvr = true;
		}
#ifdef USE_SMURF
	    else if (strcmp(argv[ra], "--io") == 0)
		{
		    ioSupported = true;
		    siopath = argv[ra + 1];
		    ra++;
		}
	    else if (strcmp(argv[ra], "--st") == 0)
		{
		    useSmurfTrace = true;
		    smftracepath = argv[ra + 1];
		    ra++;
		}
#endif
	}

#ifdef USE_SMURF
    //Initialise Smurf library.
    InitSmurf();
#endif

    //Load binary files to rom
    Read_Binary(argv[1]);
    //Open output file
    if (oindex < argc)
	Open_OutputFile(argv[oindex]);
    //Open data file
    if (rindex < argc)
	Open_DataFile(argv[rindex]);

    printf
	("########################################\n\nGENERATING TRACES...\n\n");
    for (N_ind = 0; N_ind < N; N_ind++)
	{
	    if (N_ind % 100 == 0)
		printf("########## TRACE %d\n", N_ind);
	    run();		//run one trace
	}
    //Close output file
    if (oindex < argc)
	Close_Output();
    //Open data file
    if (rindex < argc)
	Close_DataFile();

    //system("pause");
#ifdef USE_SMURF
    CleanSmurf();
#endif
    return (0);
}
