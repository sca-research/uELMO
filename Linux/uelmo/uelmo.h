#ifndef UELMO_H
#define UELMO_H
#define UELMO_ERROR (-1)

#ifdef USE_SMURF
#include "smurf/smurf.h"
#include "smurf/emulator.h"

#define ELMO_CORE "../smurffiles/uelmo.json"
extern SmurfIO *sio;
extern SmurfCore *smfcore;
extern SmurfTrace *smftrace;
extern SmurfTraceFrame *smfframe;
extern char *smftracepath;
extern char *siopath;

//Smurf frame components headers.
struct {
    //Only for smuelmo.
    SmurfTraceFrameIdx traceno;

    //Registers:
    //architectural registers: R0 to R15
    SmurfTraceFrameIdx core_valid;	//a flag for reaching the end of this execution
    SmurfTraceFrameIdx reg;	//architectural
    SmurfTraceFrameIdx cpsr;	//architectural
    //micro-arhictectural registers
    SmurfTraceFrameIdx F2D_instrreg;	//pipeline register, barrier between Fetch and Decode (i.e. D.1)  
    SmurfTraceFrameIdx D2E_reg1;	//pipeline register, barrier between Decode and Execute   (i.e. E.1)
    SmurfTraceFrameIdx D2E_reg2;	//pipeline register, barrier between Decode and Execute   (i.e. E.2)
    SmurfTraceFrameIdx D2E_instrreg;	//Pesudo register: in theory should be already tranferred to control signal, here we store the instruction instead

    //Bus/MUX
    SmurfTraceFrameIdx cpsr_valid;	//update cpsr
    SmurfTraceFrameIdx cpsr_data;	//new data for cpsr
    SmurfTraceFrameIdx D2E_reg1_valid;	//update pipeline register 1
    SmurfTraceFrameIdx D2E_reg2_valid;	//update pipeline register 2
    SmurfTraceFrameIdx D2E_reg1_data;	//input data for pipeline register 1, barrier between Decode and Execute     (i.e. D.9)
    SmurfTraceFrameIdx D2E_reg2_data;	//input data for pipeline register 2, barrier between Decode and Execute     (i.e. D.10)
    //Fetch
    SmurfTraceFrameIdx Fetch_instruction_new;	//Fetched new instruction (i.e. F.3)
    SmurfTraceFrameIdx Fetch_valid;	//A flag that stall the pipeline when jump happens
    //Decode
    SmurfTraceFrameIdx Decode_port_regindex;	//Current Decoding Read ports index (0-15, often 0-7) (i.e. D.2-D.4)
    SmurfTraceFrameIdx Decode_port_data;	//Current Decoding Read ports data (i.e. D.5-D.7)
    SmurfTraceFrameIdx Decode_destination_regindex;	//Destination register index
    SmurfTraceFrameIdx Decode_valid;	//A flag that stall the pipeline when jump happens
    SmurfTraceFrameIdx glitchy_Decode_port_regindex;	//Decode the current instruction according to the previous instruction decoding style
    SmurfTraceFrameIdx glitchy_Decode_port_data;	//Decode the current instruction according to the previous instruction decoding style

    //Execute
    SmurfTraceFrameIdx Execute_Imm;	//Current Execute Immediate data
    SmurfTraceFrameIdx Execute_ALU_result;	//Current ALU output
    SmurfTraceFrameIdx Execute_destination_regindex;	//Execute register index: 0-15 valid, 0xff: no output
    SmurfTraceFrameIdx Execute_multicycle_regindex;	//Current register index for multi-cycle execution: 0-7 valid
    SmurfTraceFrameIdx Execute_valid;	//A flag that stall the pipeline when jump happens

    //Meomory subsystem
    SmurfTraceFrameIdx Read_valid;	//set it true when a new read address is sent to address bus
    SmurfTraceFrameIdx Read_type;	//0 word, 1 byte, 2 half-word
    SmurfTraceFrameIdx Write_valid;	//set it true when a new read address is sent to address bus
    SmurfTraceFrameIdx Write_type;	//0 word, 1 byte, 2 half-word
    SmurfTraceFrameIdx SignExtend_byte_valid;	//sign extend
    SmurfTraceFrameIdx SignExtend_halfbyte_valid;	//sign extend
    SmurfTraceFrameIdx Memory_read_targetreg;	//For read instruction, the targt regsiter
    SmurfTraceFrameIdx Memory_addr;	//Address bus of the memory: must align to 4
    SmurfTraceFrameIdx Memory_data;	//shared (Read and write) data bus: must be 32-bit
    SmurfTraceFrameIdx Write_valid_delayed;	//set it true when the previous Write_valid is true
    SmurfTraceFrameIdx Memory_writebuf_delayed;	//write buffer on the write bus
    SmurfTraceFrameIdx Memory_writebuf;	//write buffer on the write bus
    SmurfTraceFrameIdx Memory_readbuf;	//read buffer on the read bus
    SmurfTraceFrameIdx Read_reg_update;	//if true, update the register according to Memory_read_targetreg and Memory_readbuf
    SmurfTraceFrameIdx Memory_read_targetreg_buf;	//For read instruction, the targt regsiter

    //Discriptions
    SmurfTraceFrameIdx Memory_instr_disp;	//Discription for the memory instruction
    SmurfTraceFrameIdx Decode_instr_disp;	//Discription for the decode instruction
    SmurfTraceFrameIdx Execute_instr_disp;	//Discription for the execute instruction
} smftidx;

#endif

#endif
