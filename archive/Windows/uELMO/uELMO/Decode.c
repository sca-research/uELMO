#include "Configure.h"
#include "core.h"
#include "Decode.h"

//One cycle of decode
void Decode_OneCycle(bool prev)
{
	unsigned int  rb,imm;
	uint8_t ra_ind, rb_ind,rc_ind;
	uint8_t rd_ind;
	int i=0;
	unsigned int inst=core_current.F2D_instrreg;
	unsigned int next_inst=core_current.Fetch_instruction_new;
	if(!core_current.Decode_valid)//Jump happens, no need to decode 
		return;
	if(prev)//re-do decodde for LDR delay
	{
		inst=core_current.D2E_instrreg;
		next_inst=core_current.F2D_instrreg;
	}
	core_current.Execute_valid=true;//next instruction can execute
	//Load glitchy decoding data: old decoding style, new data
	for (i=0;i<3;i++)
	{
		if(core_current.glitchy_Decode_port_regindex[i]!=0xff)
			core_current.glitchy_Decode_port_data[i]=read_register(core_current.glitchy_Decode_port_regindex[i]);
		else
			core_current.glitchy_Decode_port_data[i]=0;
	}
    //ADC two registers
	//Instr 8
    #pragma region
    if((inst&0xFFC0)==0x4140)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;

		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: adc r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: adc r%u,r%u", ra_ind, rb_ind);

        return;
    }
	#pragma endregion
    //ADD(1) small immediate two registers
	//Instr 4
	#pragma region
    if((inst&0xFE00)==0x1C00)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
        rb_ind=(inst>>3)&0x7;
        imm=(inst>>6)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];//remain
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: adds r%u,r%u,#0x%X\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode: adds r%u,r%u,#0x%X", ra_ind, rb_ind, imm);

        return;

    }
	#pragma endregion
    //ADD(2) big immediate one register
	#pragma region
    if((inst&0xF800)==0x3000)
    {
		//Port indices
		ra_ind=(inst>>8)&0x7;
        imm=(inst>>0)&0xFF;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];//remain
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>8)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: adds r%u,#0x%X\n",ra_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode: adds r%u,#0x%X", ra_ind, imm);

        return;

    }
	#pragma endregion

    //ADD(3) three registers
	#pragma region
    if((inst&0xFE00)==0x1800)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
        rb_ind=(inst>>3)&0x7;
        rc_ind=(inst>>6)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rc_ind;
		core_current.Decode_port_regindex[2]=rb_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rc_ind);
		core_current.Decode_port_data[2]=read_register(rb_ind);

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>6)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>3)&0x07;

		if(DEBUG_CORE)
			printf("Decode: adds r%u,r%u,r%u\n",ra_ind,rb_ind,rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: adds r%u,r%u,r%u", ra_ind, rb_ind, rc_ind);

        return;
    }
