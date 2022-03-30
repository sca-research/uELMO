#!/usr/bin/python3

import smurf

core = smurf.Core()

# Added for Smurf.
core.NewComponent('TraceNo', 'UINT32')

# Registers:
# Architectural registers: R0 to R15
# A flag for reaching the end of this execution.
core.NewComponent('core_valid', 'BOOL')  # Bool.
core.NewComponent('reg', 'UINT32', 16)  # Architectural.
core.NewComponent('cpsr', 'UINT32')  # Architectural.

# Micro-arhictectural registers
# Pipeline register (uint16_t), barrier between Fetch and Decode (i.e. D.1).
core.NewComponent('F2D_instrreg', 'UINT16')
# Pipeline register, barrier between Decode and Execute (i.e. E.1).
core.NewComponent('D2E_reg1', 'UINT32')
# Pipeline register, barrier between Decode and Execute (i.e. E.2).
core.NewComponent('D2E_reg2', 'UINT32')
# Pesudo register (uint16_t): in theory should be already tranferred to control signal, here we store the instruction instead.
core.NewComponent('D2E_instrreg', 'UINT16')

# Bus/MUX
core.NewComponent('cpsr_valid', 'BOOL')  # Update cpsr (bool).
core.NewComponent('cpsr_data', 'UINT32')  # New data for cpsr.
# Update pipeline register 1 (bool).
core.NewComponent('D2E_reg1_valid', 'BOOL')
# Update pipeline register 2 (bool).
core.NewComponent('D2E_reg2_valid', 'BOOL')
# Input data for pipeline register 1, barrier between Decode and Execute (i.e. D.9).
core.NewComponent('D2E_reg1_data', 'UINT32')
# Input data for pipeline register 2, barrier between Decode and Execute (i.e. D.10).
core.NewComponent('D2E_reg2_data', 'UINT32')

# Fetch
# Fetched new instruction (uint16_t) (i.e. F.3).
core.NewComponent('Fetch_instruction_new', 'UINT16')
# A flag that stall the pipeline when jump happens (bool).
core.NewComponent('Fetch_valid', 'BOOL')

# Decode
# Current Decoding Read ports index (0-15, often 0-7) (i.e. D.2-D.4).
core.NewComponent('Decode_port_regindex', 'OCTET', 3)
# Current Decoding Read ports data (i.e. D.5-D.7).
core.NewComponent('Decode_port_data', 'UINT32', 3)
# Destination register index.
core.NewComponent('Decode_destination_regindex', 'OCTET')
# A flag that stall the pipeline when jump happens (bool).
core.NewComponent('Decode_valid', 'BOOL')
# Decode the current instruction according to the previous instruction decoding style.
core.NewComponent('glitchy_Decode_port_regindex', 'UINT32', 3)
# Decode the current instruction according to the previous instruction decoding style.
core.NewComponent('glitchy_Decode_port_data', 'UINT32', 3)

# Execute
# Current Execute Immediate data
core.NewComponent('Execute_Imm', 'UINT32')
# Current ALU output
core.NewComponent('Execute_ALU_result', 'UINT32')
# Execute register index: 0-15 valid, 0xff: no output
core.NewComponent('Execute_destination_regindex', 'OCTET')
# Current register index for multi-cycle execution: 0-7 valid
core.NewComponent('Execute_multicycle_regindex', 'OCTET')
# A flag that stall the pipeline when jump happens
core.NewComponent('Execute_valid', 'BOOL')

# Meomory subsystem
# Set it true when a new read address is sent to address bus
core.NewComponent('Read_valid', 'BOOL')
# 0 word, 1 byte, 2 half-word
core.NewComponent('Read_type', 'OCTET')
# Set it true when a new read address is sent to address bus
core.NewComponent('Write_valid', 'BOOL')
# 0 word, 1 byte, 2 half-word
core.NewComponent('Write_type', 'OCTET')
# Sign extend
core.NewComponent('SignExtend_byte_valid', 'BOOL')
# Sign extend
core.NewComponent('SignExtend_halfbyte_valid', 'BOOL')
# For read instruction, the targt regsiter
core.NewComponent('Memory_read_targetreg', 'OCTET')
# Address bus of the memory: must align to 4
core.NewComponent('Memory_addr', 'UINT32')
# Shared (Read and write) data bus: must be 32-bit
core.NewComponent('Memory_data', 'UINT32')
# Write_valid_delayed;	//set it true when the previous Write_valid is true
core.NewComponent('Write_valid_delayed', 'BOOL')
# Write buffer on the write bus.
core.NewComponent('Memory_writebuf_delayed', 'UINT32')
# Write buffer on the write bus.
core.NewComponent('Memory_writebuf', 'UINT32')
# Read buffer on the read bus.
core.NewComponent('Memory_readbuf', 'UINT32')
# If true, update the register according to Memory_read_targetreg and Memory_readbuf
core.NewComponent('Read_reg_update', 'BOOL')
# For read instruction, the targt regsiter
core.NewComponent('Memory_read_targetreg_buf', 'OCTET')

# Discriptions
#  char Memory_instr_disp[50];	//Discription for the memory instruction
core.NewComponent('Memory_instr_disp', 'STRING', 50)
#  char Decode_instr_disp[50];	//Discription for the decode instruction
core.NewComponent('Decode_instr_disp', 'STRING', 50)
#  char Execute_instr_disp[50];	//Discription for the execute instruction
core.NewComponent('Execute_instr_disp', 'STRING', 50)

core.Save("uelmo.json")
