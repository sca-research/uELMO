#if USE_SMURF
#include <stdio.h>

#include "symuelmo.h"

#include "uelmo.h"

#include "smurf/frame.h"
#include "smurf/symbolic.h"
#include "smurf/version.h"

//Clear sym_core_current.
CORE_STATUS_SYM sym_core_current = { 0 };

//NULL Symbol.
const uSymbol SYM_NULL = { 0 };

//Count of Symbols. 
static int symidcount = 1;	//SYM_NULL existed by default.

//Dictionary.
EncDict *uDict = NULL;

//Check if ${sym} is SYM_NULL.
int IsSymNull(uSymbol sym)
{
    if (sym.symid == SYM_NULL.symid)
	{
	    return true;
	}
    else
	{
	    return false;
	}
}

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
	    symcomp[i].sid_p = ci.ci.symid + i;
	}

    return;
}

//Initialise sym_core_current.
int InitSymCore()
{
    ComponentInstance ci = { 0 };

    //Check Core Version.
    if (V2 > smurf->core->versionid)
	{
	    printf("Symbolic feature requires Core Version >= 2.\n");
	    exit(-1);
	    return -1;
	}

//Bind sym_core_current to the Symbolic fields of the Frame.
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

    //Initialise the Encoding Dictionary.
    uDict = NewEncDict();

    return 0;
}

//Clean resources related to SymCore.
void CleanSymCore()
{
    //Export Dictionary.
    ExportEncDict(uDict, "./dict.sdc");

    //Free resources.
    DelEncDict(uDict);
    return;
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

//Clear the Symbol (= reset it to NULL) of ${comp}.
int SymClear(SymbolicComponent component)
{
    return SymAssign(component, SYM_NULL);
}

//Encode a string into uELMO symbol.
//If ${symstr} is encoded for the first time, it will be automatically added into uDict.
uSymbol SymEncode(const char *symstr)
{
    uSymbol sym = SYM_NULL;
    CodeEntry *ce = NULL;

    //Dictionay initialisation check.
    if (NULL == uDict)
	{
	    return SYM_NULL;
	}

    //Attempt to find the Symbol.
    if (SMURF_SYM_NULL_ID == (sym.symid = FindSymIdByName(uDict, symstr)))
	{
	    //Not found.
	    //Construct a new CodeEntry with Symbol ID being the count of Symbols.
	    sym.symid = symidcount++;
	    ce = NewCodeEntry(sym.symid, symstr);
	    //Add the Symbol into the dictionary.
	    AddCodeEntry(uDict, ce);
	}

    return sym;
}

//Decode an uELMO symbol into string.
//Return value:
//A string pointed into the uDict if successfull, or NULL if the Symbol ID cannot be decoded.
const char *SymDecode(const uSymbol sym)
{
    const char *symstr = NULL;
    char errormsg[SMURF_INFO_MAXLEN] = { 0 };

    //Dictionay initialisation check.
    if (NULL == uDict)
	{
	    return NULL;
	}

    //Attempt to decode the string.
    if (NULL == (symstr = FindSymNameById(uDict, sym.symid)))
	{
	    //Decode failed.
	    snprintf(errormsg, sizeof(errormsg),
		     "#ERROR: Symbol ID %X cannot be decoded.\n", sym.symid);
	    INFO(errormsg);
	    return NULL;
	}

    return symstr;
}

#endif
