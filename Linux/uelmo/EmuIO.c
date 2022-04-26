//This file describe the inpuut-output functions for the emulator
//i.e. need to be rewritten for SMURF
#include "Configure.h"
#include "core.h"
#include "EmuIO.h"
#include "uelmo.h"

//global output file pointer
FILE *outfp = NULL;
//global input file pointer
FILE *datafp = NULL;

//Close output stream, executiong trace file
void Close_Output()		//SMURF_ADAPTING, change this
{
    if (outfp != NULL)
	fclose(outfp);
};

//Close input data stream, emulated input
void Close_DataFile()		//SMURF_ADAPTING, change this
{
    if (outfp != NULL)
	fclose(datafp);
}

//open output file, executiong trace file
void Open_OutputFile(char *filename)	//SMURF_ADAPTING, change this
{
    outfp = fopen(filename, "wb+");
    if (outfp == NULL)
	{
	    printf("Error opening file [%s]\n", filename);
	    return;
	}
}

//open input data file, emulated input
void Open_DataFile(char *filename)	//SMURF_ADAPTING, change this
{
    datafp = fopen(filename, "r");
    if (NULL == datafp)
	{
	    printf("Error opening file [%s]\n", filename);
	    return;
	}
}

//Get input from IO , emulated input
//SMURF_ADAPTING, change this
#ifndef USE_SMURF
unsigned int Read_Byte()
{
    char *str;
    unsigned int data = UELMO_ERROR;
    size_t len = 20;
    str = (char *)malloc(len);
    //getline(&str, &len, datafile);//TEMP: get it back after moving back to Linux
    if (NULL == fgets(str, len, datafp))
	data = (int)strtol(str, NULL, 16);

    //printf("%x\n", data);
    free(str);
    return data;
}

void Write_Byte(uint8_t input)
{
    printf("#uELMO outpus: %02X (%c)\n", input, input);
    return;
}
#else
unsigned int ReadFromFile()
{
    char *str;
    unsigned int data = UELMO_ERROR;
    size_t len = 20;
    str = (char *)malloc(len);
    //getline(&str, &len, datafile);//TEMP: get it back after moving back to Linux
    if (NULL == fgets(str, len, datafp))
	data = (int)strtol(str, NULL, 16);

    //printf("%x\n", data);
    free(str);
    return data;
}

unsigned int Read_Byte()
{
    unsigned int ret = 0;

    if (useInputFile)		//Use input file.
	{
	    ret = ReadFromFile();
	}
    else if (ioSupported)	//Use Smurf IO.
	{
	    if (NULL == sio || SMURF_IO_READY != sio->stat)
		{
		    INFO("#SmurfIO not ready.\n");
		    return 0;
		}
	    ret = SioGetchar(sio);
	}
    else			//Use stdin by default.
	{
	    ret = getchar();
	}
    return ret;
}

void Write_Byte(uint8_t input)
{
    if (NULL == sio)
	{
	    //INFO("SIO not initialised.\n");
	    putchar(input);
	    return;
	}

    if (SMURF_IO_READY == sio->stat)
	{
	    SioPutchar(sio, input);
	}
    printf("#Trying to write but SmurfIO not ready: %x\n", input);
    return;
}
#endif

//Get randomised input from IO (SMURF should not have this!!!)
//SMURF_ADAPTING, delete this!
unsigned int Rand_Byte()
{
    return rand() & 0xff;
}

#ifdef USE_SMURF
void SmurfUpdateFrame()
{
    if (NULL == smfframe)
	{
	    return;
	}
    //Assign core_current to the Smurf Frame buffer.
#define Assign(x) StfAssign(&smftidx.x, &core_current.x)
    {
	StfAssign(&smftidx.traceno, &N_ind);
	Assign(core_valid);
	Assign(reg);
	Assign(cpsr);
	Assign(F2D_instrreg);
	Assign(D2E_reg1);
	Assign(D2E_reg2);
	Assign(D2E_instrreg);
	Assign(cpsr_valid);
	Assign(cpsr_data);
	Assign(D2E_reg1_valid);
	Assign(D2E_reg2_valid);
	Assign(D2E_reg1_data);
	Assign(D2E_reg2_data);
	Assign(Fetch_instruction_new);
	Assign(Fetch_valid);
	Assign(Decode_port_regindex);
	Assign(Decode_port_data);
	Assign(Decode_destination_regindex);
	Assign(Decode_valid);
	Assign(glitchy_Decode_port_regindex);
	Assign(glitchy_Decode_port_data);
	Assign(Execute_Imm);
	Assign(Execute_ALU_result);
	Assign(Execute_destination_regindex);
	Assign(Execute_multicycle_regindex);
	Assign(Execute_valid);
	Assign(Read_valid);
	Assign(Read_type);
	Assign(Write_valid);
	Assign(Write_type);
	Assign(SignExtend_byte_valid);
	Assign(SignExtend_halfbyte_valid);
	Assign(Memory_read_targetreg);
	Assign(Memory_addr);
	Assign(Memory_data);
	Assign(Write_valid_delayed);
	Assign(Memory_writebuf_delayed);
	Assign(Memory_writebuf);
	Assign(Memory_readbuf);
	Assign(Read_reg_update);
	Assign(Memory_read_targetreg_buf);
	StfAssign(&smftidx.Memory_instr_disp, core_current.Memory_instr_disp);
	StfAssign(&smftidx.Decode_instr_disp, core_current.Decode_instr_disp);
	StfAssign(&smftidx.Execute_instr_disp, core_current.Execute_instr_disp);
    }
#undef Assign

    return;
}

void SmurfAddFrame()
{
    if (NULL == smftrace)
	{
	    return;
	}

    StAddFrame(smftrace, smfframe);
    return;
}
#endif

//Write out current cycle to Frame
//SMURF_ADAPTING, rewrite this
//Frame data in CORE_STATUS core_current
void Write_Frame()
{
    if (OnTrace == true)
	fwrite(&core_current, sizeof(CORE_STATUS), 1, outfp);
#ifdef USE_SMURF
    SmurfUpdateFrame();
    SmurfAddFrame();
#endif
}

//Write out a flag that terminate the current trace
//SMURF_ADAPTING, rewrite this
void Write_EndofTrace()
{
    bool flag = false;
    fwrite(&flag, sizeof(bool), 1, outfp);
    return;
}