#pragma endregion

    //ADD(4) two registers one or both high no flags
	//Instr 6
	#pragma region
    if((inst&0xFF00)==0x4400)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		ra_ind|=(inst>>4)&0x8;
        rb_ind=(inst>>3)&0xF;


		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x07)|((next_inst>>4)&0x8);
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x0F;
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: adds r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: adds r%u,r%u", ra_ind, rb_ind);

        return;
    }
	#pragma endregion
    //ADD(5) rd = pc plus immediate
	#pragma region
    if((inst&0xF800)==0xA000)
    {
		//Port indices
		imm=(inst>>0)&0xFF;
        ra_ind=(inst>>8)&0x7;
        imm<<=2;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=0;
		core_current.Decode_port_data[2]=0;
		//registers
		core_current.D2E_reg1_data=read_register_forward(15);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];//Not used
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>8)&0x7;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: add r%u,PC,#0x%02X\n",ra_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode: add r%u,PC,#0x%02X", ra_ind, imm);
        return;

    }
	#pragma endregion
    //ADD(6) SP = sp plus immediate
	#pragma region
    if((inst&0xF800)==0xA800)
    {		
		//Port indices
		imm=(inst>>0)&0xFF;
        rd_ind=(inst>>8)&0x7;
        imm<<=2;

		core_current.Decode_port_regindex[0]=rd_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(rd_ind);
		core_current.Decode_port_data[1]=0;
		core_current.Decode_port_data[2]=0;
		//registers
		core_current.D2E_reg1_data=read_register(13);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];//Not used
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=rd_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>8)&0x7;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: add r%u,SP,#0x%02X\n",rd_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode: add r%u,SP,#0x%02X", rd_ind, imm);

        return;
    }
	#pragma endregion
    //ADD(7) rd=sp plus immediate
	#pragma region
    if((inst&0xFF80)==0xB000)
    {
		//Port indices
		imm=(inst>>0)&0x7F;
        imm<<=2;

		core_current.Decode_port_regindex[0]=13;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(13);
		core_current.Decode_port_data[1]=0;
		core_current.Decode_port_data[2]=0;
		//registers
		core_current.D2E_reg1_data=read_register_forward(13);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];//Not used
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=13;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>8)&0x7;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: add SP,#0x%02X\n",imm);
		sprintf(core_current.Decode_instr_disp, "Decode: add SP,#0x%02X", imm);

        return;
    }
	#pragma endregion

    //AND
	//Instr 18
	#pragma region
    if((inst&0xFFC0)==0x4000)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: ands r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: ands r%u,r%u", ra_ind, rb_ind);

        return;
    }
	#pragma endregion
    //ASR(1) two register immediate
	//Instr 28
    #pragma region
    if((inst&0xF800)==0x1000)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		imm=(inst>>6)&0x1F;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: asrs r%u,r%u,#0x%X\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode: asrs r%u,r%u,#0x%X", ra_ind, rb_ind, imm);

    }
    #pragma endregion
    //ASR(2) two register
	//Instr 29
	#pragma region
    if((inst&0xFFC0)==0x4100)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;
		//core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: asrs r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: asrs r%u,r%u", ra_ind, rb_ind);

        return;
    }
	#pragma endregion
    //B(1) conditional branch
	//Instr 49
	#pragma region
    if((inst&0xF000)==0xD000)
    {
		//Port indices
		imm=(inst>>0)&0xFF;
		core_current.Decode_port_regindex[0]=0xff;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=0;
		core_current.Decode_port_data[1]=0;
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[0];
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=15;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:b* Imm=0x%08X\n",imm);
		sprintf(core_current.Decode_instr_disp,"Decode:b * Imm = 0x % 08X",imm);
        return;

    }
	#pragma endregion

    //B(2) unconditional branch
	//Instr 49
	#pragma region
    if((inst&0xF800)==0xE000)
    {
		//Port indices
		imm=(inst>>0)&0x7FF;
		core_current.Decode_port_regindex[0]=0xff;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=0;
		core_current.Decode_port_data[1]=0;
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[0];
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=15;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:b Imm=0x%08X\n",imm);
		sprintf(core_current.Decode_instr_disp, "Decode:b Imm=0x%08X", imm);
        return;
    }
#pragma endregion
    //BIC two registers
	//Instr 21
#pragma region
    if((inst&0xFFC0)==0x4380)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Decode_destination_regindex=ra_ind;
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: bics r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: bics r%u,r%u", ra_ind, rb_ind);
		return;
    }
#pragma endregion
    //BKPT: enter the debug mode; ignored
#pragma region
    if((inst&0xFF00)==0xBE00)
    {
        //rb=(inst>>0)&0xFF;
        //fprintf(stderr,"bkpt 0x%02X\n",rb);
		printf("Error! Do not support BKPT instruction!\n");
        return;
    }
#pragma endregion
    //BL/BLX(1)
	//Instr 50
