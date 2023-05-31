#include "Configure.h"
#include "core.h"
#include "Emulator.h"
#include "Memory.h"
#include "Execute.h"
#include "Decode.h"
#include "Fetch.h"
#include "EmuIO.h"

Instruction_t annotatedInst[3];
int numAnnotatedInst = 0;
int totalNumberInst = 3;

void initialize_instructions(){
    // dictionary
    // 1 , &a
    // 2 , a0
    // 3 , &b
    // 4 , b0
    // 5 , rnd
    // 6 , rnd ^ a0
    //@src r0 , &a
    //@dst r6 , a0
    //ldrb r6, [r0, #0]
    strcpy(annotatedInst[0].instCode, "ldrb r6, [r0, #0]");
    annotatedInst[0].srcTag0.registerNum = 0;
    annotatedInst[0].srcTag0.annotation.symid = 1;
    annotatedInst[0].dstTag.registerNum = 6;
    annotatedInst[0].dstTag.annotation.symid = 2;
    printf("inst: %s\n", annotatedInst[0].instCode);
    printf("srcTag0: %d\n", annotatedInst[0].srcTag0.registerNum);
    printf("srcTag0 annotation: %d\n", annotatedInst[0].srcTag0.annotation.symid);
    printf("dstTag0: %d\n", annotatedInst[0].dstTag.registerNum);
    printf("dstTag0 annotation: %d\n", annotatedInst[0].dstTag.annotation.symid);
    //@src r1 , &b
    //@dst r3 , b0
    //ldrb r3, [r1, #0]
    strcpy(annotatedInst[1].instCode, "ldrb r3, [r1, #0]");
    annotatedInst[1].srcTag0.registerNum = 1;
    annotatedInst[1].srcTag0.annotation.symid = 3;
    annotatedInst[1].dstTag.registerNum = 3;
    annotatedInst[1].dstTag.annotation.symid =  4;
    //@src r2 , rnd
    //@src r6 , a0
    //@dst r2 , rnd ^ a0
    //eor r2, r6
    strcpy(annotatedInst[2].instCode, "eor r2, r6");
    annotatedInst[2].srcTag0.registerNum = 2;
    annotatedInst[2].srcTag0.annotation.symid = 5;
    annotatedInst[2].srcTag1.registerNum = 6;
    annotatedInst[2].srcTag1.annotation.symid = 2;
    annotatedInst[2].dstTag.registerNum = 2;
    annotatedInst[2].dstTag.annotation.symid = 6;

    fetchInst.isEmpty = 1;
    decodeInst.isEmpty = 1;
    executeInst.isEmpty = 1;
}

void print_instruction(Instruction_t inst){
    printf("inst: %s\n", inst.instCode);
    printf("srcTag0: %d\n", inst.srcTag0.registerNum);
    printf("dstTag: %d\n", inst.dstTag.registerNum);
    //printf("srcTag0: %s\n", inst.srcTag0.annotation);
}

