#include "Configure.h"
#include "core.h"

CORE_STATUS core_current;


//global flag that shows whether the current cycle is on the trace
bool OnTrace = false;
//Check if the current executed LDR instruction requires an extra delay cycle, i.e. LDR r0,xxx; LDR xxx,[r0]
bool check_delay(unsigned int reg)
{
    if ((core_current.Memory_read_targetreg_buf != 0xff)
	&& (reg == core_current.Memory_read_targetreg_buf))
	return true;
    else
	return false;

}

//Read register from current core status
void read_register(unsigned int reg, Component_t* comp)
{
    unsigned int data;

    reg &= 0xF;
    //if(DEBUG_CORE) printf("read_register(%u)=",reg);
    data = core_current.reg[reg].num_value;
    if (reg == 15)
	{
	    if (data & 1)
		{
		    printf("pc has lsbit set 0x%08X\n", data);
		}
	    data &= ~1;
	}
    //if(DEBUG_CORE) printf("0x%08X\n",data);
    update_component(comp, &(core_current.reg[reg]));
    comp->num_value = data;
}

//Read register from current core status
unsigned int read_register2(unsigned int reg)
{
    unsigned int data;

    reg &= 0xF;
    //if(DEBUG_CORE) printf("read_register(%u)=",reg);
    data = core_current.reg[reg].num_value;
    if (reg == 15)
    {
        if (data & 1)
        {
            printf("pc has lsbit set 0x%08X\n", data);
        }
        data &= ~1;
    }
    //if(DEBUG_CORE) printf("0x%08X\n",data);
    return data;
}

//Read register with result forwarding

void read_register_forward(unsigned int reg, Component_t* comp)
{
    unsigned int data;
    reg &= 0xF;
    if ((core_current.Memory_read_targetreg_buf != 0xff)
	&& (reg == core_current.Memory_read_targetreg_buf))
	update_component(comp, &(core_current.Memory_readbuf));

    else
	{
	    if ((core_current.Execute_destination_regindex != 0xff)
		&& (reg == core_current.Execute_destination_regindex))
        {
            update_component(comp, &(core_current.Execute_ALU_result));
        }
	    else
		{
		    data = core_current.reg[reg].num_value;
		    if (reg == 15)
			data &= ~1;
            update_component(comp, &(core_current.reg[reg]));
		    comp->num_value = data; //TODO: review this
        }
	}
    //if(DEBUG_CORE) printf("0x%08X\n",data);
}

//Write register to current core status
void write_register(unsigned int reg, Component_t* comp)
{
    unsigned int data = comp->num_value;
    reg &= 0xF;
    if (reg == 15)
	data &= ~1;
    update_component(&(core_current.reg[reg]), comp);
    core_current.reg[reg].num_value = data;
    if (DEBUG_CORE)
	printf("write_register(%u,0x%08X)\n", reg, comp->num_value);
}

//Write register to current core status
void write_register_value(unsigned int reg, unsigned int data)
{
    reg &= 0xF;
    if (reg == 15)
        data &= ~1;
    core_current.reg[reg].num_value = data;
    if (DEBUG_CORE)
        printf("write_register(%u,0x%08X)\n", reg, data);
}

//Write CPSR-Z
void do_zflag(unsigned int x)
{
    if (x == 0)
	core_current.cpsr_data = CPSR_Z | core_current.cpsr_data;
    else
	core_current.cpsr_data = (~CPSR_Z) & core_current.cpsr_data;
}

//-------------------------------------------------------------------
void do_nflag(unsigned int x)
{
    if (x & 0x80000000)
	core_current.cpsr_data = CPSR_N | core_current.cpsr_data;
    else
	core_current.cpsr_data = (~CPSR_N) & core_current.cpsr_data;
}

//-------------------------------------------------------------------
void do_cflag(unsigned int a, unsigned int b, unsigned int c)
{
    unsigned int rc;

    core_current.cpsr_data = (~CPSR_C) & core_current.cpsr_data;
    rc = (a & 0x7FFFFFFF) + (b & 0x7FFFFFFF) + c;	//carry inbuses
    rc = (rc >> 31) + (a >> 31) + (b >> 31);	//carry out
    if (rc & 2)
	core_current.cpsr_data = CPSR_C | core_current.cpsr_data;
}