#pragma region
    if((inst&0xE000)==0xE000) //BL,BLX
    {
        if((inst&0x1800)==0x1000) //H=b10
        {
			imm=inst&((1<<11)-1);
			core_current.Decode_port_regindex[0]=0xff;
			core_current.Decode_port_regindex[1]=0xff;
			core_current.Decode_port_regindex[2]=0xff;
			//Port data
			core_current.Decode_port_data[0]=0;
			core_current.Decode_port_data[1]=0;
			core_current.Decode_port_data[2]=0;//Not used

			//registers
			//core_current.D2E_reg1_data=core_current.Decode_port_data[0];
			//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
			core_current.Execute_Imm=imm;
			core_current.Decode_destination_regindex=14;
			core_current.D2E_reg1_valid=false;
			core_current.D2E_reg2_valid=false;
			//Decode next instruction using the current decoder style
			core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used
			core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
			core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used
			if(DEBUG_CORE)
				printf("Decode: b1 pre-fix\n");
			sprintf(core_current.Decode_instr_disp, "Decode: b1 pre-fix");

			return;
        }
        else
        if((inst&0x1800)==0x1800) //H=b11
        {
            //branch to thumb
            imm=(inst&((1<<11)-1))<<1;
			core_current.Decode_port_regindex[0]=0xff;
			core_current.Decode_port_regindex[1]=0xff;
			core_current.Decode_port_regindex[2]=0xff;
			//Port data
			core_current.Decode_port_data[0]=0;
			core_current.Decode_port_data[1]=0;
			core_current.Decode_port_data[2]=0;//Not used
			//registers
			//core_current.D2E_reg1_data=core_current.Decode_port_data[0];
			//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
			core_current.Execute_Imm=imm;
			core_current.Decode_destination_regindex=15;
			//Decode next instruction using the current decoder style
			core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used
			core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
			core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used
			if(DEBUG_CORE)
				printf("Decode: bl 0x%08X\n",imm-3);
			return;
        }
        else
        if((inst&0x1800)==0x0800) //H=b01
        {
            //fprintf(stderr,"cannot branch to arm 0x%08X 0x%04X\n",pc,inst);
            //return(1);
            //branch to thumb
            imm=(inst&((1<<11)-1))<<1;;
           	core_current.Decode_port_regindex[0]=0xff;
			core_current.Decode_port_regindex[1]=0xff;
			core_current.Decode_port_regindex[2]=0xff;
			//Port data
			core_current.Decode_port_data[0]=0;
			core_current.Decode_port_data[1]=0;
			core_current.Decode_port_data[2]=0;//Not used
			//registers
			//core_current.D2E_reg1_data=core_current.Decode_port_data[0];
			//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
			//core_current.Execute_Imm=imm;
			core_current.Decode_destination_regindex=15;
			//Decode next instruction using the current decoder style
			core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used
			core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
			core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used
            if(DEBUG_CORE)
				printf("Decode: bl 0x%08X\n",imm-3);
			return;
        }
    }
#pragma endregion
    //BLX(2)
	//Instr 50
#pragma region
    if((inst&0xFF87)==0x4780)
    {
		ra_ind=(inst>>3)&0xF;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=0;
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=15;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>3)&0x0F;
		core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used
		if(DEBUG_CORE)
			printf("blx r%u\n",ra_ind);
		sprintf(core_current.Decode_instr_disp, "blx r%u\n", ra_ind);
		return;

    }
	#pragma endregion
    //BX
	//Instr 50
	#pragma region
    if((inst&0xFF87)==0x4700)
    {
		ra_ind=(inst>>3)&0xF;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=0;
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=15;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>3)&0x0F;
		core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used
		if(DEBUG_CORE)
			printf("Decode: bx r%u\n",ra_ind);
		sprintf(core_current.Decode_instr_disp,"Decode: bx r%u",ra_ind);
		return;
    }
#pragma endregion
    //CMN
#pragma region
    if((inst&0xFFC0)==0x42C0)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Decode_destination_regindex=ra_ind;
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: cmns r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: cmns r%u,r%u", ra_ind, rb_ind);
		return;
    }
#pragma endregion
    //CMP(1) compare immediate
	//Instr 17
#pragma region
    if((inst&0xF800)==0x2800)
    {
		//Port indices
		ra_ind=(inst>>8)&0x7;
        imm=(inst>>0)&0xFF;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];//remain
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>8)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:cmp r%u,#0x%02X\n",ra_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:cmp r%u,#0x%02X", ra_ind, imm);
        return;
    }
#pragma endregion
    //CMP(2) compare register
	//Instr 15
