#if USE_SMURF
#include "symuelmo.h"

#include "uelmo.h"

#include "smurf/frame.h"
#include "smurf/symbolic.h"
#include <stdio.h>

//Clear sym_core_current.
CORE_STATUS_SYM sym_core_current; // = { 0 };

//NULL Symbol.
uSymbol SYM_NULL = { 0 };

//Bind array typed Symbol.
static inline void BindSymArray(const char *compname,
                                SymbolicComponent * symcomp, int size)
{
    int i;
    ComponentInstance ci = { 0 };

    //Fetch ComponentInstace from Smurf buffered Frame.
    SmurfFetchComp(&ci, smurf->frame, compname);

    //Set pointers to the Symbolic fileds in the Frame.
    for (i = 0; i < size; i++)
        {
            symcomp[i].sid_p = ci.ci.symid;
        }

    return;
}

//Initialise sym_core_current.
int InitSymCore()
{
    ComponentInstance ci = { 0 };

//Macro to ease binding the symbolic fields.
#define\
    BindSym(x)\
    {\
        SmurfFetchComp(&ci,smurf->frame,#x);\
        sym_core_current.x.sid_p=ci.ci.symid;\
    }

    BindSym(core_valid);
    //BindSym(reg);
    BindSymArray("reg", sym_core_current.reg, 16);
    BindSym(cpsr);
    BindSym(F2D_instrreg);
    BindSym(D2E_reg1);
    BindSym(D2E_reg2);
    BindSym(D2E_instrreg);
    BindSym(cpsr_valid);
    BindSym(cpsr_data);
    BindSym(D2E_reg1_valid);
    BindSym(D2E_reg2_valid);
    BindSym(D2E_reg1_data);
    BindSym(D2E_reg2_data);
    BindSym(Fetch_instruction_new);
    BindSym(Fetch_valid);
    //BindSym(Decode_port_regindex);
    BindSymArray("Decode_destination_regindex",
                 sym_core_current.Decode_port_regindex, 3);
    //BindSym(Decode_port_data);
    BindSymArray("Decode_port_data", sym_core_current.Decode_port_data, 3);
    BindSym(Decode_destination_regindex);
    BindSym(Decode_valid);
    //BindSym(glitchy_Decode_port_regindex);
    BindSymArray("glitchy_Decode_port_regindex",
                 sym_core_current.glitchy_Decode_port_regindex, 3);
    BindSym(Decode_destination_regindex);
    //BindSym(glitchy_Decode_port_data);
    BindSymArray("glitchy_Decode_port_data",
                 sym_core_current.glitchy_Decode_port_data, 3);
    BindSym(Execute_Imm);
    BindSym(Execute_ALU_result);
    BindSym(Execute_destination_regindex);
    BindSym(Execute_multicycle_regindex);
    BindSym(Execute_valid);
    BindSym(Read_valid);
    BindSym(Read_type);
    BindSym(Write_valid);
    BindSym(Write_type);
    BindSym(SignExtend_byte_valid);
    BindSym(SignExtend_halfbyte_valid);
    BindSym(Memory_read_targetreg);
    BindSym(Memory_addr);
    BindSym(Memory_data);
    BindSym(Write_valid_delayed);
    BindSym(Memory_writebuf_delayed);
    BindSym(Memory_writebuf);
    BindSym(Memory_readbuf);
    BindSym(Read_reg_update);
    BindSym(Memory_read_targetreg_buf);
    BindSym(Memory_instr_disp);
    BindSym(Decode_instr_disp);
    BindSym(Execute_instr_disp);
#undef BindSym

    return 0;
}

//Assign a Symbol to a component.
int SymAssign(SymbolicComponent component, uSymbol symbol)
{
    SfSetFrameSymid(component.sid_p, symbol.symid);
    return 0;
}

//Copy the Symbol of a component to another.
int SymCopy(SymbolicComponent dstcomp, SymbolicComponent srccomp)
{
    SmurfSymId t;

    t = SfGetFrameSymid(srccomp.sid_p);
    SfSetFrameSymid(dstcomp.sid_p, t);
    return 0;
}
#endif