//-------------------------------------------------------------------
//-------------------------------------------------------------------
//-------------------------------------------------------------------
//Execute one instruction: if return 1, it reaches an error or the end of the trace
int Execute_OneInstr(int *cycle)
{
    bool wait_exe = false;      //Execute cycle requires extra cycle
    bool wait_mem = false;      //Memory cycle requires extra cycle
    do
        {
            if (DEBUG_CORE)
                printf("Cycle=%d\n", *cycle);
            //Clock+1; update the registers with new values: i.e. pipeline registers, reg[16] and cpsr
            Clock(wait_exe);
            //Memory run one cycle: 
            //read address and output data to bus
            wait_mem = Memory_OneCycle();
            if (core_current.core_valid == false)
                return 1;
            if (wait_mem == true)
                {
                    wait_exe = true;
                    sprintf(core_current.Decode_instr_disp, "Decode: stall");
                    sprintf(core_current.Execute_instr_disp, "Execute: stall");
                    //Write out current cycle to Frame
                    Write_Frame();
                    (*cycle)++;
                    continue;
                }

            //Execute
            wait_exe = Execute_OneCylce(wait_mem);
            //printf("OK 1\n");
            if(decodeInst.isEmpty == 0) {
                copyInstToFrom(&executeInst, &decodeInst);
                executeInst.isEmpty = 0;
                printf("EXECUTE\n");
                print_instruction(decodeInst);
                printf("\n\n");
            } else {
                executeInst.isEmpty = 1;
            }
            //printf("OK 2\n");
            if (wait_exe == false)      //Execute did not stall the pipeline
                {
                    if(fetchInst.isEmpty == 0) {
                        copyInstToFrom(&decodeInst, &fetchInst);
                        decodeInst.isEmpty = 0;
                        printf("DECODE\n");
                        print_instruction(decodeInst);
                        printf("\n\n");
                    } else{
                        decodeInst.isEmpty = 1;
                    }

                    //Fetch
                    Fetch_OneCycle();
                    //printf("OK 3\n");
                    if(numAnnotatedInst < totalNumberInst) {
                        copyInstToFrom(&fetchInst, &(annotatedInst[numAnnotatedInst]));
                        fetchInst.isEmpty = 0;
                        printf("FETCH\n");
                        print_instruction(fetchInst);
                        printf("\n\n");
                        numAnnotatedInst += 1;
                    } else {
                        fetchInst.isEmpty = 1;
                    }
                    //Decode
                    Decode_OneCycle(false);
                    //printf("OK 4\n");//
                }
            else
                sprintf(core_current.Decode_instr_disp, "Decode: stall");

            //Write out current cycle to Frame
            Write_Frame();
            (*cycle)++;
        }
    while (wait_exe);
    return 0;
}

//-------------------------------------------------------------------
//Initialise the running enviroment before each trace
int reset(void)
{
    //memset(ram,0xFF,sizeof(ram));
    core_current.cpsr = 0;
    core_current.cpsr_data = 0;
    core_current.core_valid = true;
    core_current.reg[13] = fetch32(0x00000000); //cortex-m
    core_current.reg[14] = 0xFFFFFFFF;
    core_current.reg[15] = fetch32(0x00000004); //cortex-m
    if ((core_current.reg[15] & 1) == 0)
        {
            printf("reset vector with an ARM address 0x%08X\n",
                   core_current.reg[15]);
            exit(1);
        }
    core_current.reg[15] &= ~1;
    core_current.reg[15] += 2;
    core_current.Read_valid = false;
    core_current.Write_valid = false;
    core_current.Fetch_valid = true;
    core_current.Decode_valid = false;
    core_current.Execute_valid = false;
    core_current.Read_reg_update = false;
    core_current.D2E_reg1_valid = false;
    core_current.D2E_reg2_valid = false;
    core_current.cpsr_valid = false;
    core_current.Decode_destination_regindex = 0xff;
    core_current.Execute_destination_regindex = 9;
    core_current.Execute_destination_regindex = 0xff;
    core_current.glitchy_Decode_port_regindex[0] = 0xff;
    core_current.glitchy_Decode_port_regindex[1] = 0xff;
    core_current.glitchy_Decode_port_regindex[2] = 0xff;
    strcpy(core_current.Memory_instr_disp, "Memory init");
    strcpy(core_current.Decode_instr_disp, "Decode init");
    strcpy(core_current.Execute_instr_disp, "Execute init");
    //Fetch
    Fetch_OneCycle();
    if(numAnnotatedInst < totalNumberInst) {
        copyInstToFrom(&fetchInst, &(annotatedInst[numAnnotatedInst]));
        fetchInst.isEmpty = 0;
        //print_instruction(fetchInst);
        numAnnotatedInst += 1;
    } else {
        fetchInst.isEmpty = 1;
    }

    return (0);
}

//-------------------------------------------------------------------
//Run one trace
int run(void)
{
    int cycle = 0;
    //Intialise enviroment
    reset();
    initialize_instructions();
    //Run each cycle
    while (1)
        {

            if (Execute_OneInstr(&cycle))
                break;          //one instruction till ELMO endprogram() is called
        }
    return (0);
}
