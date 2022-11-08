//#pragma once
#ifndef CORE_H_
#define CORE_H_
#include "Configure.h"

#define CPSR_N (1<<31)
#define CPSR_Z (1<<30)
#define CPSR_C (1<<29)
#define CPSR_V (1<<28)
#define CPSR_Q (1<<27)
//SMURF_ADAPTING, this is the core definition
//Do not change anything here(unless you would like to rewrite Thumbulator)!

typedef struct {
    unsigned int num_value;     //numerical value
    char *exp;                  //expression
} Component_t;

typedef struct {
    //Registers:
    //architectural registers: R0 to R15
    bool core_valid;            //a flag for reaching the end of this execution
    Component_t reg[16];        //architectural
    unsigned int cpsr;          //architectural

    //micro-architectural registers
    uint16_t F2D_instrreg;      //pipeline register, barrier between Fetch and Decode (i.e. D.1)  
    Component_t D2E_reg1;       //pipeline register, barrier between Decode and Execute   (i.e. E.1)
    Component_t D2E_reg2;       //pipeline register, barrier between Decode and Execute   (i.e. E.2)

    uint16_t D2E_instrreg;      //Pesudo register: in theory should be already tranferred to control signal, here we store the instruction instead

    //Bus/MUX
    bool cpsr_valid;            //update cpsr
    unsigned int cpsr_data;     //new data for cpsr
    bool D2E_reg1_valid;        //update pipeline register 1
    bool D2E_reg2_valid;        //update pipeline register 2
    Component_t D2E_reg1_data;  //input data for pipeline register 1, barrier between Decode and Execute     (i.e. D.9)
    Component_t D2E_reg2_data;  //input data for pipeline register 2, barrier between Decode and Execute     (i.e. D.10)

    //Fetch
    uint16_t Fetch_instruction_new;     //Fetched new instruction (i.e. F.3)
    bool Fetch_valid;           //A flag that stall the pipeline when jump happens
    //Decode
    uint8_t Decode_port_regindex[3];    //Current Decoding Read ports index (0-15, often 0-7) (i.e. D.2-D.4)

    Component_t Decode_port_data[3];    //Current Decoding Read ports data (i.e. D.5-D.7)
    uint32_t Decode_port_data_temp[3];  //Temporary patch for fixing bug induced from Exp branch.

    uint8_t Decode_destination_regindex;        //Destination register index
    bool Decode_valid;          //A flag that stall the pipeline when jump happens
    unsigned int glitchy_Decode_port_regindex[3];       //Decode the current instruction according to the previous instruction decoding style

    Component_t glitchy_Decode_port_data[3];    //Decode the current instruction according to the previous instruction decoding style

    //Execute
    unsigned int Execute_Imm;   //Current Execute Immediate data

    Component_t Execute_ALU_result;     //Current ALU output

    uint8_t Execute_destination_regindex;       //Execute register index: 0-15 valid, 0xff: no output
    uint8_t Execute_multicycle_regindex;        //Current register index for multi-cycle execution: 0-7 valid
    bool Execute_valid;         //A flag that stall the pipeline when jump happens

    //Meomory subsystem
    bool Read_valid;            //set it true when a new read address is sent to address bus
    uint8_t Read_type;          //0 word, 1 byte, 2 half-word
    bool Write_valid;           //set it true when a new read address is sent to address bus
    uint8_t Write_type;         //0 word, 1 byte, 2 half-word
    bool SignExtend_byte_valid; //sign extend
    bool SignExtend_halfbyte_valid;     //sign extend
    uint8_t Memory_read_targetreg;      //For read instruction, the target register

    Component_t Memory_addr;    //Address bus of the memory: must align to 4
    Component_t Memory_data;    //shared (Read and write) data bus: must be 32-bit

    bool Write_valid_delayed;   //set it true when the previous Write_valid is true

    Component_t Memory_writebuf_delayed;        //write buffer on the write bus
    Component_t Memory_writebuf;        //write buffer on the write bus
    Component_t Memory_readbuf; //read buffer on the read bus

    bool Read_reg_update;       //if true, update the register according to Memory_read_targetreg and Memory_readbuf
    uint8_t Memory_read_targetreg_buf;  //For read instruction, the targt regsiter

    //Descriptions
    char Memory_instr_disp[50]; //Description for the memory instruction
    char Decode_instr_disp[50]; //Description for the decode instruction
    char Execute_instr_disp[50];        //Description for the execute instruction
} CORE_STATUS;

extern CORE_STATUS core_current;
//global flag that shows whether the current cycle is on the trace
extern bool OnTrace;
//Check if the current executed LDR instruction requires an extra delay cycle, i.e. LDR r0,xxx; LDR xxx,[r0]
bool check_delay(unsigned int);
void read_register(unsigned int, Component_t *);
unsigned int read_register2(unsigned int);
void read_register_forward(unsigned int, Component_t *);
void Clock(bool);
void write_register(unsigned int, Component_t *);
void write_register_value(unsigned int, unsigned int);
void do_zflag(unsigned int);
void do_nflag(unsigned int);
void do_cflag(unsigned int, unsigned int, unsigned int);
void do_vflag(unsigned int, unsigned int, unsigned int);
void do_cflag_bit(unsigned int);
void do_vflag_bit(unsigned int);
void update_component(Component_t *, Component_t *);
void reset_component(Component_t *);
#endif
