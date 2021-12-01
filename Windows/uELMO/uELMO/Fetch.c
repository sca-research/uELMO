#include "Configure.h"
#include "core.h"
#include "Memory.h"
#include "Fetch.h"
void Fetch_OneCycle()
{
	unsigned int pc;
    pc=read_register(15);
	core_current.Fetch_instruction_new=fetch16(pc-2);
    pc+=2;
    write_register(15,pc);
}