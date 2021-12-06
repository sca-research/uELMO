#pragma once
#include "../../uELMO/uELMO/core.h"
//options for adjusting the leakage model
#define FORCE_LINEAR 0 //force all leakage to be linear

#define NON_ACTIVE_REG 0 //Allows leakage for non-active registers
#define NON_ACTIVE_MEM 1 //Allows leakage for non-active memory buses

#define MICROARCHITECTURAL 1//Allows leakage from the micro-architecture
#define CPSR 1//Allows leakage from the CPSR register
#define DECODE_PORT 1//Allows leakage from the decoding register access
#define GLITCHY_DECODE 1//Allows for glitchy decoding register access

#define TRANSITION 1//Allows for transition leakage
#define LSB_NEIGHBOUR 1//Allows for LSB based neibouring effect
//print out the instruction discription for current cycle
void Generate_Leakage_Instr(CORE_STATUS*, bool);
void Generate_Leakage_Select(CORE_STATUS*,bool);
void Generate_Leakage_Transition(CORE_STATUS*, CORE_STATUS*, bool);