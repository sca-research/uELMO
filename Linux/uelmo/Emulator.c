#include "Configure.h"
#include "core.h"
#include "Emulator.h"
#include "Memory.h"
#include "Execute.h"
#include "Decode.h"
#include "Fetch.h"
#include "EmuIO.h"

#include "ulang.h"
#include "ulangcmd.h"
#include "uelmo.h"

//-------------------------------------------------------------------
//-------------------------------------------------------------------
//-------------------------------------------------------------------
//Execute one instruction: if return 1, it reaches an error or the end of the trace
int Execute_OneInstr(int *cycle)
{
    bool wait_exe = false;	//Execute cycle requires extra cycle
    bool wait_mem = false;	//Memory cycle requires extra cycle
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
		    cyclecount++;
		    continue;
		}

	    //Execute
	    wait_exe = Execute_OneCylce(wait_mem);
	    if (wait_exe == false)	//Execute did not stall the pipeline
		{

		    //Fetch
		    Fetch_OneCycle();
		    //Decode
		    Decode_OneCycle(false);

		}
	    else
		sprintf(core_current.Decode_instr_disp, "Decode: stall");

	    //Write out current cycle to Frame
	    Write_Frame();
	    (*cycle)++;
	    cyclecount++;
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
    core_current.reg[13] = fetch32(0x00000000);	//cortex-m
    core_current.reg[14] = 0xFFFFFFFF;
    core_current.reg[15] = fetch32(0x00000004);	//cortex-m
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

    return (0);
}

//-------------------------------------------------------------------
//Run one trace
int run(void)
{
    int cycle = 0;
    //Intialise enviroment
    reset();
    //Run each cycle
    while (1)
	{

	    if (Execute_OneInstr(&cycle))
		break;		//one instruction till ELMO endprogram() is called
	}
    return (0);
}
