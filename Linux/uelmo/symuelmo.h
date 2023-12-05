#ifndef SYMUELMO_H
#define SYMUELMO_H
#ifdef USE_SMURF

#include "uelmo.h"
#include "Configure.h"
#include "smurf/smurf.h"
#include "smurf/symbolic.h"

#define NON_ARRAY_SYM_COMP (-1)
#define SYM_ENABLED ((useScript && OnTrace))

typedef struct {
    const char *name;
    int index;                  //Index of this SymbolicComponent if it is an array typed.
    SmurfSymId *sid_p;
} SymbolicComponent;

typedef struct {
    SmurfSymId symid;
} uSymbol;

//NULL Symbol.
extern const uSymbol SYM_NULL;

//Flag to control symbolic operations.
extern bool SymActive;

//Check if ${sym} is SYM_NULL.
int IsSymNull(uSymbol sym);

//Symbolic structure for uELMO core.
typedef struct {
    //Registers:
    //architectural registers: R0 to R15
    SymbolicComponent core_valid;       //a flag for reaching the end of this execution
    SymbolicComponent reg[16];  //architectural
    SymbolicComponent cpsr;     //architectural
    //micro-arhictectural registers
    SymbolicComponent F2D_instrreg;     //pipeline register, barrier between Fetch and Decode (i.e. D.1)  
    SymbolicComponent D2E_reg1; //pipeline register, barrier between Decode and Execute   (i.e. E.1)
    SymbolicComponent D2E_reg2; //pipeline register, barrier between Decode and Execute   (i.e. E.2)
    SymbolicComponent D2E_instrreg;     //Pesudo register: in theory should be already tranferred to control signal, here we store the instruction instead

    //Bus/MUX
    SymbolicComponent cpsr_valid;       //update cpsr
    SymbolicComponent cpsr_data;        //new data for cpsr
    SymbolicComponent D2E_reg1_valid;   //update pipeline register 1
    SymbolicComponent D2E_reg2_valid;   //update pipeline register 2
    SymbolicComponent D2E_reg1_data;    //input data for pipeline register 1, barrier between Decode and Execute     (i.e. D.9)
    SymbolicComponent D2E_reg2_data;    //input data for pipeline register 2, barrier between Decode and Execute     (i.e. D.10)
    //Fetch
    SymbolicComponent Fetch_instruction_new;    //Fetched new instruction (i.e. F.3)
    SymbolicComponent Fetch_valid;      //A flag that stall the pipeline when jump happens
    //Decode
    SymbolicComponent Decode_port_regindex[3];  //Current Decoding Read ports index (0-15, often 0-7) (i.e. D.2-D.4)
    SymbolicComponent Decode_port_data[3];      //Current Decoding Read ports data (i.e. D.5-D.7)
    SymbolicComponent Decode_destination_regindex;      //Destination register index
    SymbolicComponent Decode_valid;     //A flag that stall the pipeline when jump happens
    SymbolicComponent glitchy_Decode_port_regindex[3];  //Decode the current instruction according to the previous instruction decoding style
    SymbolicComponent glitchy_Decode_port_data[3];      //Decode the current instruction according to the previous instruction decoding style

    //Execute
    SymbolicComponent Execute_Imm;      //Current Execute Immediate data
    SymbolicComponent Execute_ALU_result;       //Current ALU output
    SymbolicComponent Execute_destination_regindex;     //Execute register index: 0-15 valid, 0xff: no output
    SymbolicComponent Execute_multicycle_regindex;      //Current register index for multi-cycle execution: 0-7 valid
    SymbolicComponent Execute_valid;    //A flag that stall the pipeline when jump happens

    //Meomory subsystem
    SymbolicComponent Read_valid;       //set it true when a new read address is sent to address bus
    SymbolicComponent Read_type;        //0 word, 1 byte, 2 half-word
    SymbolicComponent Write_valid;      //set it true when a new read address is sent to address bus
    SymbolicComponent Write_type;       //0 word, 1 byte, 2 half-word
    SymbolicComponent SignExtend_byte_valid;    //sign extend
    SymbolicComponent SignExtend_halfbyte_valid;        //sign extend
    SymbolicComponent Memory_read_targetreg;    //For read instruction, the targt regsiter
    SymbolicComponent Memory_addr;      //Address bus of the memory: must align to 4
    SymbolicComponent Memory_data;      //shared (Read and write) data bus: must be 32-bit
    SymbolicComponent Write_valid_delayed;      //set it true when the previous Write_valid is true
    SymbolicComponent Memory_writebuf_delayed;  //write buffer on the write bus
    SymbolicComponent Memory_writebuf;  //write buffer on the write bus
    SymbolicComponent Memory_readbuf;   //read buffer on the read bus
    SymbolicComponent Read_reg_update;  //if true, update the register according to Memory_read_targetreg and Memory_readbuf
    SymbolicComponent Memory_read_targetreg_buf;        //For read instruction, the targt regsiter

    //Discriptions
    SymbolicComponent Memory_instr_disp;        //Discription for the memory instruction (STRING Component has only a unique Symbol.)
    SymbolicComponent Decode_instr_disp;        //Discription for the decode instruction (STRING Component has only a unique Symbol.)
    SymbolicComponent Execute_instr_disp;       //Discription for the execute instruction (STRING Component has only a unique Symbol.)
} CORE_STATUS_SYM;

//Symbolic CORE_STATUS
extern CORE_STATUS_SYM sym_core_current;

//Dictionary.
extern EncDict *uDict;

//Initialise sym_core_current.
int InitSymCore();

//Clean resources related to SymCore.
void CleanSymCore();

//Assign a Symbol to a component.
int SymAssign(SymbolicComponent component, uSymbol sym);

//Copy the Symbol of a component to another.
int SymCopy(SymbolicComponent dstcomp, SymbolicComponent srccomp);

//Clear the Symbol (= reset it to NULL) of ${component}.
int SymClear(SymbolicComponent component);

//Return the Symbol of ${component}
uSymbol GetSym(SymbolicComponent component);

//Encode a string into uELMO symbol.
//If ${symstr} is encoded for the first time, it will be automatically added into uDict.
uSymbol SymEncode(const char *symstr);

//Decode an uELMO symbol into string.
//Return value:
//A string pointed into the uDict if successfull, or NULL if the Symbol ID cannot be decoded.
const char *SymDecode(const uSymbol);

#endif
#endif