#pragma region
    if((inst&0xFFC0)==0x4280)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Decode_destination_regindex=0xff;
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: cmps r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: cmps r%u,r%u", ra_ind, rb_ind);
        return;
    }
	#pragma endregion
    //CMP(3) compare high register
	#pragma region
    if((inst&0xFF00)==0x4500)
    {
       		//Port indices
		ra_ind=(inst>>0)&0x7;
		ra_ind|=(inst>>4)&0x8;
        rb_ind=(inst>>3)&0xF;


		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x07)|((next_inst>>4)&0x8);
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x0F;
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: cmps r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: cmps r%u,r%u", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    //CPS change processor state
	#pragma region
    if((inst&0xFFE8)==0xB660)
    {
        printf("Error! CPS not supported\n");
        return;
    }
	#pragma endregion
    //CPY copy high register: pre-UAL synonym for MOV
	//Bug: this is the same as the high register mov, so there
	//seems no point to operate this as the low register mov, even if
	//it is executing with low registers
	/*
    if((inst&0xFFC0)==0x4600)
    {
        //same as mov except you can use both low registers
        //going to let mov handle high registers
        rd=(inst>>0)&0x7; //mov handles the high registers
        rm=(inst>>3)&0x7; //mov handles the high registers
        rc=read_register(rm);
        write_register(rd,rc);
        if(registerdataflow && ((t==1))) fprintf(asmoutput,"cpy r%u,r%u\n",rd,rm);
        act=init_action((enum Component)(rd),rc);
		if(registerdataflow) dataptr = update_dataflow(dataptr,inst,act);

        return(0);
    }
	*/

    //EOR
	//Instr 19
	#pragma region
    if((inst&0xFFC0)==0x4040)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Decode_destination_regindex=ra_ind;
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:eors r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode:eors r%u,r%u", ra_ind, rb_ind);
        return;
    }
	#pragma endregion

    //LDMIA
	//Instr 39
	#pragma region
    if((inst&0xF800)==0xC800)
    {
		//Port indices
		rc_ind=(inst>>8)&0x7;
		core_current.Decode_port_regindex[0]=0xff;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=0;//Not used
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=read_register(rc_ind);
		//registers
		core_current.D2E_reg1_data=read_register_forward(rc_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=rc_ind;
		core_current.Execute_multicycle_regindex=9;
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>8)&0x7;//Not used

		if(DEBUG_CORE)
			printf("Decode:ldmia r%u\n",rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode:ldmia r%u", rc_ind);
		return;

    }
	#pragma endregion
    //LDR(1) two register immediate
	//Instr 31
	#pragma region
    if((inst&0xF800)==0x6800)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		imm=(inst>>6)&0x1F;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=imm;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:ldr r%u,[r%u,#0x%X]\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:ldr r%u,[r%u,#0x%X]", ra_ind, rb_ind, imm);
        return;
    }
	#pragma endregion
    //LDR(2) three register
	//Instr 34
	#pragma region
    if((inst&0xFE00)==0x5800)
    {
		//According to paper
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		rc_ind=(inst>>6)&0x7;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=read_register(rc_ind);

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>6)&0x07;

		if(DEBUG_CORE)
			printf("Decode:ldr r%u,[r%u,r%u]\n",ra_ind,rb_ind,rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode:ldr r%u,[r%u,r%u]", ra_ind, rb_ind, rc_ind);
        return;
    }
	#pragma endregion
    //LDR(3)
	//rd=[PC+offset]: treat like LDRI 31
	#pragma region
    if((inst&0xF800)==0x4800)
    {
		//Port indices
		ra_ind=(inst>>8)&0x07;
		imm=(inst>>0)&0xFF;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(15)-2;
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=imm;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>8)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:ldr r%u,[PC+#0x%X]\n",ra_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:ldr r%u,[PC+#0x%X]", ra_ind, imm);
		return;
    }
	#pragma endregion

    //LDR(4)
	//Load rd [Sp+imm], treat as LDRI Instr 31
	#pragma region
    if((inst&0xF800)==0x9800)
    {
		//Port indices
		ra_ind=(inst>>8)&0x07;
		imm=(inst>>0)&0xFF;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(13);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=imm;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>8)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:ldr r%u,[SP+#0x%X]\n",ra_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:ldr r%u,[SP+#0x%X]", ra_ind, imm);
		return;
    }
	#pragma endregion
    //LDRB(1)
	//Instr 33 LDRBI
	#pragma region
    if((inst&0xF800)==0x7800)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		imm=(inst>>6)&0x1F;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=imm;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:ldrb r%u,[r%u,#0x%X]\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:ldrb r%u,[r%u,#0x%X]", ra_ind, rb_ind, imm);
        return;
    }
	#pragma endregion

    //LDRB(2)
	//Instr 37  LDRB 2reg
	#pragma region
    if((inst&0xFE00)==0x5C00)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		rc_ind=(inst>>6)&0x7;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=read_register(rc_ind);

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>6)&0x07;

		if(DEBUG_CORE)
			printf("Decode:ldrb r%u,[r%u,r%u]\n",ra_ind,rb_ind,rc_ind);
		//if(ra_ind==6 && rb_ind==0 && rc_ind==4)
		sprintf(core_current.Decode_instr_disp, "Decode:ldrb r%u,[r%u,r%u]", ra_ind, rb_ind, rc_ind);

        return;
    }
	#pragma endregion
    //LDRH(1)
	//Instr 32  LDRHI
	#pragma region
    if((inst&0xF800)==0x8800)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		imm=(inst>>6)&0x1F;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=imm;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:ldrh r%u,[r%u,#0x%X]\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:ldrh r%u,[r%u,#0x%X]", ra_ind, rb_ind, imm);
        return;
    }
	#pragma endregion
    //LDRH(2)
	//Instr 35 LDRH 2reg
	#pragma region
    if((inst&0xFE00)==0x5A00)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		rc_ind=(inst>>6)&0x7;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=read_register(rc_ind);//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>6)&0x07;

		if(DEBUG_CORE)
			printf("Decode:ldrh r%u,[r%u,r%u]\n",ra_ind,rb_ind,rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode:ldrh r%u,[r%u,r%u]", ra_ind, rb_ind, rc_ind);
        return;

    }
	#pragma endregion

    //LDRSB
	//Instr 38 2reg
	#pragma region
    if((inst&0xFE00)==0x5600)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		rc_ind=(inst>>6)&0x7;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=read_register(rc_ind);

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>6)&0x07;

		if(DEBUG_CORE)
			printf("Decode:ldrsb r%u,[r%u,r%u]\n",ra_ind,rb_ind,rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode:ldrh r%u,[r%u,r%u]", ra_ind, rb_ind, rc_ind);
        return;

    }
	#pragma endregion
    //LDRSH
	//Instr 35 2reg
	#pragma region
    if((inst&0xFE00)==0x5E00)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		rc_ind=(inst>>6)&0x7;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=read_register(rc_ind);//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Decode_destination_regindex=ra_ind;//
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>6)&0x07;

		if(DEBUG_CORE)
			printf("Decode:ldrsh r%u,[r%u,r%u]\n",ra_ind,rb_ind,rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode:ldrsh r%u,[r%u,r%u]", ra_ind, rb_ind, rc_ind);

        return;
    }
	#pragma endregion
    //LSL(1)
	//Instr 24 LSLI
	#pragma region
    if((inst&0xF800)==0x0000)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		imm=(inst>>6)&0x1F;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: lsls r%u,r%u,#0x%X\n", ra_ind, rb_ind, imm);
		sprintf(core_current.Decode_instr_disp, "Decode: lsls r%u,r%u,#0x%X", ra_ind, rb_ind, imm);

		return;
    }
	#pragma endregion

    //LSL(2) two register
	//Instr 25 LSL 2 reg
	#pragma region
    if((inst&0xFFC0)==0x4080)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;
		//core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: lsls r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: lsls r%u,r%u", ra_ind, rb_ind);

        return;
    }
	#pragma endregion
    //LSR(1) two register immediate
	//Instr 26: LSRI
	#pragma region
    if((inst&0xF800)==0x0800)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		imm=(inst>>6)&0x1F;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: lsrs r%u,r%u,#0x%X\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode: lsrs r%u,r%u,#0x%X", ra_ind, rb_ind, imm);
		return;
    }
	#pragma endregion
    //LSR(2) two register
	//Instr 27 LSR two registers
	#pragma region
    if((inst&0xFFC0)==0x40C0)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: lsrs r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: lsrs r%u,r%u", ra_ind, rb_ind);
        return;
    }
	#pragma endregion

    //MOV(1) immediate
	//Instr 1: movs imm
	#pragma region
    if((inst&0xF800)==0x2000)
    {

		//Port indices
		ra_ind=(inst>>8)&0x07;
		imm=(inst>>0)&0xFF;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=0;
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>8)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: movs r%u,#0x%02X\n",ra_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode: movs r%u,#0x%02X", ra_ind, imm);
		return;
    }
