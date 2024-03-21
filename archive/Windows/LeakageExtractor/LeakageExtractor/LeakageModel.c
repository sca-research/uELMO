#include "Config.h"
#include "../../uELMO/uELMO/core.h"
#include "LeakageModel.h"
#include "Write_LeakageState.h"
//Combine four unsigned int to a uint8_t array
void Combine4(unsigned int a, unsigned int b, unsigned int c, unsigned int d, uint8_t* arr)
{
	int i = 0;
	uint8_t* ap = (uint8_t*)&a;
	uint8_t* bp = (uint8_t*)&b;
	uint8_t* cp = (uint8_t*)&c;
	uint8_t* dp = (uint8_t*)&d;
	for (i = 0; i < 4; i++)
	{
		arr[i] = ap[i];
		arr[i + 4] = bp[i];
		arr[i + 8] = cp[i];
		arr[i + 12] = dp[i];
	}
}

//print out the instruction discription for current cycle
void Generate_Leakage_Instr(CORE_STATUS* current, bool header)
{
	if (header == true)
	{
		char disp[150];
		sprintf(disp, "%s\n%s\n%s\n", current->Execute_instr_disp, current->Decode_instr_disp, current->Memory_instr_disp);
		Write_Instr(disp);
	}
	return;
}

//Part 1: select the components in each frame as leakage
//each component can be linear or nominal
//header==true--->write out the discription for header
//header==false --->write out leakage state data
void Generate_Leakage_Select(CORE_STATUS* current,bool header)
{
	int i;
	char disp[50];
	if (NON_ACTIVE_REG)//reg[16]: nominal
	{
		for (i = 0; i < 16; i++)
		{
			if (header)
			{
				sprintf(disp, "Reg %d", i);
				Write_leakage_label(disp, 0);
			}
			else
				Write_leakage_data((uint8_t*)&(current->reg[i]), sizeof(unsigned int), 0);	
		}
	}
	if (CPSR)
	{
		//CPSR, linear
		if (header)
			Write_leakage_label("CPSR", 1);
		else
			Write_leakage_data((uint8_t*)&(current->cpsr), sizeof(unsigned int), 1);
	}

	//2 pipeline registers, nominal
	if (MICROARCHITECTURAL)
	{
		if (header)
			Write_leakage_label("Pipeline Reg 1", 0);
		else
			Write_leakage_data((uint8_t*) &(current->D2E_reg1), sizeof(unsigned int), 0);
		if (header)
			Write_leakage_label("Pipeline Reg 2", 0);
		else
			Write_leakage_data((uint8_t*)&(current->D2E_reg2), sizeof(unsigned int), 0);
	}
	//pipeline data bus (i.e. D.9 and 10) whether comes from decoding reg ports, or 
	//forwarded from current ALUout/memory read output; therefore will be covered later

	//Fetch does not produce data-dependent leakage, ignore

	//Decode
	//Decoding register access, linear
	if (MICROARCHITECTURAL && DECODE_PORT)
	{
		for (i = 0; i < 3; i++)
		{
			if (header)
			{
				sprintf(disp, "Decoding port %d", i);
				Write_leakage_label(disp, 1);
			}
			else
				Write_leakage_data((uint8_t*)&(current->Decode_port_data[i]), sizeof(unsigned int), 1);
		}
	}
	
	//Glitchy decoding register access, linear
	if (MICROARCHITECTURAL && DECODE_PORT && GLITCHY_DECODE)
	{
		for (i = 0; i < 3; i++)
		{
			if (header)
			{
				sprintf(disp, "Glitchy decoding port %d", i);
				Write_leakage_label(disp, 1);
			}
			else
				Write_leakage_data((uint8_t*)&(current->glitchy_Decode_port_data[i]), sizeof(unsigned int), 1);
		}
	}

	//Execute
    //Only ALU output, other captured by decode (pipeline register) or interaction (combinatorial)
	//ALU output, nominal
	if (header)
		Write_leakage_label("ALU output", 0);
	else
		Write_leakage_data((uint8_t*) & (current->Execute_ALU_result), sizeof(unsigned int), 0);

	//Memory subsystem
	if (NON_ACTIVE_MEM || (current->Read_valid == true) || (current->Write_valid == true))
	{
		//Memory address, nomial
		if (header)
			Write_leakage_label("Memory address", 0);
		else
			Write_leakage_data((uint8_t*)&(current->Memory_addr), sizeof(unsigned int), 0);
		//Memory data, nomial
		if (header)
			Write_leakage_label("Memory data", 0);
		else
			Write_leakage_data((uint8_t*)&(current->Memory_data), sizeof(unsigned int), 0);
		//Memory write buffer, nomial
		if (header)
			Write_leakage_label("Memory write buffer", 0);
		else
			Write_leakage_data((uint8_t*)&(current->Memory_writebuf), sizeof(unsigned int), 0);
		//Memory write buffer delayed, nomial
		if (header)
			Write_leakage_label("Memory write buffer delayed", 0);
		else
			Write_leakage_data((uint8_t*)&(current->Memory_writebuf_delayed), sizeof(unsigned int), 0);

		//Memory read buffer, nomial
		if (header)
			Write_leakage_label("Memory read buffer", 0);
		else
			Write_leakage_data((uint8_t*)&(current->Memory_readbuf), sizeof(unsigned int), 0);
	}

}

