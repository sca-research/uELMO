#include "uelmo.h"

#include "Configure.h"
#include "core.h"
#include "EmuIO.h"
#include "Emulator.h"
#include "Memory.h"
#include <time.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef USE_SMURF
#include "smurf/smurf.h"
#include "symuelmo.h"
#include "ulang.h"
#endif

bool fvr = false;
int N = 0;
int N_ind = 0;
bool ioSupported = false;
bool useSmurfTrace = false;
bool useInputFile = false;
//bool uSymbolEnabled = false;
bool uSymbolEnabled = true;     //DBG

#ifdef USE_SMURF
SmurfIO *sio = NULL;
char *smftracepath = NULL;
char *siopath = NULL;
Smurf *smurf = NULL;
//const char * scriptpath = NULL;
const char *scriptpath = "../example/uelmo_gadget/isw2.set";    //DBG
#endif

uint32_t frameno = 0;
int cyclecount = 0;

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
    printf("\t-r ${input} : Use input file ${input}.\n");
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
static void Init_Smurf()
{
    if(useSmurfTrace)
    {
        smurf = InitSmurf(ELMO_CORE, smftracepath, SMURF_TRACE_MODE_CREATE);
        SmurfBind(smurf, "TraceNo", &N_ind);
        SmurfBind(smurf, "FrameNo", &frameno);

        //Bind core components.
#define Bind(x) SmurfBind(smurf, #x, &core_current.x)
        Bind(core_valid);
        Bind(reg);
        Bind(cpsr);
        Bind(F2D_instrreg);
        Bind(D2E_reg1);
        Bind(D2E_reg2);
        Bind(D2E_instrreg);
        Bind(cpsr_valid);
        Bind(cpsr_data);
        Bind(D2E_reg1_valid);
        Bind(D2E_reg2_valid);
        Bind(D2E_reg1_data);
        Bind(D2E_reg2_data);
        Bind(Fetch_instruction_new);
        Bind(Fetch_valid);
        Bind(Decode_port_regindex);
        Bind(Decode_port_data);
        Bind(Decode_destination_regindex);
        Bind(Decode_valid);
        Bind(glitchy_Decode_port_regindex);
        Bind(glitchy_Decode_port_data);
        Bind(Execute_Imm);
        Bind(Execute_ALU_result);
        Bind(Execute_destination_regindex);
        Bind(Execute_multicycle_regindex);
        Bind(Execute_valid);
        Bind(Read_valid);
        Bind(Read_type);
        Bind(Write_valid);
        Bind(Write_type);
        Bind(SignExtend_byte_valid);
        Bind(SignExtend_halfbyte_valid);
        Bind(Memory_read_targetreg);
        Bind(Memory_addr);
        Bind(Memory_data);
        Bind(Write_valid_delayed);
        Bind(Memory_writebuf_delayed);
        Bind(Memory_writebuf);
        Bind(Memory_readbuf);
        Bind(Read_reg_update);
        Bind(Memory_read_targetreg_buf);
        Bind(Memory_instr_disp);
        Bind(Decode_instr_disp);
        Bind(Execute_instr_disp);
#undef Bind
    }

    //Smurf IO init.
    if(ioSupported)
    {
        sio = SioOpen(siopath);
        INFO("#Waiting for connection...\n");
        SioWaitConn(sio);
    }
    else
    {
        sio = NULL;
    }

    if(uSymbolEnabled)
    {
        InitSymCore();
        InitScript(scriptpath);
    }

    return;
}

//Clean Smurf data structures.
static void CleanSmurf()
{
    if(uSymbolEnabled)
    {
        CleanScript();
        CleanSymCore();
    }

    if(ioSupported)
    {
        SioClose(sio);
    }
    if(useSmurfTrace)
    {
        FreeSmurf(smurf);
    }

    return;
}
#endif

//Read the arm binary file to ROM
void Read_Binary(char *filename)
{
    FILE *fp = fopen(filename, "rb");
    if(fp == NULL)
    {
        printf("Error opening file [%s]\n", filename);
        return;
    }
    memset(rom, 0xFF, sizeof(rom));
    memset(ram, 0x00, sizeof(ram));
    if(0 != fread(rom, 1, sizeof(rom), fp))
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

    if(argc < 2)
    {
        printf("bin file not specified\n");
        PrintHelp();
        return (1);
    }

    for (ra = 0; ra < argc; ra++)
    {
        if(strcmp(argv[ra], "-h") == 0)
        {
            PrintHelp();
            exit(0);
        }
        else if(strcmp(argv[ra], "-N") == 0)
        {
            sscanf(argv[ra + 1], "%d", &N);
            ra++;
        }
        else if(strcmp(argv[ra], "-o") == 0)
        {
            oindex = ra + 1;
        }
        else if(strcmp(argv[ra], "-r") == 0)
        {
            rindex = ra + 1;
            useInputFile = true;
        }
        else if(strcmp(argv[ra], "-fvr") == 0)
        {
            fvr = true;
        }
#ifdef USE_SMURF
        else if(strcmp(argv[ra], "--io") == 0)
        {
            ioSupported = true;
            siopath = argv[ra + 1];
            ra++;
        }
        else if(strcmp(argv[ra], "--st") == 0)
        {
            useSmurfTrace = true;
            smftracepath = argv[ra + 1];
            ra++;
        }
#endif
    }

#ifdef USE_SMURF
    //Initialise Smurf library.
    Init_Smurf();
#endif

    //Load binary files to rom
    Read_Binary(argv[1]);
    //Open output file
    if(oindex < argc)
        Open_OutputFile(argv[oindex]);
    //Open data file
    if(rindex < argc)
        Open_DataFile(argv[rindex]);

    printf
        ("########################################\n\nGENERATING TRACES...\n\n");
    for (N_ind = 0; N_ind < N; N_ind++)
    {
        frameno = 0;            //Reset Frame counter.
        cyclecount = 0;

        if(N_ind % 100 == 0)
            printf("########## TRACE %d\n", N_ind);
        run();                  //run one trace
    }
    //Close output file
    if(oindex < argc)
        Close_Output();
    //Open data file
    if(rindex < argc)
        Close_DataFile();

    //system("pause");
#ifdef USE_SMURF
    CleanSmurf();
#endif
    return (0);
}
