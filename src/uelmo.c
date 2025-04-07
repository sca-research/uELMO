#include "uelmo.h"

#include "Configure.h"
#include "core.h"
#include "EmuIO.h"
#include "Emulator.h"
#include "Memory.h"
#include <time.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef USE_SEAL
#include "seal/seal.h"
#include "symuelmo.h"
#include "ulang.h"
#endif

bool fvr = false;
int N = 0;
int N_ind = 0;
bool ioSupported = false;
bool useSealTrace = true;
bool useInputFile = false;
bool useScript = false;
bool verbose = false;

//global flag that shows whether the current cycle is on the trace
bool OnTrace = false;

#ifdef USE_SEAL
SealVirtualPort *sealport = NULL;
char *sealtracepath = "/dev/null";      //Use NULL device by default.
char *portpath = NULL;
Seal *seal = NULL;
const char *scriptpath = NULL;  //DBG
char dictpath[MAX_PATH_LAN] = { 0 };
#endif

uint32_t frameno = 0;
int cyclecount = 0;

bool oflag = false;

//Check cmd args.
static bool ArgsValid(const int argc, char *argv[])
{
    int i = 0;

    //Number of args.
    if(2 > argc)
    {
        return false;
    }
    else                        //Help option.
    {
        for (i = 1; i < argc; i++)
        {
            if((0 == strncmp("-h", argv[i], 255))
               || (0 == strncmp("--help", argv[i], 255)))
            {
                return false;
            }
        }
    }

    return true;
}

//Print help message.
void PrintHelp()
{
#ifdef USE_SEAL
    printf("smuelmo ${TargetBinary} [OPTIONS]");
#else
    printf("uelmo ${TargetBinary} [OPTIONS]");
#endif
    printf("OPTIONS:\n");
    printf("\t-h|--help : Print this message.\n");
    printf("\t-N ${n} : Set number of traces to ${n}.\n");
    //printf("\t-o ${output} : Original uELMO output into ${output}.\n");
    //printf("\t-r ${input} : Use input file ${input}.\n");
    printf("\t--verbose : Print verbose emulation log.\n");
#ifdef USE_SEAL
    printf("Seal Extensions:\n");
    printf
        ("\t--io ${IFPATH}: Enable IO support at the path given by ${IFPATH}.\n");
    printf
        ("\t--st ${SEAL_TRACE_PATH}: Seal trace output at ${SEAL_TRACE_PATH}.\n");
    printf("\t--sc ${SCRIPT_PATH}: Use ULANG script at ${SCRIPT_PATH}.\n");
#endif
    return;
}

#ifdef USE_SEAL
//Print Core info.
void PrintCoreInfo(SealCore *core)
{
    int i = 0;
    SealCoreComponent *scc = NULL;

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

//Initialise Seal data structures.
static void Init_Seal()
{
    seal = InitSeal(ELMO_CORE, sealtracepath, SEAL_TRACE_MODE_CREATE);

    if(useSealTrace)
    {
        SealBind(seal, "TraceNo", &N_ind);
        SealBind(seal, "FrameNo", &frameno);

        //Bind core components.
#define Bind(x) SealBind(seal, #x, &core_current.x)
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

    //Seal IO init.
    if(ioSupported)
    {
        SealCleanPort(portpath);
        if(NULL == (sealport = SealOpenPort(portpath)))
        {
            INFO("#Failed to initiate SEAL port.");
        }
    }
    else
    {
        sealport = NULL;
    }

    if(useScript)
    {
        InitSymCore();
        InitScript(scriptpath);
    }

    return;
}

//Clean Seal data structures.
static void CleanSeal()
{
    if(useScript)
    {
        ExportEncDict(uDict, dictpath); //DBG
        CleanScript();
        CleanSymCore();
    }

    if(ioSupported)
    {
        SealClosePort(&sealport);
    }

    if(useSealTrace)
    {
        FreeSeal(seal);
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
    if(0 == fread(rom, 1, sizeof(rom), fp))
    {
        perror(NULL);
    }
    fclose(fp);

    return;
}

//main function: dealing with command line input/output
//argv[0]=uELMO
//argv[1]=xxx.bin  -- target binary arm code 
// -N xxxx --- generate xxxx traces
int main(int argc, char *argv[])
{
    time_t timet;
    int ra = 0;

    fvr = false;
    N = 1;
    N_ind = 0;
    srand((unsigned)time(&timet));

    if(!ArgsValid(argc, argv))
    {
        //printf("bin file not specified\n");
        PrintHelp();
        return (1);
    }

    for (ra = 2; ra < argc; ra++)
    {
        if(strcmp(argv[ra], "-N") == 0)
        {
            sscanf(argv[ra + 1], "%d", &N);
            ra++;
        }
        else if(strcmp(argv[ra], "-fvr") == 0)
        {
            fvr = true;
        }
        else if(strcmp(argv[ra], "--verbose") == 0)
        {
            verbose = true;
        }
#ifdef USE_SEAL
        else if(strcmp(argv[ra], "--io") == 0)
        {
            ioSupported = true;
            portpath = argv[ra + 1];
            ra++;
        }
        else if(strcmp(argv[ra], "--st") == 0)
        {
            useSealTrace = true;
            sealtracepath = argv[ra + 1];
            ra++;
        }
        else if(strcmp(argv[ra], "--sc") == 0)  //Use ULANG script.
        {
            useScript = true;
            scriptpath = argv[ra + 1];  //Script path.
            snprintf(dictpath, sizeof(dictpath) - 1, "%s.sdc", scriptpath);     //Seal dictionary path.
            ra++;
        }
#endif
        else
        {
            printf("Unknown option: %s\n", argv[ra]);
            PrintHelp();
            exit(0);
        }

    }

#ifdef USE_SEAL
    //Initialise Seal library.
    Init_Seal();
#endif

    //Load binary files to rom
    Read_Binary(argv[1]);

    printf
        ("########################################\n\nGENERATING TRACES...\n\n");
    for (N_ind = 0; N_ind < N; N_ind++)
    {
        frameno = 0;            //Reset Frame counter.
        cyclecount = 0;

        if(N_ind % 100 == 0)
            printf("########## TRACE %d\n", N_ind);
        run();                  //run one trace
        if(useScript)
        {
            ResetScript();
        }
    }

    //system("pause");
#ifdef USE_SEAL
    CleanSeal();
#endif
    return (0);
}