//Part 2: select the components in each frame that produce transition leakage
//each component can be linear or nominal (i.e. combining two nominal state)
//header==true--->write out the discription for header
//header==false --->write out leakage state data
void Generate_Leakage_Transition(CORE_STATUS* prev,CORE_STATUS* current, bool header)
{
	int i;
	char disp[50];
	unsigned int temp = 0;
	//LSB Neighbouring effect
	if (TRANSITION && LSB_NEIGHBOUR)
	{
		for (i = 0; i < 13; i = i + 2)//no PC, LR or SP
		{
			if (header)
			{
				sprintf(disp, "LSB Neighbouring Reg %d XOR Reg %d", i, i^0x1);
				Write_leakage_label(disp, 1);
			}
			else
			{
				temp = current->reg[i] ^ current->reg[i ^ 0x1];
				Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
			}
		}
	}
	//Target register HD
	if (TRANSITION)//reg[16]: linear
	{
		for (i = 0; i < 13; i++)//no PC, LR or SP
		{
			if (header)
			{
				sprintf(disp, "Previous Reg %d", i);
				Write_leakage_label(disp, 1);
			}
			else
			{
				Write_leakage_data((uint8_t*)&(prev->reg[i]), sizeof(unsigned int), 1);
			}
				
		}
		for (i = 0; i < 13; i++)
		{
			if (header)
			{
				sprintf(disp, "Reg %d HD", i);
				Write_leakage_label(disp, 1);
			}
			else
			{
				temp = prev->reg[i] ^ current->reg[i];
				Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
			}

		}
	}
	if (CPSR&&TRANSITION)
	{
		//CPSR, linear
		if (header)
			Write_leakage_label("Previous CPSR", 1);
		else
			Write_leakage_data((uint8_t*)&(prev->cpsr), sizeof(unsigned int), 1);
		if (header)
			Write_leakage_label("CPSR HD", 1);
		else
		{
			temp = (prev->cpsr) ^ (current->cpsr);
			Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
		}
	}

	//2 pipeline registers, linear
	if (MICROARCHITECTURAL && TRANSITION)
	{
		if (header)
			Write_leakage_label("Previous Pipeline Reg 1", 1);
		else
			Write_leakage_data((uint8_t*)&(prev->D2E_reg1), sizeof(unsigned int), 1);
		if (header)
			Write_leakage_label("Previous Pipeline Reg 2", 1);
		else
			Write_leakage_data((uint8_t*)&(prev->D2E_reg2), sizeof(unsigned int), 1);
		if (header)
			Write_leakage_label("Pipeline Reg 1 HD", 1);
		else
		{
			temp = (prev->D2E_reg1) ^ (current->D2E_reg1);
			Write_leakage_data((uint8_t*)&temp, sizeof(unsigned int), 1);
		}
		if (header)
			Write_leakage_label("Pipeline Reg 2 HD", 1);
		else
		{
			temp = (prev->D2E_reg2) ^ (current->D2E_reg2);
			Write_leakage_data((uint8_t*)&temp, sizeof(unsigned int), 1);
		}
			
	}

	//Decode
	//Decoding register access, linear
	if (MICROARCHITECTURAL && DECODE_PORT&& TRANSITION)
	{
		for (i = 0; i < 3; i++)
		{
			if (header)
			{
				sprintf(disp, "Previous Decoding port %d", i);
				Write_leakage_label(disp, 1);
			}
			else
				Write_leakage_data((uint8_t*)&(prev->Decode_port_data[i]), sizeof(unsigned int), 1);
			if (header)
			{
				sprintf(disp, "Decoding port %d HD", i);
				Write_leakage_label(disp, 1);
			}
			else
			{
				temp = (prev->Decode_port_data[i]) ^ (current->Decode_port_data[i]);
				Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
			}
		}
	}

	//Glitchy decoding register access, linear
	if (MICROARCHITECTURAL && DECODE_PORT && GLITCHY_DECODE && TRANSITION)
	{
		for (i = 0; i < 3; i++)
		{
			if (header)
			{
				sprintf(disp, "Glitchy decoding port %d XOR current port %d", i,i);
				Write_leakage_label(disp, 1);
			}
			else
			{
				temp = (current->glitchy_Decode_port_data[i]) ^ (current->Decode_port_data[i]);
				Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
			}
			if (header)
			{
				sprintf(disp, "Glitchy decoding port %d XOR previous port %d", i, i);
				Write_leakage_label(disp, 1);
			}
			else
			{
				temp = (current->glitchy_Decode_port_data[i]) ^ (prev->Decode_port_data[i]);
				Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
			}
		}
	}

	//Execute
	//Only ALU output, other captured by decode (pipeline register) or interaction (combinatorial)
	//ALU output, nominal
	if (TRANSITION)
	{
		if (header)
			Write_leakage_label("Previous ALU output", 1);
		else
			Write_leakage_data((uint8_t*)&(prev->Execute_ALU_result), sizeof(unsigned int), 1);
		if (header)
			Write_leakage_label("ALU output HD", 1);
		else
		{
			temp = (prev->Execute_ALU_result) ^ (current->Execute_ALU_result);
			Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
		}
	}

	//Memory subsystem
	if ((TRANSITION)&&(NON_ACTIVE_MEM || (current->Read_valid == true) || (current->Write_valid == true) || (current->Write_valid_delayed == true)))
	{
		//Memory address
		if (header)
			Write_leakage_label("Previous Memory address", 0);
		else
			Write_leakage_data((uint8_t*)&(prev->Memory_addr), sizeof(unsigned int), 0);
		if (header)
			Write_leakage_label("Memory address HD", 1);
		else
		{
			temp = (prev->Memory_addr) ^ (current->Memory_addr);
			Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
		}	
		//Memory data, nomial
		if (header)
			Write_leakage_label("Previous Memory data", 0);
		else
			Write_leakage_data((uint8_t*)&(prev->Memory_data), sizeof(unsigned int), 0);
		if (header)
			Write_leakage_label("Memory data HD", 1);
		else
		{
			temp = (prev->Memory_data) ^ (current->Memory_data);
			Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
		}
			
		//Memory write buffer, nomial
		if (header)
			Write_leakage_label("Previous Memory write buffer", 0);
		else
			Write_leakage_data((uint8_t*)&(prev->Memory_writebuf), sizeof(unsigned int), 0);
		if (header)
			Write_leakage_label("Memory write buffer HD", 1);
		else
		{
			temp = (prev->Memory_writebuf) ^ (current->Memory_writebuf);
			Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
		}
		//Memory write buffer delayed, nomial
		if (header)
			Write_leakage_label("Previous Memory write buffer delayed", 0);
		else
			Write_leakage_data((uint8_t*)&(prev->Memory_writebuf_delayed), sizeof(unsigned int), 0);
		if (header)
			Write_leakage_label("Memory write buffer delayed HD", 1);
		else
		{
			temp = (prev->Memory_writebuf_delayed) ^ (current->Memory_writebuf_delayed);
			Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
		}
		//Memory read buffer, nomial
		if (header)
			Write_leakage_label("Previous Memory read buffer", 0);
		else
			Write_leakage_data((uint8_t*)&(prev->Memory_readbuf), sizeof(unsigned int), 0);
		if (header)
			Write_leakage_label("Memory read buffer HD", 1);
		else
		{
			temp = (current->Memory_readbuf) ^ (prev->Memory_readbuf);
			Write_leakage_data((uint8_t*)&(temp), sizeof(unsigned int), 1);
		}
			
	}
	
}

//Part 3: select the components in each frame that produce interaction leakage
//all nominal 
//header==true--->write out the discription for header
//header==false --->write out leakage state data

void Generate_Leakage_Interaction(CORE_STATUS* prev, CORE_STATUS* current, bool header)
{
	uint8_t* combine = NULL;
	if (TRANSITION && MICROARCHITECTURAL)
	{
		if (header)
		{
			Write_leakage_label("Reg A * Reg B * Previous Reg A * Previous Reg B", 0);//Reg A * Reg B *prev_Reg A * prev_Reg B: Full
		}
		else
		{
			combine = (uint8_t*)malloc(4 * sizeof(unsigned int));
			Combine4(current->D2E_reg1, current->D2E_reg2, prev->D2E_reg1, prev->D2E_reg2, combine);
			Write_leakage_data(combine, 4 * sizeof(unsigned int), 0);//Reg A * Reg B *prev_Reg A * prev_Reg B: Full
			free(combine);
		}

	}
}