#pragma endregion
    //MOV(2) two low registers
	//Instr 2: movs low reg
	#pragma region
    if((inst&0xFFC0)==0x1C00)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Execute_Imm=0;
		//core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: movs r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: movs r%u,r%u", ra_ind, rb_ind);
        return;
    }
	#pragma endregion
    //MOV(3)
	// Instr 3: mov high reg
	#pragma region
    if((inst&0xFF00)==0x4600)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		ra_ind|=(inst>>4)&0x8;
        rb_ind=(inst>>3)&0xF;


		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[0];
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x07)|((next_inst>>4)&0x8);
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x0F;
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: mov r%u,r%u\n", ra_ind, rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: mov r%u,r%u", ra_ind, rb_ind);
        return;
    }
	#pragma endregion
    //MUL
	//Instr 14
	#pragma region
    if((inst&0xFFC0)==0x4340)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: muls r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: muls r%u,r%u", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    //MVN
	//Instr 22
	#pragma region
    if((inst&0xFFC0)==0x43C0)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;
		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[1];
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: mvns r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: mvns r%u,r%u\n", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    //NEG/RSB
	//Instr 13
	#pragma region
    if((inst&0xFFC0)==0x4240)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[1];
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;

		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: negs r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: negs r%u,r%u", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    //ORR
	//Instr 20
	#pragma region
    if((inst&0xFFC0)==0x4300)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: orrs r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: orrs r%u,r%u", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    //POP
	//Instr 48=LDM
	#pragma region
    if((inst&0xFE00)==0xBC00)
    {
		//Port indices
		core_current.Decode_port_regindex[0]=0xff;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=0;//Not used
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[2];
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=13;
		core_current.Execute_multicycle_regindex=9;
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: pop\n");
		sprintf(core_current.Decode_instr_disp, "Decode: pop");
		return;
    }
	#pragma endregion
    //PUSH
	//Instr 49, =STM
	#pragma region
    if((inst&0xFE00)==0xB400)
    {
		//Port indices
		core_current.Decode_port_regindex[0]=0xff;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=0;//Not used
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[2];
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=13;
		core_current.Execute_multicycle_regindex=9;
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: push\n");
		sprintf(core_current.Decode_instr_disp, "Decode: push");
		return;
    }
	#pragma endregion
    //REV
	//Instr 55 two regs
	#pragma region
    if((inst&0xFFC0)==0xBA00)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[1];
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: rev r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: rev r%u,r%u", ra_ind, rb_ind);

		return;
    }
	#pragma endregion
    //REV16
	//Instr 56
	#pragma region
    if((inst&0xFFC0)==0xBA40)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[1];
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: rev16 r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: rev16 r%u,r%u", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    //REVSH
	//Instr 57
	#pragma region
    if((inst&0xFFC0)==0xBAC0)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[1];
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;

		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: revsh r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: revsh r%u,r%u", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    //ROR
	//Instr 30
	#pragma region
    if((inst&0xFFC0)==0x41C0)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;
		//core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: rors r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: rors r%u,r%u", ra_ind, rb_ind);
        return;
    }
	#pragma endregion
   //SBC
	//Instr 12
	#pragma region
    if((inst&0xFFC0)==0x4180)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used
		//registers
		core_current.D2E_reg1_data=read_register(ra_ind);
		core_current.D2E_reg2_data=read_register(rb_ind);
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: sbcs r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: sbcs r%u,r%u", ra_ind, rb_ind);
        return;
    }
	#pragma endregion
    //SETEND
	#pragma region
    if((inst&0xFFF7)==0xB650)
    {
		printf("setend not implemented\n");
        return;
    }
	#pragma endregion
    //STMIA
	//Instr 46
	#pragma region
    if((inst&0xF800)==0xC000)
    {
		rc_ind=(inst>>8)&0x7;
		//Port indices
		core_current.Decode_port_regindex[0]=0xff;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=0;//Not used
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=read_register(rc_ind);
		//registers
		core_current.D2E_reg1_data=read_register_forward(rc_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];
		core_current.Decode_destination_regindex=rc_ind;
		core_current.Execute_multicycle_regindex=9;
		core_current.Execute_Imm=0;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>8)&0x7;//Not used

		if(DEBUG_CORE)
			printf("Decode: stmia\n",rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: stmia", rc_ind);
		return;
    }
	#pragma endregion
    //STR(1)
	//Instr 40 STRI
	#pragma region
    if((inst&0xF800)==0x6000)
    {
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
        imm=(inst>>6)&0x1F;
		//Port indices
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;//Not used
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(ra_ind);
		core_current.Decode_destination_regindex=0xff;//Not used
		core_current.Execute_Imm=imm;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x7;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x7;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:str r%u,[r%u,#0x%X]\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:str r%u,[r%u,#0x%X]", ra_ind, rb_ind, imm);
		return;
    }
	#pragma endregion
    //STR(2)
	//Instr 43
	#pragma region
    if((inst&0xFE00)==0x5000)
    {
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
        rc_ind=(inst>>6)&0x07;
		//Port indices
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=read_register(rc_ind);

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Decode_destination_regindex=0xff;//Not used
		core_current.Execute_multicycle_regindex=9;
		core_current.Execute_Imm=0;//not used
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x7;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x7;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>6)&0x7;

		if(DEBUG_CORE)
			printf("Decode:str r%u,[r%u,r%u]\n",ra_ind,rb_ind,rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode:str r%u,[r%u,r%u]\n", ra_ind, rb_ind, rc_ind);

		return;
    }
	#pragma endregion
    //STR(3)
	//Store SP with offset, as STRI
	#pragma region
    if((inst&0xF800)==0x9000)
    {
		rc_ind=(inst>>8)&0x07;
        imm=(inst>>0)&0xFF;
		//Port indices
		core_current.Decode_port_regindex[0]=0xff;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=0;
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=read_register(rc_ind);
		//registers
		core_current.D2E_reg1_data=read_register_forward(13);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Decode_destination_regindex=0xff;//Not used
		core_current.Execute_Imm=imm;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=0xff;//Not used;
		core_current.glitchy_Decode_port_regindex[1]=0xff;//Not used
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>8)&0x7;//

		if(DEBUG_CORE)
			printf("Decode:str r%u,[SP,#0x%X]\n",rc_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:str r%u,[SP,#0x%X]\n", rc_ind, imm);

		return;
    }
	#pragma endregion
    //STRB(1)
	//Instr 42 STRBI
	#pragma region
    if((inst&0xF800)==0x7000)
    {
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
        imm=(inst>>6)&0x1F;
		//Port indices
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;//Not used
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);//Not used
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(ra_ind);
		core_current.Decode_destination_regindex=0xff;//Not used
		core_current.Execute_Imm=imm;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x7;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x7;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:strb r%u,[r%u,#0x%X]\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:strb r%u,[r%u,#0x%X]", ra_ind, rb_ind, imm);

		return;
    }
	#pragma endregion
    //STRB(2)
	//Instr 45 STRB
	#pragma region
    if((inst&0xFE00)==0x5400)
    {
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
        rc_ind=(inst>>6)&0x07;
		//Port indices
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=read_register(rc_ind);

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Decode_destination_regindex=0xff;//Not used
		core_current.Execute_multicycle_regindex=9;
		core_current.Execute_Imm=0;//not used
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x7;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x7;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>6)&0x7;

		if(DEBUG_CORE)
			printf("Decode:strb r%u,[r%u,r%u]\n",ra_ind,rb_ind,rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode:strb r%u,[r%u,r%u]", ra_ind, rb_ind, rc_ind);
		return;
    }
	#pragma endregion
    //STRH(1)
	//Instr 41 STRHI
	#pragma region
    if((inst&0xF800)==0x8000)
    {
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
        imm=(inst>>6)&0x1F;
		//Port indices
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;//Not used
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(ra_ind);
		core_current.Decode_destination_regindex=0xff;//Not used
		core_current.Execute_Imm=imm;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x7;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x7;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode:strh r%u,[r%u,#0x%X]\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode:strh r%u,[r%u,#0x%X]", ra_ind, rb_ind, imm);

		return;
    }
	#pragma endregion
    //STRH(2)
	//Instr 44 STRH
	#pragma region
    if((inst&0xFE00)==0x5200)
    {
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
        rc_ind=(inst>>6)&0x07;
		//Port indices
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=rc_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=read_register(rc_ind);

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Decode_destination_regindex=0xff;//Not used
		core_current.Execute_multicycle_regindex=9;
		core_current.Execute_Imm=0;//not used
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x7;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x7;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>6)&0x7;

		if(DEBUG_CORE)
			printf("Decode:strh r%u,[r%u,r%u]\n",ra_ind,rb_ind,rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode:strh r%u,[r%u,r%u]\n", ra_ind, rb_ind, rc_ind);
		return;
    }
	#pragma endregion
    //SUB(1)
	//Instr 10 Sub 2reg+imm
	#pragma region
    if((inst&0xFE00)==0x1E00)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
        rb_ind=(inst>>3)&0x7;
        imm=(inst>>6)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];//remain
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: subs r%u,r%u,#0x%X\n",ra_ind,rb_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode: subs r%u,r%u,#0x%X", ra_ind, rb_ind, imm);

        return;
    }
	#pragma endregion
    //SUB(2)
	//Instr 11: Sub 1reg+Imm
	#pragma region
    if((inst&0xF800)==0x3800)
    {
		//Port indices
		ra_ind=(inst>>8)&0x7;
        imm=(inst>>0)&0xFF;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=0;//Not used
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];//remain
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>8)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: subs r%u,#0x%X\n",ra_ind,imm);
		sprintf(core_current.Decode_instr_disp, "Decode: subs r%u,#0x%X", ra_ind, imm);
        return;

    }
	#pragma endregion
    //SUB(3)
	//Instr 9: sub 3regs
	#pragma region
    if((inst&0xFE00)==0x1A00)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
        rb_ind=(inst>>3)&0x7;
        rc_ind=(inst>>6)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rc_ind;
		core_current.Decode_port_regindex[2]=rb_ind;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rc_ind);
		core_current.Decode_port_data[2]=read_register(rb_ind);

		//registers
		core_current.D2E_reg1_data=read_register_forward(rb_ind);
		core_current.D2E_reg2_data=read_register_forward(rc_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>6)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=(next_inst>>3)&0x07;

		if(DEBUG_CORE)
			printf("Decode: subs r%u,r%u,r%u\n",ra_ind,rb_ind,rc_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: subs r%u,r%u,r%u", ra_ind, rb_ind, rc_ind);
        return;
    }
	#pragma endregion
    //SUB(4)
	//Sub SP=Sp-imm
	#pragma region
    if((inst&0xFF80)==0xB080)
    {
		//Port indices
		imm=(inst>>0)&0x7F;
        imm<<=2;

		core_current.Decode_port_regindex[0]=13;
		core_current.Decode_port_regindex[1]=0xff;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(13);
		core_current.Decode_port_data[1]=0;
		core_current.Decode_port_data[2]=0;

		//registers
		core_current.D2E_reg1_data=read_register_forward(13);
		//core_current.D2E_reg2_data=core_current.Decode_port_data[1];//Not used
		core_current.Execute_Imm=imm;
		core_current.Decode_destination_regindex=13;
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=false;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=0xff;
		core_current.glitchy_Decode_port_regindex[1]=0xff;
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: sub SP,#0x%02X\n",imm);
		sprintf(core_current.Decode_instr_disp, "Decode: sub SP,#0x%02X", imm);
        return;
    }
	#pragma endregion
    //SWI/SVC
	#pragma region
    if((inst&0xFF00)==0xDF00)
    {
        rb=inst&0xFF;
        if((inst&0xFF)==0xCC)
        {
			printf("Error! swi/svc 0x%02X\n",rb);
            return;
        }
        else
        {
            printf("\n\nswi 0x%02X\n",rb);
            return;
        }
    }
	#pragma endregion
    //SXTB
	//Instr 52
	#pragma region
    if((inst&0xFFC0)==0xB240)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[1];
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: sxtb r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: sxtb r%u,r%u\n", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    //SXTH
	//Instr 51
	#pragma region
    if((inst&0xFFC0)==0xB200)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[1];
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: sxth r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: sxth r%u,r%u\n", ra_ind, rb_ind);

		return;
    }
	#pragma endregion

    //TST
	//Instr 23
	#pragma region
    if((inst&0xFFC0)==0x4200)
    {
		//Port indices
		ra_ind=(inst>>0)&0x07;
        rb_ind=(inst>>3)&0x07;
		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;//Not used

		//registers
		core_current.D2E_reg1_data=read_register_forward(ra_ind);
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;
		core_current.Decode_destination_regindex=0xff;//Not used
		core_current.D2E_reg1_valid=true;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=(next_inst>>0)&0x07;
		core_current.glitchy_Decode_port_regindex[1]=(next_inst>>3)&0x07;
		core_current.glitchy_Decode_port_regindex[2]=0xff;//Not used

		if(DEBUG_CORE)
			printf("Decode: tst r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: tst r%u,r%u\n", ra_ind, rb_ind);

		return;
    }
	#pragma endregion
    //UXTB
	//Instr 54
	#pragma region
    if((inst&0xFFC0)==0xB2C0)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[1];
		core_current.D2E_reg2_data=read_register_forward(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: uxtb r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: uxtb r%u,r%u", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    //UXTH
	//Instr 53
	#pragma region
    if((inst&0xFFC0)==0xB280)
    {
		//Port indices
		ra_ind=(inst>>0)&0x7;
		rb_ind=(inst>>3)&0x7;

		core_current.Decode_port_regindex[0]=ra_ind;
		core_current.Decode_port_regindex[1]=rb_ind;
		core_current.Decode_port_regindex[2]=0xff;
		//Port data
		core_current.Decode_port_data[0]=read_register(ra_ind);
		core_current.Decode_port_data[1]=read_register(rb_ind);
		core_current.Decode_port_data[2]=0;

		//registers
		//core_current.D2E_reg1_data=core_current.Decode_port_data[1];
		core_current.D2E_reg2_data=read_register(rb_ind);
		core_current.Execute_Imm=0;//Not used
		core_current.Decode_destination_regindex=ra_ind;
		core_current.D2E_reg1_valid=false;
		core_current.D2E_reg2_valid=true;
		//Decode next instruction using the current decoder style
		core_current.glitchy_Decode_port_regindex[0]=((next_inst>>0)&0x7);
		core_current.glitchy_Decode_port_regindex[1]=((next_inst>>3)&0x7);
		core_current.glitchy_Decode_port_regindex[2]=0xff;

		if(DEBUG_CORE)
			printf("Decode: uxth r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Decode_instr_disp, "Decode: uxth r%u,r%u\n", ra_ind, rb_ind);
		return;
    }
	#pragma endregion
    printf("invalid instruction 0x%04X\n",inst);
    return;
}