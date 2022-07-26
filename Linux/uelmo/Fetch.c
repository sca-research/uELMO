#include "Configure.h"
#include "core.h"
#include "Memory.h"
#include "Fetch.h"
void Fetch_OneCycle()
{
    unsigned int pc;
    pc = read_register2(15);
    if (core_current.Fetch_valid == true)
        {
            core_current.Fetch_instruction_new = fetch16(pc - 2);
            pc += 2;
            write_register_value(15, pc);
        }
}
