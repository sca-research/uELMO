#include "Config.h"
#include "../../uELMO/uELMO/core.h"
#include "LeakageExtractor.h"
#include "FrameReader.h"
#include "Write_LeakageState.h"
//process one trace
//print out header if header==true
void Process_OneTrace(bool header)
{
    CORE_STATUS* prev = (CORE_STATUS*)malloc(sizeof(CORE_STATUS));
    CORE_STATUS* current = (CORE_STATUS*)malloc(sizeof(CORE_STATUS));
    int framecount = 0;
    //Read first frame
    Read_Frame(current);
    memcpy(prev, current, sizeof(CORE_STATUS));
    while (current->core_valid == true)
    {
        //printf("Frame %d: %s %s\n", framecount, current->Decode_instr_disp, current->Execute_instr_disp);
        //Print out current instruction discriptione
        Generate_Leakage_Instr(current, header);
        //Generate leakage & write out
        Generate_Leakage_Select(current,header);
        Generate_Leakage_Transition(prev,current,header);
        Generate_Leakage_Interaction(prev,current,header);
        Write_frameender();
        //move on
        memcpy(prev, current, sizeof(CORE_STATUS));
        Read_Frame(current);
        framecount++;
    }
    if (header)
        Write_headender();
    else
        Write_traceender();
    //printf("\n\n\n\n");
    free(prev);
    free(current);
    if (header)
    {
        Rewind();
    }
}

//main function: dealing with command line input/output
//argv[0]=LeakageExtractor
//argv[1]=xxx.dat  -- target execution frame file
// -o xxxx.dat --- output leakage state file
int main(int argc, char* argv[])
{
    int ra = 0;
    int tracecount = 0;
    bool header = true;
    int oindex = argc;
    if (argc < 2)
    {
        printf("Execution frame file not specified\n");
        return(1);
    }
    for (ra = 0; ra < argc; ra++)
    {
        if (strcmp(argv[ra], "-o") == 0) {
            oindex = ra + 1;
        }
    }
    if (oindex == argc)
    {
        printf("Please assign an output file for the leakage state!\n");
        exit(0);
    }
    else
    {
        OpenLeakageFile(argv[oindex]);
    }
    //Open execution file
    Open_Exefile(argv[1]);

    //Read execution file
    while (IsEof() == false)
    {
        if(tracecount%100==0)
            printf("############Trace %d:\n",tracecount);
        //process one trace
        Process_OneTrace(header);
        if (header == true)
            header = false;
        else
            tracecount++;
    }
    //Close execution file
    Close_Exefile(argv[1]);
    //Close output leakage state file
    CloseLeakageFile();
    system("pause");
}