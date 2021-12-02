#include "Configure.h"
#include "core.h"
#include "Execute.h"
#include "Decode.h"
//One cycle of execute; if return true, the decode/fetch will be stalled
bool Execute_OneCylce(bool wait_mem)
{
	unsigned int ra, rb, rc;
	uint8_t ra_ind, rb_ind;
	uint8_t rd_ind;
	unsigned int inst=core_current.D2E_instrreg;
	bool IsLDR=((inst&0xF800)==0x6800)||((inst&0xFE00)==0x5800)||((inst&0xF800)==0x4800)||((inst&0xF800)==0x9800)||((inst&0xF800)==0x7800)||((inst&0xFE00)==0x5C00)||((inst&0xF800)==0x8800)||((inst&0xFE00)==0x5A00)||((inst&0xFE00)==0x5600)||((inst&0xFE00)==0x5E00)||((inst&0xFE00)==0xBC00);
	if(!core_current.Execute_valid)//Jump happens, no need to execute this instruction
		return false;
	if((!IsLDR)&&core_current.Read_reg_update)//LDR is still runing, while the new one is not LDR
	{
		if(DEBUG_CORE)
				printf("LDR delay!\n");
		sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
		//nullified the target index propogated from the last Decode
		core_current.Execute_destination_regindex=0xff;
		//Re-do decode for LDR
		Decode_OneCycle(true);
		return true;
	}
    //ADC two registers
	//Instr 8
    #pragma region
    if((inst&0xFFC0)==0x4140)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;

		if(DEBUG_CORE)
			printf("adc r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: adc r%u,r%u\n", ra_ind, rb_ind);
		//Logical calculation 
		rc=ra+rb;
		if(core_current.cpsr&CPSR_C) rc=rc+1;
		
		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
		if(core_current.cpsr&CPSR_C) { do_cflag(ra,rb,1); do_vflag(ra,rb,1); }
        else            { do_cflag(ra,rb,0); do_vflag(ra,rb,0); }
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;

        return false;
    }
	#pragma endregion
    //ADD(1) small immediate two registers
	//Instr 4
	#pragma region
    if((inst&0xFE00)==0x1C00)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("adds r%u,r%u,#0x%X\n",rd_ind,ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: adds r%u,r%u,#0x%X\n", rd_ind, ra_ind, rb);
        //Logical calculation 
        rc=ra+rb;
		
		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,rb,0);
        do_vflag(ra,rb,0);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;

        return false;

    }
	#pragma endregion
    //ADD(2) big immediate one register
	#pragma region
    if((inst&0xF800)==0x3000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[0];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("adds r%u,#0x%02X\n",rd_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: adds r%u,#0x%02X", rd_ind, rb);

		//Functional
        rc=ra+rb;

		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,rb,0);
        do_vflag(ra,rb,0);
		core_current.cpsr_valid=true;		
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion

    //ADD(3) three registers
	#pragma region
    if((inst&0xFE00)==0x1800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[2];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("adds r%u,r%u,r%u\n",rd_ind,ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: adds r%u,r%u,r%u", rd_ind, ra_ind, rb_ind);
		//Functional
        rc=ra+rb;

		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,rb,0);
        do_vflag(ra,rb,0);
		core_current.cpsr_valid=true;		
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
#pragma endregion

    //ADD(4) two registers one or both high no flags
	//Instr 6
	#pragma region
    if((inst&0xFF00)==0x4400)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("add r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: add r%u,r%u", ra_ind, rb_ind);

		//Functional
        rc=ra+rb;

		//Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
        //do_cflag(ra,rb,0);
        //do_vflag(ra,rb,0);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //ADD(5) rd = pc plus immediate
	#pragma region
    if((inst&0xF800)==0xA000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("add r%u,PC,#0x%02X\n",rd_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: add r%u,PC,#0x%02X", rd_ind, rb);
		//Functional
        rc=ra+rb;

		//Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
        //do_cflag(ra,rb,0);
        //do_vflag(ra,rb,0);
		core_current.cpsr_valid=false;		
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;

    }
	#pragma endregion
    //ADD(6) rd = sp plus immediate
	#pragma region
    if((inst&0xF800)==0xA800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("add r%u,SP,#0x%02X\n",rd_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: add r%u,SP,#0x%02X", rd_ind, rb);

		//Functional
        rc=ra+rb;

		//Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
        //do_cflag(ra,rb,0);
        //do_vflag(ra,rb,0);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //ADD(7) sp plus immediate
	#pragma region
    if((inst&0xFF80)==0xB000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		rd_ind=13;
		if(DEBUG_CORE)
			printf("add SP,#0x%02X\n",rb);
		sprintf(core_current.Execute_instr_disp, "Execute: add SP,#0x%02X", rb);

		//Functional
        rc=ra+rb;

		//Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
        //do_cflag(ra,rb,0);
        //do_vflag(ra,rb,0);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion

    //AND
	//Instr 18
	#pragma region
    if((inst&0xFFC0)==0x4000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("ands r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: ands r%u,r%u", ra_ind, rb_ind);

		//Functional
        rc=ra&rb;

		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,rb,0);
        //do_vflag(ra,rb,0);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //ASR(1) two register immediate
	//Instr 28
    #pragma region
    if((inst&0xF800)==0x1000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("asrs r%u,r%u,#0x%X\n",rd_ind,ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: asrs r%u,r%u,#0x%X", rd_ind, ra_ind, rb);

		//Functional
		rc=ra;
        if(rb==0)
        {
            if(rc&0x80000000)
            {
                rc=~0;
            }
            else
            {
                rc=0;
            }
        }
        else
        {
            ra=rc&0x80000000;
            rc>>=rb;
            if(ra) //asr, sign is shifted in
            {
                rc|=(~0)<<(32-rb);
            }
        };

		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,rb,0);
        //do_vflag(ra,rb,0);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
    #pragma endregion
    //ASR(2) two register
	//Instr 29
	#pragma region
    if((inst&0xFFC0)==0x4100)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("asrs r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: asrs r%u,r%u", ra_ind, rb_ind);

		//Functional
        rc=ra;
        rb&=0xFF;
        if(rb==0)
        {

        }
        else if(rb<32)
        {
            ra=rc&0x80000000;
            rc>>=rb;
            if(ra) //asr, sign is shifted in
            {
                rc|=(~0)<<(32-rb);
            }
        }
        else
        {
            if(rc&0x80000000)
            {
                rc=(~0);
            }
            else
            {
                rc=0;
            }
        }

		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,rb,0);
        //do_vflag(ra,rb,0);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //B(1) conditional branch
	//Instr 49
	#pragma region
    if((inst&0xF000)==0xD000)
    {
		//According to paper
		rb=core_current.Execute_Imm;
		rd_ind=15;
		if(rb&0x80) 
		{
            unsigned int tmp = ~0;
            tmp <<= 8;
            rb|=tmp;
		}
		rc=read_register(15)-2;
		rb<<=1;
		rb=rb+rc;
		rb=rb+2;

		//Functional
        switch((inst>>8)&0xF)
        {
            case 0x0: //b eq  z set
                if(core_current.cpsr&CPSR_Z)
                {
                    rc=rb;
                }
				if(DEBUG_CORE)
					printf("beq 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: beq 0x%08X", rb - 3);

				break;

            case 0x1: //b ne  z clear
                if(!(core_current.cpsr&CPSR_Z))
                {
                    rc=rb;
                }
				if(DEBUG_CORE)
					printf("bne 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bne 0x%08X", rb - 3);
                break;

            case 0x2: //b cs c set
                if(core_current.cpsr&CPSR_C)
                {
                    rc=rb;
                }
				if(DEBUG_CORE)
					printf("bcs 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bcs 0x%08X", rb - 3);
                break;

            case 0x3: //b cc c clear
                if(!(core_current.cpsr&CPSR_C))
                {
                     rc=rb;
                }
                if(DEBUG_CORE)
					printf("bcc 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bcc 0x%08X", rb - 3);
                break;

            case 0x4: //b mi n set
                if(core_current.cpsr&CPSR_N)
                {
                    rc=rb;
                }
				if(DEBUG_CORE)
					printf("bmi 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bmi 0x%08X", rb - 3);
                break;

            case 0x5: //b pl n clear
                if(!(core_current.cpsr&CPSR_N))
                {
                    rc=rb;
                }
                if(DEBUG_CORE)
					printf("bpl 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bpl 0x%08X", rb - 3);
                break;

            case 0x6: //b vs v set
                if(core_current.cpsr&CPSR_V)
                {
                    rc=rb;
                }
                if(DEBUG_CORE)
					printf("bvs 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bvs 0x%08X", rb - 3);
                break;

            case 0x7: //b vc v clear
                if(!(core_current.cpsr&CPSR_V))
                {
                    rc=rb;
                }
                if(DEBUG_CORE)
					printf("bvc 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bvc 0x%08X", rb - 3);
                break;

            case 0x8: //b hi c set z clear
                if((core_current.cpsr&CPSR_C)&&(!(core_current.cpsr&CPSR_Z)))
                {
                   rc=rb;
                }
                if(DEBUG_CORE)
					 printf("bhi 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bhi 0x%08X", rb - 3);
                break;

            case 0x9: //b ls c clear or z set
                if((core_current.cpsr&CPSR_Z)||(!(core_current.cpsr&CPSR_C)))
                {
                    rc=rb;
                }
                if(DEBUG_CORE)
					 printf("bls 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bls 0x%08X", rb - 3);
                break;

            case 0xA: //b ge N == V
                ra=0;
                if(  (core_current.cpsr&CPSR_N) &&  (core_current.cpsr&CPSR_V) ) ra++;
                if((!(core_current.cpsr&CPSR_N))&&(!(core_current.cpsr&CPSR_V))) ra++;
                if(ra)
                {
                   rc=rb;
                }
                if(DEBUG_CORE)
					printf("bge 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bge 0x%08X", rb - 3);
                break;

            case 0xB: //b lt N != V
                ra=0;
                if((!(core_current.cpsr&CPSR_N))&&(core_current.cpsr&CPSR_V)) ra++;
                if((!(core_current.cpsr&CPSR_V))&&(core_current.cpsr&CPSR_N)) ra++;
                if(ra)
                {
                    rc=rb;
                }

                if(DEBUG_CORE)
					printf("blt 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: blt 0x%08X", rb - 3);
				break;

            case 0xC: //b gt Z==0 and N == V
                ra=0;
                if(  (core_current.cpsr&CPSR_N) &&  (core_current.cpsr&CPSR_V) ) ra++;
                if((!(core_current.cpsr&CPSR_N))&&(!(core_current.cpsr&CPSR_V))) ra++;
                if(core_current.cpsr&CPSR_Z) ra=0;
                if(ra)
                {
                    rc=rb;
                }
                if(DEBUG_CORE)
					printf("bgt 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: bgt 0x%08X", rb - 3);
                break;

            case 0xD: //b le Z==1 or N != V
                ra=0;
                if((!(core_current.cpsr&CPSR_N))&&(core_current.cpsr&CPSR_V)) ra++;
                if((!(core_current.cpsr&CPSR_V))&&(core_current.cpsr&CPSR_N)) ra++;
                if(core_current.cpsr&CPSR_Z) ra++;
                if(ra)
                {
                   rc=rb;
                }
                if(DEBUG_CORE)
					 printf("ble 0x%08X\n",rb-3);
				sprintf(core_current.Execute_instr_disp, "Execute: ble 0x%08X", rb - 3);
                break;

            case 0xE:
                //undefined instruction
                break;
            case 0xF:
                //swi
                break;
        }
		
		
		//branch taken
		//if(read_register(15)+2!=rc)
		//{
			//Update ALU output
			core_current.Execute_ALU_result=rc;
			core_current.Execute_destination_regindex=15;
			write_register(core_current.Execute_destination_regindex,core_current.Execute_ALU_result);
			core_current.Execute_destination_regindex=0xff;
			core_current.Decode_destination_regindex=0xff;
			//Set the following two instruction to invalid
			core_current.Fetch_valid = false;
			core_current.Decode_valid=false;
			core_current.Execute_valid=false;
			core_current.cpsr_valid=false;
		//}
        return false;

    }
	#pragma endregion

    //B(2) unconditional branch
	//Instr 49
	#pragma region
    if((inst&0xF800)==0xE000)
    {
		//According to paper
		rb=core_current.Execute_Imm;
		rd_ind=15;
        if(rb&(1<<10)) 
		{
            unsigned int tmp = ~0;
            tmp <<= 11;
            rb|=tmp;
        }

        rb<<=1;
        rb+=read_register(15);

		if(DEBUG_CORE)
			printf("B 0x%08X\n",rb-3);
		sprintf(core_current.Execute_instr_disp, "Execute: B 0x%08X", rb - 3);
		//Update ALU output
		core_current.Execute_ALU_result = rb;
		core_current.Execute_destination_regindex = 15;
		write_register(core_current.Execute_destination_regindex, core_current.Execute_ALU_result);
		core_current.Execute_destination_regindex = 0xff;
		core_current.Decode_destination_regindex = 0xff;
		//Set the following two instruction to invalid
		core_current.Decode_valid = false;
		core_current.Execute_valid = false;
		core_current.cpsr_valid = false;
        return false;
    }
#pragma endregion
    //BIC two registers
	//Instr 21
#pragma region
    if((inst&0xFFC0)==0x4380)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("bics r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: bics r%u,r%u", ra_ind, rb_ind);
		//Functional
		rc=ra&(~rb);

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,rb,0);
        //do_vflag(ra,rb,0);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
#pragma endregion
    //BKPT: enter the debug mode; ignored
#pragma region
    if((inst&0xFF00)==0xBE00)
    {
        //rb=(inst>>0)&0xFF;
        //fprintf(stderr,"bkpt 0x%02X\n",rb);
		printf("Error! Do not support BKPT instruction!\n");
        return false;
    }
#pragma endregion
    //BL/BLX(1)
	//Instr 50
#pragma region
    if((inst&0xE000)==0xE000) //BL,BLX
    {
		core_current.cpsr_valid=false;
        if((inst&0x1800)==0x1000) //H=b10
        {
			rb=core_current.Execute_Imm;
			rd_ind=14;
            if(rb&1<<10) rb|=(~((1<<11)-1)); //sign extend
            rb<<=12;
            rb+=read_register(15)-2;
			if(DEBUG_CORE)
				printf("b1 pre-fix\n");
			sprintf(core_current.Execute_instr_disp, "Execute: b1 pre-fix");
			//Update ALU output
			core_current.Execute_ALU_result=rb;
			core_current.Execute_destination_regindex=14;
			return false;
        }
        else
        if((inst&0x1800)==0x1800) //H=b11
        {
            //branch to thumb
            rb=read_register_forward(14);
            rb+=core_current.Execute_Imm;
            rb+=2;
			rd_ind=15;
            write_register(14,(read_register(15)-4)|1);
			if(DEBUG_CORE)
				printf("bl 0x%08X\n",rb-3);
			sprintf(core_current.Execute_instr_disp, "Execute: bl 0x%08X", rb - 3);
			//Update ALU output
			core_current.Execute_ALU_result=rb;
			core_current.Execute_destination_regindex=15;
			write_register(core_current.Execute_destination_regindex,core_current.Execute_ALU_result);
			core_current.Execute_destination_regindex=0xff;
			core_current.Decode_destination_regindex=0xff;
            //Set the following two instruction to invalid
			core_current.Fetch_valid = false;
			core_current.Decode_valid=false;
			core_current.Execute_valid=false;
			return false;
        }
        else
        if((inst&0x1800)==0x0800) //H=b01
        {
            //fprintf(stderr,"cannot branch to arm 0x%08X 0x%04X\n",pc,inst);
            //return(1);
            //branch to thumb
            rb=read_register(14);
            rb+=core_current.Execute_Imm;
            rb&=0xFFFFFFFC;
            rb+=2;
			rd_ind=15;

            write_register(14,(read_register(15)-2)|1);
            if(DEBUG_CORE)
				printf("bl 0x%08X\n",rb-3);

			//Update ALU output
			core_current.Execute_ALU_result=rb;
			core_current.Execute_destination_regindex=15;
			write_register(core_current.Execute_destination_regindex,core_current.Execute_ALU_result);
			core_current.Execute_destination_regindex=0xff;
			core_current.Decode_destination_regindex=0xff;
            //Set the following two instruction to invalid
			core_current.Fetch_valid = false;
			core_current.Decode_valid=false;
			core_current.Execute_valid=false;
			return false;
        }
    }
#pragma endregion
    //BLX(2)
	//Instr 50
#pragma region
    if((inst&0xFF87)==0x4780)
    {
		ra_ind=core_current.Decode_port_regindex[0];
		rc=core_current.D2E_reg1;
		rd_ind=15;
        rc+=2;
		core_current.cpsr_valid=false;
        if(rc&1)
        {
            write_register(14,(read_register(15)-2)|1);
            rc&=~1;

			if(DEBUG_CORE)
				printf("blx r%u\n",ra_ind);
			sprintf(core_current.Execute_instr_disp, "Execute:blx r%u", ra_ind);
			//Update ALU output
			core_current.Execute_ALU_result=rc;
			core_current.Execute_destination_regindex=15;
			write_register(core_current.Execute_destination_regindex,core_current.Execute_ALU_result);
			core_current.Execute_destination_regindex=0xff;
			core_current.Decode_destination_regindex=0xff;
            //Set the following two instruction to invalid
			core_current.Fetch_valid = false;
			core_current.Decode_valid=false;
			core_current.Execute_valid=false;
			return false;
        }
        else
        {
            printf("cannot branch to arm 0x%08X 0x%04X\n",read_register(15),inst);
            return(1);
        }
    }
	#pragma endregion
    //BX
	//Instr 50
	#pragma region
    if((inst&0xFF87)==0x4700)
    {
			ra_ind=core_current.Decode_port_regindex[0];
			rd_ind=15;
			rc=core_current.D2E_reg1;
			rc+=2;
            if(DEBUG_CORE)
				printf("bx r%u\n",ra_ind);
			sprintf(core_current.Execute_instr_disp, "Execute: bx r%u", ra_ind);

			core_current.cpsr_valid=false;
			//Update ALU output
			core_current.Execute_ALU_result=rc;
			core_current.Execute_destination_regindex=15;
			write_register(core_current.Execute_destination_regindex,core_current.Execute_ALU_result);
			core_current.Execute_destination_regindex=0xff;
			core_current.Decode_destination_regindex=0xff;
            //Set the following two instruction to invalid
			core_current.Fetch_valid = false;
			core_current.Decode_valid=false;
			core_current.Execute_valid=false;
			return false;
    }
#pragma endregion
    //CMN
#pragma region
    if((inst&0xFFC0)==0x42C0)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=0xff;//Do not produce result written to rd
		if(DEBUG_CORE)
			printf("cmns r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute:cmns r%u,r%u", ra_ind, rb_ind);

		//Functional
		rc=ra+rb;

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,rb,0);
        do_vflag(ra,rb,0);
		core_current.cpsr_valid=true;	
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
#pragma endregion
    //CMP(1) compare immediate
	//Instr 17
#pragma region
    if((inst&0xF800)==0x2800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=0xff;//Do not produce result written to rd
		if(DEBUG_CORE)
			printf("cmp r%u,#0x%02X\n",ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute:cmp r%u,#0x%02X", ra_ind, rb);
		//Functional
		rc=ra-rb;

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,~rb,1);
        do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
		core_current.Execute_destination_regindex=0xff;
        return false;
    }
#pragma endregion
    //CMP(2) compare register
	//Instr 15
#pragma region
    if((inst&0xFFC0)==0x4280)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=0xff;//Do not produce result written to rd
		if(DEBUG_CORE)
			printf("cmps r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute:cmps r%u,r%u", ra_ind, rb_ind);
		//Functional
		rc=ra-rb;

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,~rb,1);
        do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
		core_current.Execute_destination_regindex=0xff;
        return false;
    }
	#pragma endregion
    //CMP(3) compare high register
	#pragma region
    if((inst&0xFF00)==0x4500)
    {
       
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=0xff;//Do not produce result written to rd
		if(DEBUG_CORE)
			printf("cmps r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute:cmps r%u,r%u", ra_ind, rb_ind);
		//Functional
		rc=ra-rb;

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,~rb,1);
        do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
		core_current.Execute_destination_regindex=0xff;
		return;
    }
	#pragma endregion
    //CPS change processor state
	#pragma region
    if((inst&0xFFE8)==0xB660)
    {
        printf("Error! CPS not supported\n");
        return(1);
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
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		if(DEBUG_CORE)
			printf("eors r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute:eors r%u,r%u", ra_ind, rb_ind);
		//Functional
		rc=ra^rb;

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
		core_current.Execute_destination_regindex=ra_ind;
        return false;
    }
	#pragma endregion

    //LDMIA
	//Instr 39
	#pragma region
    if((inst&0xF800)==0xC800)
    {
		if (check_delay(core_current.Decode_port_regindex[2]) == true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
		//According to paper
		ra=core_current.D2E_reg1;
		rd_ind=core_current.Execute_destination_regindex;
		rb_ind=core_current.Execute_multicycle_regindex;
		if(rb_ind==9)
			rb_ind=0;//start from 0 and load
        while(rb_ind<8)
        {
			rb=(0x1<<rb_ind)&0xff;
            if(inst&rb)//Find one register to fill
            {
				core_current.Memory_read_targetreg=rb_ind;//sent to memory
				core_current.Memory_addr=ra;
				core_current.Read_valid=true;
				core_current.Read_type=0;
				core_current.Execute_multicycle_regindex=rb_ind+1;//next register
				sprintf(core_current.Execute_instr_disp, "Execute: STMIA r%u=0x%X",rb_ind,ra);
				ra=ra+4;
				core_current.D2E_reg1_data=ra;//update address
				core_current.D2E_reg1_valid=true;
				core_current.D2E_reg2_valid=false;
				core_current.cpsr_valid=false;
				break;
            }
			rb_ind++;
        }
        //there is a write back exception.
        if((inst&(1<<rd_ind))==0)
		{
			   //Update ALU output
			   core_current.Execute_ALU_result=ra;
			   core_current.Execute_destination_regindex=rd_ind;
				//Update destination register
				write_register(rd_ind,core_current.Execute_ALU_result);
		}
		if(rb_ind<8)
			return true;
		else
			return false;

    }
	#pragma endregion
    //LDR(1) two register immediate
	//Instr 31
	#pragma region
    if((inst&0xF800)==0x6800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Decode_port_regindex[0];
		rb<<=2;
        rc=ra+rb;
		if (check_delay(ra_ind) == true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
		if(DEBUG_CORE)
			printf("ldr r%u,[r%u,#0x%X]\n",rd_ind,ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: ldr r%u,[r%u,#0x%X]", rd_ind, ra_ind, rb);
		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Read_valid=true;
		core_current.Read_type=0;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
		return false;
    }
	#pragma endregion
    //LDR(2) three register
	//Instr 34
	#pragma region
    if((inst&0xFE00)==0x5800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[1];
		rb_ind=core_current.Decode_port_regindex[2];
		rd_ind=core_current.Decode_port_regindex[0];
        rc=ra+rb;
		if (check_delay(ra_ind) == true || check_delay(rb_ind)==true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
		if(DEBUG_CORE)
			printf("ldr r%u,[r%u,r%u]\n",rd_ind,ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: ldr r%u,[r%u,r%u]", rd_ind, ra_ind, rb_ind);
		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Read_valid=true;
		core_current.Read_type=0;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
		return false;
    }
	#pragma endregion
    //LDR(3)
	//rd=[PC+offset]: treat like LDRI 31
	#pragma region
    if((inst&0xF800)==0x4800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=15;
		rd_ind=core_current.Decode_port_regindex[0];
		rb<<=2;
        ra&=~3;
        rc=ra+rb;
		if(DEBUG_CORE)
			printf("ldr r%u,[PC+#0x%X]\n",rd_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: ldr r%u,[PC+#0x%X]", rd_ind, rb);
		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Read_valid=true;
		core_current.Read_type=0;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //Let memory do this
		core_current.cpsr_valid=false;
		return false;
    }
	#pragma endregion

    //LDR(4)
	//Load rd [Sp+imm], treat as LDRI Instr 31
	#pragma region
    if((inst&0xF800)==0x9800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		rb<<=2;
		ra_ind=13;
		rd_ind=core_current.Decode_port_regindex[0];
		if (check_delay(13) == true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
        rc=ra+rb;
		if(DEBUG_CORE)
			printf("ldr r%u,[SP+#0x%X]\n",rd_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: ldr r%u,[SP+#0x%X]", rd_ind, rb);
		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Read_valid=true;
		core_current.Read_type=0;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
		return false;
    }
	#pragma endregion
    //LDRB(1)
	//Instr 33 LDRBI
	#pragma region
    if((inst&0xF800)==0x7800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Decode_port_regindex[0];
        rc=ra+rb;
		if (check_delay(ra_ind) == true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
		//rc=rc&(~1);
        //if(rb&1)
        //{
        //    rc>>=8;
        //}
		if(DEBUG_CORE)
			printf("ldrb r%u,[r%u,#0x%X]\n",rd_ind,ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: ldrb r%u,[r%u,#0x%X]", rd_ind, ra_ind, rb);
		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Read_valid=true;
		core_current.Read_type=1;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
		return false;
    }
	#pragma endregion

    //LDRB(2)
	//Instr 37  LDRB 2reg
	#pragma region
    if((inst&0xFE00)==0x5C00)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[1];
		rb_ind=core_current.Decode_port_regindex[2];
		rd_ind=core_current.Decode_port_regindex[0];
        rc=ra+rb;
		if (check_delay(ra_ind) == true||check_delay(rb_ind)==true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
		//rc=rc&(~1);
		//if(rb&1)
        //{
        //    rc>>=8;
       // }
		if(DEBUG_CORE)
			printf("ldrb r%u,[r%u,r%u]\n",rd_ind,ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: ldrb r%u,[r%u,r%u]", rd_ind, ra_ind, rb_ind);
		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Read_valid=true;
		core_current.Read_type=1;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
		return false;
    }
	#pragma endregion
    //LDRH(1)
	//Instr 32  LDRHI
	#pragma region
    if((inst&0xF800)==0x8800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		rb<<=1;
		ra_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Decode_port_regindex[0];
        rc=ra+rb;
		if (check_delay(ra_ind) == true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
		if(DEBUG_CORE)
			printf("ldrh r%u,[r%u,#0x%X]\n",rd_ind,ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: ldrh r%u,[r%u,#0x%X]", rd_ind, ra_ind, rb);

		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Read_valid=true;
		core_current.Read_type=2;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
		return false;
    }
	#pragma endregion
    //LDRH(2)
	//Instr 35 LDRH 2reg
	#pragma region
    if((inst&0xFE00)==0x5A00)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[1];
		rb_ind=core_current.Decode_port_regindex[2];
		rd_ind=core_current.Decode_port_regindex[0];
		if (check_delay(ra_ind) == true||check_delay(rb_ind)==true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
        rc=ra+rb;
		if(DEBUG_CORE)
			printf("ldrh r%u,[r%u,r%u]\n",rd_ind,ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: ldrh r%u,[r%u,r%u]", rd_ind, ra_ind, rb_ind);
		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Read_valid=true;
		core_current.Read_type=2;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
		return false;

    }
	#pragma endregion

    //LDRSB
	//Instr 38 2reg
	#pragma region
    if((inst&0xFE00)==0x5600)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[1];
		rb_ind=core_current.Decode_port_regindex[2];
		rd_ind=core_current.Decode_port_regindex[0];
        rc=ra+rb;
		if (check_delay(ra_ind) == true||check_delay(rb_ind)==true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
		//rc=rc&(~1);
		if(DEBUG_CORE)
			printf("ldrsb r%u,[r%u,r%u]\n",rd_ind,ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: ldrsb r%u,[r%u,r%u]", rd_ind, ra_ind, rb_ind);
		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.SignExtend_byte_valid=true;
		core_current.Read_valid=true;
		core_current.Read_type=1;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
		return false;

    }
	#pragma endregion
    //LDRSH
	//Instr 35 2reg
	#pragma region
    if((inst&0xFE00)==0x5E00)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[1];
		rb_ind=core_current.Decode_port_regindex[2];
		rd_ind=core_current.Decode_port_regindex[0];
        rc=ra+rb;
		if (check_delay(ra_ind) == true||check_delay(rb_ind)==true)
		{
			if (DEBUG_CORE)
				printf("LDR delay!\n");
			sprintf(core_current.Execute_instr_disp, "Execute: stall by LDR");
			//nullified the target index propogated from the last Decode
			core_current.Execute_destination_regindex = 0xff;
			//Re-do decode for LDR
			Decode_OneCycle(true);
			return true;
		}
		if(DEBUG_CORE)
			printf("ldrsh r%u,[r%u,r%u]\n",rd_ind,ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: ldrsh r%u,[r%u,r%u]", rd_ind, ra_ind, rb_ind);
		core_current.Memory_read_targetreg=rd_ind;//sent to memory
		core_current.Memory_addr=rc;
		core_current.SignExtend_halfbyte_valid=true;
		core_current.Read_valid=true;
		core_current.Read_type=2;
		//Update ALU output
	    core_current.Execute_ALU_result=rc;
	    core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
		return false;
    }
	#pragma endregion
    //LSL(1)
	//Instr 24 LSLI
	#pragma region
    if((inst&0xF800)==0x0000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[0];;
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("lsls r%u,r%u,#0x%X\n",rd_ind,ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: lsls r%u,r%u,#0x%X", rd_ind, ra_ind, rb);
		//Functional
		rc=ra;
		if(rb!=0)
        {
            //else immed_5 > 0
            unsigned int shifted = 1;
            shifted = shifted << (32 - rb);
            do_cflag_bit(rc&shifted);
            rc<<=rb;
        }
        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
	    core_current.cpsr_valid=true;
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion

    //LSL(2) two register
	//Instr 25 LSL 2 reg
	#pragma region
    if((inst&0xFFC0)==0x4080)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("lsls r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: lsls r%u,r%u\n", ra_ind, rb_ind);
		//Functional
		rc=ra;
		rb&=0xFF;
        if(rb==0)
        {
        }
        else if(rb<32)
        {
            unsigned int shifted = 1;
            shifted = shifted << (32 - rb);
            do_cflag_bit(rc&shifted);
            rc<<=rb;

        }
        else if(rb==32)
        {
            do_cflag_bit(rc&1);
            rc=0;
        }
        else
        {
            do_cflag_bit(0);
            rc=0;
        }

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;		
		//Update ALU output
		core_current.Execute_ALU_result=rc;

        return false;
    }
	#pragma endregion
    //LSR(1) two register immediate
	//Instr 26: LSRI
	#pragma region
    if((inst&0xF800)==0x0800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[0];;
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("lsrs r%u,r%u,#0x%X\n",rd_ind,ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: lsrs r%u,r%u,#0x%X", rd_ind, ra_ind, rb);
		rc=ra;
		//Functional
		if(rb==0)
        {
            do_cflag_bit(rc&0x80000000);
            rc=0;
        }
        else
        {
            do_cflag_bit(rc&(1<<(rb-1)));
            rc>>=rb;
        }
        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //LSR(2) two register
	//Instr 27 LSR two registers
	#pragma region
    if((inst&0xFFC0)==0x40C0)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("lsrs r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: lsrs r%u,r%u", ra_ind, rb_ind);
		//Functional
		rc=ra;
		rb&=0xFF;
        if(rb==0)
        {
        }
        else if(rb<32)
        {
            do_cflag_bit(rc&(1<<(rb-1)));
            rc>>=rb;
        }
        else if(rb==32)
        {
            do_cflag_bit(rc&0x80000000);
            rc=0;
        }
        else
        {
            do_cflag_bit(0);
            rc=0;
        }

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion

    //MOV(1) immediate
	//Instr 1: movs imm
	#pragma region
    if((inst&0xF800)==0x2000)
    {
		//According to paper;
		rb=core_current.Execute_Imm;
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("movs r%u,#0x%02X\n",rd_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: movs r%u,#0x%02X", rd_ind, rb);
		//Functional
		rc=rb;
		
        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
#pragma endregion
    //MOV(2) two low registers
	//Instr 2: movs low reg
	#pragma region
    if((inst&0xFFC0)==0x1C00)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		ra_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("movs r%u,r%u\n",rd_ind,ra_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: movs r%u,r%u", rd_ind, ra_ind);
		//Functional
		rc=ra;
		
        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
		do_cflag_bit(0);
        do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
		//Update destination register
		write_register(rd_ind,core_current.Execute_ALU_result);
        return false;
    }
	#pragma endregion
    //MOV(3)
	// Instr 3: mov high reg
	#pragma region
    if((inst&0xFF00)==0x4600)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("mov r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: mov r%u,r%u", rd_ind, rb_ind);
		//Functional
		rc=rb;
		if(rd_ind==15)
        {

            rc&=~1; //write_register may do this as well
            rc+=2; //The program counter is special
        }
        //Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //MUL
	//Instr 14
	#pragma region
    if((inst&0xFFC0)==0x4340)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("muls r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: muls r%u,r%u", ra_ind, rb_ind);
		//Functional
		rc=ra*rb;

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
		//Update destination register
		write_register(rd_ind,core_current.Execute_ALU_result);
        return false;
    }
	#pragma endregion
    //MVN
	//Instr 22
	#pragma region
    if((inst&0xFFC0)==0x43C0)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("mvns r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: mvns r%u,r%u", rd_ind, rb_ind);
		//Functional
		rc=(~rb);
        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //NEG/RSB
	//Instr 13
	#pragma region
    if((inst&0xFFC0)==0x4240)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("negs r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: negs r%u,r%u\n", rd_ind, rb_ind);
		//Functional
		rc=0-rb;
        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        do_cflag(0,~rb,1);
        do_vflag(0,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //ORR
	//Instr 20
	#pragma region
    if((inst&0xFFC0)==0x4300)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("orrs r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: orrs r%u,r%u", ra_ind, rb_ind);
		//Functional
		rc=ra|rb;

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
		//Update destination register
		write_register(rd_ind,core_current.Execute_ALU_result);
        return false;
    }
	#pragma endregion
    //POP
	//Instr 48=LDM
	#pragma region
    if((inst&0xFE00)==0xBC00)
    {
		bool find = false;
		//According to paper
		ra=read_register(13);
		rb_ind=core_current.Execute_multicycle_regindex;
		if(rb_ind==9)
			rb_ind=0;//start from 0 and load
		core_current.cpsr_valid=false;
        while(rb_ind<8)
        {
			rb=(0x1<<rb_ind)&0xff;
            if(inst&rb)//Find one register to fill
            {
				core_current.Memory_read_targetreg=rb_ind;//sent to memory
				core_current.Memory_addr=ra;
				sprintf(core_current.Execute_instr_disp, "Execute: pop r%u", rb_ind);
				core_current.Read_valid=true;
				core_current.Read_type=0;
				core_current.Execute_multicycle_regindex=rb_ind+1;//next register
				ra=ra+4;
				write_register( 13, ra);//update address
				rb_ind++;
				find = true;
				break;
            }
			rb_ind++;
        }
		core_current.Execute_destination_regindex=0xff;
		
		if(find)//already find one low reg to pop
		{
			if((((inst&0xff)>>(rb_ind-1))>0)||(inst&0x100>0))//more to pop)
				return true;
			else//Finish pop
			{
				core_current.Execute_destination_regindex=0xff; //do not update this
				core_current.Execute_multicycle_regindex=9;//next register
				return false;
			}
		}
		else//Did not find one low reg to pop
		{
			core_current.Execute_destination_regindex=0xff; //do not update this
			if(inst&0x100)//check if pc need to pop
			{
				core_current.Memory_read_targetreg=15;//sent to memory
				core_current.Memory_addr=ra;
				core_current.Read_valid=true;
				core_current.Read_type=0;
				core_current.Execute_multicycle_regindex=9;//next register
				ra=ra+4;
				sprintf(core_current.Execute_instr_disp, "Execute: pop PC");
				write_register( 13, ra);//update address
				//Set the following two instruction to invalid
				core_current.Decode_destination_regindex=0xff;
				core_current.Execute_destination_regindex=0xff;
				core_current.Fetch_valid = false;
				core_current.Decode_valid=false;
				core_current.Execute_valid=false;
				return true;
			}
			else
				return false;
		}
    }
	#pragma endregion
    //PUSH
	//Instr 49, =STM
	#pragma region
    if((inst&0xFE00)==0xB400)
    {
		ra=read_register(13);
		rb_ind=core_current.Execute_multicycle_regindex;
		if(rb_ind==9)
		{
			rb_ind=0;//start from 0 and store
			if(inst&0x100)//push lr
			{
				ra=ra-4;
				core_current.Memory_data=read_register(14);//sent to memory
				core_current.Memory_addr=ra;
				sprintf(core_current.Execute_instr_disp, "Execute: push lr=0x%X", core_current.Memory_data);
				core_current.Write_valid=true;
				core_current.Write_type=0;
				core_current.Execute_multicycle_regindex=0;//next register
				core_current.cpsr_valid=false;
				core_current.Execute_destination_regindex=0xff;
				write_register( 13, ra);//update address
				return true;
			}
		}
		core_current.cpsr_valid=false;
		 while(rb_ind<8)
        {
			rb=(0x1<<(7-rb_ind))&0xff;
            if(inst&rb)//Find one register to fill
            {
				ra=ra-4;
				core_current.Memory_data=read_register(7-rb_ind);//sent to memory
				sprintf(core_current.Execute_instr_disp, "Execute: push r%u=0x%X", 7-rb_ind,core_current.Memory_data);

				core_current.Memory_addr=ra;
				core_current.Write_valid=true;
				core_current.Write_type=0;
				core_current.Execute_multicycle_regindex=rb_ind+1;//next register
				write_register( 13, ra);//update address
				rb_ind++;
				break;
            }
			rb_ind++;
        }
		 core_current.Execute_destination_regindex=0xff;

		if((rb_ind<8) &&((inst&((0x1<<(8-rb_ind))-1))>0))
			return true;
		else
		{
			core_current.Execute_multicycle_regindex=9;
			return false;
		}
    }
	#pragma endregion
    //REV
	//Instr 55 two regs
	#pragma region
    if((inst&0xFFC0)==0xBA00)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("rev r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: rev r%u,r%u", rd_ind, rb_ind);


		//Functional
		rc =((rb>> 0)&0xFF)<<24;
        rc|=((rb>> 8)&0xFF)<<16;
        rc|=((rb>>16)&0xFF)<< 8;
        rc|=((rb>>24)&0xFF)<< 0;
        //Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=false;	
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //REV16
	//Instr 56
	#pragma region
    if((inst&0xFFC0)==0xBA40)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("rev16 r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: rev16 r%u,r%u", rd_ind, rb_ind);
		//Functional
        rc =((rb>> 0)&0xFF)<< 8;
        rc|=((rb>> 8)&0xFF)<< 0;
        rc|=((rb>>16)&0xFF)<<24;
        rc|=((rb>>24)&0xFF)<<16;
        //Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //REVSH
	//Instr 57
	#pragma region
    if((inst&0xFFC0)==0xBAC0)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("revsh r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: revsh r%u,r%u", rd_ind, rb_ind);
		//Functional
        rc =((rb>> 0)&0xFF)<< 8;
        rc|=((rb>> 8)&0xFF)<< 0;
        //Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //ROR
	//Instr 30
	#pragma region
    if((inst&0xFFC0)==0x41C0)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("rors r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: rors r%u,r%u", rd_ind, rb_ind);
		//Functional
		rb&=0xFF;
		rc=ra;
		if(rb==0)
        {
        }
        else
        {
            rb&=0x1F;
            if(rb==0)
            {
                do_cflag_bit(rc&0x80000000);
            }
            else
            {
                do_cflag_bit(rc&(1<<(rb-1)));
                ra=rc<<(32-rb);
                rc>>=rb;
                rc|=ra;
            }
        }

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
   //SBC
	//Instr 12
	#pragma region
    if((inst&0xFFC0)==0x4180)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;

		if(DEBUG_CORE)
			printf("sbc r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: sbc r%u,r%u", ra_ind, rb_ind);
		//Logical calculation 
		rc=ra-rb;
        if(!(core_current.cpsr&CPSR_C)) rc--;
		
		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
		if(core_current.cpsr&CPSR_C) { do_cflag(ra,~rb,1); do_vflag(ra,~rb,1); }
        else            { do_cflag(ra,~rb,0); do_vflag(ra,~rb,0); }
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;

    }
	#pragma endregion
    //SETEND
	#pragma region
    if((inst&0xFFF7)==0xB650)
    {
		printf("setend not implemented\n");
        return false;
    }
	#pragma endregion
    //STMIA
	//Instr 46
	#pragma region
    if((inst&0xF800)==0xC000)
    {
		ra_ind=core_current.Decode_port_regindex[2];
		ra=core_current.D2E_reg1;
		rb_ind=core_current.Execute_multicycle_regindex;
		if(rb_ind==9)
			rb_ind=0;//start from 0 and load
		core_current.cpsr_valid=false;
		 while(rb_ind<8)
        {
			rb=(0x1<<rb_ind)&0xff;
            if(inst&rb)//Find one register to fill
            {
				core_current.Memory_data=read_register(rb_ind);//sent to memory
				core_current.Memory_addr=ra;
				sprintf(core_current.Execute_instr_disp, "Execute: stmia r%u", rb_ind);
				core_current.Write_valid=true;
				core_current.Write_type=0;
				core_current.Execute_multicycle_regindex=rb_ind+1;//next register
				ra=ra+4;
				write_register( ra_ind, ra);//update address
				break;
            }
			rb_ind++;
        }
		 core_current.Execute_destination_regindex=0xff;
		if(rb_ind<8)
			return true;
		else
		{
			core_current.Execute_destination_regindex=0xff; //do not update this
			if(inst&0x100)//push pc
			{
				core_current.Memory_data=read_register(15);//sent to memory
				core_current.Memory_addr=ra;
				sprintf(core_current.Execute_instr_disp, "Execute: stmia pc");
				core_current.Write_valid=true;
				core_current.Write_type=0;
				core_current.Execute_multicycle_regindex=rb_ind+1;//next register
				ra=ra+4;
				write_register( ra_ind, ra);//update address
				//Set the following two instruction to invalid
				core_current.Fetch_valid = false;
				core_current.Decode_valid=false;
				core_current.Execute_valid=false;
				return true;
			}
			else
				return false;
		}
    }
	#pragma endregion
    //STR(1)
	//Instr 40 STRI
	#pragma region
    if((inst&0xF800)==0x6000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		rc=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[1];
		rb_ind=core_current.Decode_port_regindex[0];
		rd_ind=0xff;//not used
		if(DEBUG_CORE)
			printf("str r%u,[r%u,#0x%X]\n",rb_ind,ra_ind,rc);
		sprintf(core_current.Execute_instr_disp, "Execute: str r%u,[r%u,#0x%X]", rb_ind, ra_ind, rc);
		//Functional
		rc<<=2;
		rc=ra+rc;
		core_current.Memory_data=rb;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Write_valid=true;
		core_current.Write_type=0;
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rb;
		core_current.Execute_destination_regindex=0xff; //do not update this
        return false;
    }
	#pragma endregion
    //STR(2)
	//Instr 43
	#pragma region
    if((inst&0xFE00)==0x5000)
    {
		if(core_current.Execute_multicycle_regindex==9)//First cycle
		{
			//According to paper
			ra=core_current.D2E_reg1;
			rb=core_current.D2E_reg2;
			ra_ind=core_current.Decode_port_regindex[1];
			rb_ind=core_current.Decode_port_regindex[2];
			rd_ind=core_current.Decode_port_regindex[0];
			if(DEBUG_CORE)
				printf("Execute C1:str r%u,[r%u,r%u]\n",rd_ind,ra_ind,rb_ind);
			sprintf(core_current.Execute_instr_disp, "Execute C1: str r%u,[r%u,r%u]", rd_ind, ra_ind, rb_ind);
			core_current.Execute_multicycle_regindex=0;
			//Functional
			rc=ra+rb;
			//core_current.Memory_data=rb;//sent to memory
			core_current.Memory_addr=rc;
			core_current.Write_valid=false;
			core_current.Write_type=0;
			//Update ALU output
			core_current.Execute_ALU_result=rc;
			core_current.D2E_reg1_data=read_register_forward(rd_ind);
			core_current.D2E_reg1_valid=true;
			core_current.D2E_reg2_valid=false;
			core_current.Execute_destination_regindex=0xff;
			core_current.cpsr_valid=false;
			return true;
		}
		else//Second cycle
		{
			//According to paper
			ra=core_current.D2E_reg1;
			ra_ind=core_current.Decode_port_regindex[0];
			rb_ind=core_current.Decode_port_regindex[2];
			rd_ind=core_current.Decode_port_regindex[1];
			if(DEBUG_CORE)
				printf("Execute C2:str r%u,[r%u,r%u]\n",ra_ind,rd_ind,rb_ind);
			sprintf(core_current.Execute_instr_disp, "Execute C2: str r%u,[r%u,r%u]", ra_ind, rd_ind, rb_ind);
			rd_ind=0xff;//not used
			core_current.Execute_multicycle_regindex=9;
			core_current.Memory_data=ra;//sent to memory
			core_current.Write_valid=true;
			core_current.Write_type=0;
			//Update ALU output
			core_current.Execute_ALU_result=ra;
			core_current.Execute_destination_regindex=0xff; //do not update this
			core_current.cpsr_valid=false;
			return false;
		}
    }
	#pragma endregion
    //STR(3)
	//Store SP with offset, as STRI
	#pragma region
    if((inst&0xF800)==0x9000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		rc=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[1];
		rb_ind=core_current.Decode_port_regindex[0];
		if(DEBUG_CORE)
			printf("str r%u,[SP,#0x%X]\n",rb_ind,rc);
		sprintf(core_current.Execute_instr_disp, "Execute: str r%u,[SP,#0x%X]", rb_ind, rc);
		//Functional
		rc<<=2;
		rc=ra+rc;
		core_current.Memory_data=rb;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Write_valid=true;
		core_current.Write_type=0;
		
		//Update ALU output
		core_current.Execute_ALU_result=rb;
		core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
        return false;
    }
	#pragma endregion
    //STRB(1)
	//Instr 42 STRBI
	#pragma region
    if((inst&0xF800)==0x7000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		rc=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[1];
		rb_ind=core_current.Decode_port_regindex[0];
		if(DEBUG_CORE)
			printf("strb r%u,[r%u,#0x%X]\n",rb_ind,ra_ind,rc);
		sprintf(core_current.Execute_instr_disp, "Execute: strb r%u,[r%u,#0x%X]", rb_ind, ra_ind, rc);
		//Functional
		rc=ra+rc;
		core_current.Memory_data=rb;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Write_valid=true;
		core_current.Write_type=1;//byte
		
		//Update ALU output
		core_current.Execute_ALU_result=rb;
		core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
        return false;
    }
	#pragma endregion
    //STRB(2)
	//Instr 45 STRB
	#pragma region
    if((inst&0xFE00)==0x5400)
    {
 		if(core_current.Execute_multicycle_regindex==9)//First cycle
		{
			//According to paper
			ra=core_current.D2E_reg1;
			rb=core_current.D2E_reg2;
			ra_ind=core_current.Decode_port_regindex[1];
			rb_ind=core_current.Decode_port_regindex[2];
			rd_ind=core_current.Decode_port_regindex[0];
			if(DEBUG_CORE)
				printf("C1:strb r%u,[r%u,r%u]\n",rd_ind,ra_ind,rb_ind);
			sprintf(core_current.Execute_instr_disp, "Execute C1:strb r%u,[r%u,r%u]", rd_ind, ra_ind, rb_ind);

			core_current.Execute_multicycle_regindex=0;
			//Functional
			rc=ra+rb;
			//core_current.Memory_data=rb;//sent to memory
			core_current.Memory_addr=rc;
			core_current.Write_valid=false;
			core_current.Write_type=1;//byte
			//Update ALU output
			core_current.Execute_ALU_result=rc;
			core_current.D2E_reg1_data=read_register_forward(rd_ind);
			core_current.D2E_reg1_valid=true;
			core_current.D2E_reg2_valid=false;
			core_current.Execute_destination_regindex=0xff;
			core_current.cpsr_valid=false;
			return true;
		}
		else//Second cycle
		{
			//According to paper
			ra=core_current.D2E_reg1;
			ra_ind=core_current.Decode_port_regindex[0];
			rb_ind=core_current.Decode_port_regindex[2];
			rd_ind=core_current.Decode_port_regindex[1];
			if(DEBUG_CORE)
				printf("C2:strb r%u,[r%u,r%u]\n",ra_ind,rd_ind,rb_ind);
			sprintf(core_current.Execute_instr_disp, "Execute C2:strb r%u,[r%u,r%u]", ra_ind, rd_ind, rb_ind);
			rd_ind=0xff;//not used
			core_current.Execute_multicycle_regindex=9;
			core_current.Memory_data=ra;//sent to memory
			core_current.Write_valid=true;
			core_current.Write_type=1;//byte
			//Update ALU output
			core_current.Execute_ALU_result=ra;
			core_current.Execute_destination_regindex=0xff; //do not update this
			core_current.cpsr_valid=false;
			return false;
		}
    }
	#pragma endregion
    //STRH(1)
	//Instr 41 STRHI
	#pragma region
    if((inst&0xF800)==0x8000)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		rc=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[1];
		rb_ind=core_current.Decode_port_regindex[0];
		if(DEBUG_CORE)
			printf("strh r%u,[r%u,#0x%X]\n",rb_ind,ra_ind,rc);
		sprintf(core_current.Execute_instr_disp, "Execute: strh r%u,[r%u,#0x%X]", rb_ind, ra_ind, rc);

		//Functional
		rc<<=1;
		rc=ra+rc;
		core_current.Memory_data=rb;//sent to memory
		core_current.Memory_addr=rc;
		core_current.Write_valid=true;
		core_current.Write_type=2;//half word
		
		//Update ALU output
		core_current.Execute_ALU_result=rb;
		core_current.Execute_destination_regindex=0xff; //do not update this
		core_current.cpsr_valid=false;
    }
	#pragma endregion
    //STRH(2)
	//Instr 44 STRH
	#pragma region
    if((inst&0xFE00)==0x5200)
    {
		 if(core_current.Execute_multicycle_regindex==9)//First cycle
		{
			//According to paper
			ra=core_current.D2E_reg1;
			rb=core_current.D2E_reg2;
			ra_ind=core_current.Decode_port_regindex[1];
			rb_ind=core_current.Decode_port_regindex[2];
			rd_ind=core_current.Decode_port_regindex[0];
			if(DEBUG_CORE)
				printf("C1:strh r%u,[r%u,r%u]\n",rd_ind,ra_ind,rb_ind);
			sprintf(core_current.Execute_instr_disp, "Execute C1:strh r%u,[r%u,r%u]", rd_ind, ra_ind, rb_ind);
			core_current.Execute_multicycle_regindex=0;
			//Functional
			rc=ra+rb;
			//core_current.Memory_data=rb;//sent to memory
			core_current.Memory_addr=rc;
			core_current.Write_valid=false;
			core_current.Write_type=2;//half word
			//Update ALU output
			core_current.Execute_ALU_result=rc;
			core_current.Execute_destination_regindex=0xff;
			core_current.D2E_reg1_data=read_register_forward(rd_ind);
			core_current.D2E_reg1_valid=true;
			core_current.cpsr_valid=false;
			core_current.D2E_reg2_valid=false;
			core_current.cpsr_valid=false;
			return true;
		}
		else//Second cycle
		{
			//According to paper
			ra=core_current.D2E_reg1;
			ra_ind=core_current.Decode_port_regindex[0];
			rb_ind=core_current.Decode_port_regindex[2];
			rd_ind=core_current.Decode_port_regindex[1];
			if(DEBUG_CORE)
				printf("C2:strh r%u,[r%u,r%u]\n",ra_ind,rd_ind,rb_ind);
			sprintf(core_current.Execute_instr_disp, "Execute C2:strh r%u,[r%u,r%u]", ra_ind, rd_ind, rb_ind);

			rd_ind=0xff;//not used
			core_current.Execute_multicycle_regindex=9;
			core_current.Memory_data=ra;//sent to memory
			core_current.Write_valid=true;
			core_current.Write_type=2;//half word
			//Update ALU output
			core_current.Execute_ALU_result=ra;
			core_current.Execute_destination_regindex=0xff; //do not update this
			return false;
		}
    }
	#pragma endregion
    //SUB(1)
	//Instr 10 Sub 2reg+imm
	#pragma region
    if((inst&0xFE00)==0x1E00)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("subs r%u,r%u,#0x%X\n",rd_ind,ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute:subs r%u,r%u,#0x%X", rd_ind, ra_ind, rb);

        //Logical calculation 
        rc=ra-rb;
		
		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,~rb,1);
        do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
		//Update destination register
		write_register(rd_ind,core_current.Execute_ALU_result);
		core_current.Execute_destination_regindex=0xff; //do not update this
        return false;
    }
	#pragma endregion
    //SUB(2)
	//Instr 11: Sub 1reg+Imm
	#pragma region
    if((inst&0xF800)==0x3800)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		ra_ind=core_current.Decode_port_regindex[0];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("subs r%u,#0x%02X\n",ra_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute:subs r%u,#0x%02X", ra_ind, rb);
        //Logical calculation 
        rc=ra-rb;
		
		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,~rb,1);
        do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;

		return false;

    }
	#pragma endregion
    //SUB(3)
	//Instr 9: sub 3regs
	#pragma region
    if((inst&0xFE00)==0x1A00)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[2];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("subs r%u,r%u,r%u\n",rd_ind,ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: subs r%u,r%u,r%u", rd_ind, ra_ind, rb_ind);
		//Functional
         rc=ra-rb;

		//Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        do_cflag(ra,~rb,1);
        do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //SUB(4)
	//Sub SP=Sp-imm
	#pragma region
    if((inst&0xFF80)==0xB080)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.Execute_Imm;
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("sub r%u,SP,#0x%02X\n",rd_ind,rb);
		sprintf(core_current.Execute_instr_disp, "Execute: sub r%u,SP,#0x%02X", rd_ind, rb);
		//Functional
        rc=ra-rb;

		//Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
        //do_cflag(ra,rb,0);
        //do_vflag(ra,rb,0);
		core_current.cpsr_valid=false;		
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
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
            return(0);
        }
        else
        {
            printf("\n\nswi 0x%02X\n",rb);
            return(1);
        }
    }
	#pragma endregion
    //SXTB
	//Instr 52
	#pragma region
    if((inst&0xFFC0)==0xB240)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("sxtb r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: sxtb r%u,r%u\n", rd_ind, rb_ind);
		//Functional
		rc=rb&0xFF;
        if(rc&0x80) {
            unsigned int tmp = ~0;
            tmp <<= 8;
            rc|=tmp;
        }
        //Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //SXTH
	//Instr 51
	#pragma region
    if((inst&0xFFC0)==0xB200)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("sxth r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: sxth r%u,r%u", rd_ind, rb_ind);
		//Functional
		rc=rb&0xFFFF;
        if(rc&0x8000) {
            unsigned int tmp = ~0;
            tmp <<= 16;
            rc|=tmp;
        }
        //Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion

    //TST
	//Instr 23
	#pragma region
    if((inst&0xFFC0)==0x4200)
    {
		//According to paper
		ra=core_current.D2E_reg1;
		rb=core_current.D2E_reg2;
		ra_ind=core_current.Decode_port_regindex[0];
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=-1;
		if(DEBUG_CORE)
			printf("tst r%u,r%u\n",ra_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: tst r%u,r%u", ra_ind, rb_ind);
		//Functional
		rc=ra&rb;

        //Update CPSR
		do_nflag(rc);
        do_zflag(rc);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=true;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
		core_current.Execute_destination_regindex=0xff; //do not update this
        return false;
    }
	#pragma endregion
    //UXTB
	//Instr 54
	#pragma region
    if((inst&0xFFC0)==0xB2C0)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("uxtb r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: uxtb r%u,r%u", rd_ind, rb_ind);
		//Functional
		rc=rb&0xFF;
        //Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    //UXTH
	//Instr 53
	#pragma region
    if((inst&0xFFC0)==0xB280)
    {
		//According to paper
		rb=core_current.D2E_reg2;
		rb_ind=core_current.Decode_port_regindex[1];
		rd_ind=core_current.Execute_destination_regindex;
		if(DEBUG_CORE)
			printf("uxth r%u,r%u\n",rd_ind,rb_ind);
		sprintf(core_current.Execute_instr_disp, "Execute: uxth r%u,r%u\n", rd_ind, rb_ind);
		//Functional
		rc=rb&0xFFFF;
        //Update CPSR
		//do_nflag(rc);
        //do_zflag(rc);
		//do_cflag_bit(0);
        //do_vflag_bit(0);
        //do_cflag(ra,~rb,1);
        //do_vflag(ra,~rb,1);
		core_current.cpsr_valid=false;
		//Update ALU output
		core_current.Execute_ALU_result=rc;
        return false;
    }
	#pragma endregion
    printf("invalid instruction 0x%04X\n",inst);
    return false;
}