//-------------------------------------------------------------------
void do_vflag(unsigned int a, unsigned int b, unsigned int c)
{
    unsigned int rc;
    unsigned int rd;

    core_current.cpsr_data = (~CPSR_V) & core_current.cpsr_data;
    rc = (a & 0x7FFFFFFF) + (b & 0x7FFFFFFF) + c;	//carry in
    rc >>= 31;			//carry in in lsbit
    rd = (rc & 1) + ((a >> 31) & 1) + ((b >> 31) & 1);	//carry out
    rd >>= 1;			//carry out in lsbit
    rc = (rc ^ rd) & 1;		//if carry in != carry out then signed overflow
    if (rc)
	core_current.cpsr_data = CPSR_V | core_current.cpsr_data;
}

//-------------------------------------------------------------------
void do_cflag_bit(unsigned int x)
{
    if (x)
	core_current.cpsr_data = CPSR_C | core_current.cpsr_data;
    else
	core_current.cpsr_data = (~CPSR_C) & core_current.cpsr_data;
}

//-------------------------------------------------------------------
void do_vflag_bit(unsigned int x)
{
    if (x)
	core_current.cpsr_data = CPSR_V | core_current.cpsr_data;
    else
	core_current.cpsr_data = (~CPSR_V) & core_current.cpsr_data;
}

//update the core registers with new value
void Clock(bool pause)
{

    //Memory ---> target register
    if (core_current.Read_reg_update == true)
	{
	    if (core_current.Memory_read_targetreg_buf == 15)
		write_register_value(core_current.Memory_read_targetreg_buf,
			       core_current.Memory_readbuf.num_value + 2);
	    else
		write_register(core_current.Memory_read_targetreg_buf,
			       &(core_current.Memory_readbuf));
	    core_current.Read_reg_update = false;
	    core_current.Memory_read_targetreg_buf = 0xff;
	}
    else
	//ALU---> target register
    if (core_current.Execute_destination_regindex != 0xff)
	{
	    write_register(core_current.Execute_destination_regindex,
			   &(core_current.Execute_ALU_result));
	    //core_current.Execute_destination_regindex=0xff;
	}
    //Update pipeline registers
    if (core_current.D2E_reg1_valid)
	{
        update_component(&(core_current.D2E_reg1), &(core_current.D2E_reg1_data));
	}
    //Update pipeline registers
    if (core_current.D2E_reg2_valid)
	{
        update_component(&(core_current.D2E_reg2), &(core_current.D2E_reg2_data));
	}
    //Update cpsr
    if (core_current.cpsr_valid)
	{
	    core_current.cpsr = core_current.cpsr_data;
	}
    core_current.Execute_destination_regindex =
	core_current.Decode_destination_regindex;
    //propragate the instruction
    if (pause == false)
	{

	    core_current.D2E_instrreg = core_current.F2D_instrreg;
	    core_current.Execute_valid = core_current.Decode_valid;
	    core_current.F2D_instrreg = core_current.Fetch_instruction_new;
	    core_current.Decode_valid = core_current.Fetch_valid;
	    core_current.Fetch_valid = true;
	}

}

//-------------------------------------------------------------------
// Component a is updated with the field values of component b
void update_component(Component_t* a, Component_t* b)
{
    a->num_value = b->num_value;
    if (a->exp != NULL)
    {
        free(a->exp);
    }
    if (b->exp != NULL)
    {
        a->exp = malloc(strlen(b->exp) + 1);
        strcpy(a->exp, b->exp);
    }
}

void reset_component(Component_t* a)
{
    a->num_value = 0;
    if (a->exp != NULL)
    {
        free(a->exp);
    }
    a->exp = NULL;
}

void add(Component_t* a, Component_t* b, Component_t* c)
{
    a->num_value = b->num_value + c->num_value;
    if (a->exp != NULL)
    {
        free(a->exp);
    }
    a->exp = malloc(strlen(b->exp) + 1);
    strcpy(a->exp, b->exp);
}