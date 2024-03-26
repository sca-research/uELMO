#include "Configure.h"
#include "core.h"
#include "Memory.h"
#include "EmuIO.h"
#include "symuelmo.h"

unsigned short rom[ROMSIZE >> 1];
unsigned short ram[RAMSIZE >> 1];

//Read 16 bits, RAM or ROM
unsigned int fetch16(unsigned int addr)
{
    unsigned int data;
    switch (addr & 0xF0000000)
    {
    case 0x00000000:           //ROM
        addr &= ROMADDMASK;
        addr >>= 1;
        data = rom[addr];
        return (data);
    case 0x10000000:           //ROM
        addr &= ROMADDMASK;
        addr >>= 1;
        data = rom[addr];
        return (data);
    default:                   //RAM
        addr &= RAMADDMASK;
        addr >>= 1;
        data = ram[addr];
        return (data);
    }
}

//Read 32 bits, RAM or ROM
unsigned int fetch32(unsigned int addr)
{
    unsigned int data;
    switch (addr & 0xF0000000)
    {
    case 0x00000000:           //ROM
        if(addr < 0x50)
        {
            data = read32(addr);
            if(addr == 0x00000000)
                return (data);
            if(addr == 0x00000004)
                return (data);
            if(addr == 0x0000003C)
                return (data);
            if(DEBUG_MEM)
                printf("fetch32(0x%08X), abort pc = 0x%04X\n",
                       addr, core_current.reg[15]);
            exit(1);
        }
    case 0x10000000:           //ROM
        if(addr < 0x50)
        {
            data = read32(addr);
            if(addr == 0x00000000)
                return (data);
            if(addr == 0x00000004)
                return (data);
            if(addr == 0x0000003C)
                return (data);
            if(DEBUG_MEM)
                printf("fetch32(0x%08X), abort pc = 0x%04X\n",
                       addr, core_current.reg[15]);
            exit(1);
        }
    default:                   //RAM
        data = read32(addr);
        return (data);
    }
}

//Write 16 bits, RAM
void write16(unsigned int addr, unsigned int data)
{
    // Assume write is to RAM
    if(DEBUG_MEM)
        printf("write16(0x%08X,0x%04X)\n", addr, data);
    addr &= RAMADDMASK;
    addr >>= 1;
    ram[addr] = data & 0xFFFF;

    return;
}

//Write 32 bits, RAM + ELMO defined functions (e.g. starttrigger, printbyte, etc.)
void write32(unsigned int addr, unsigned int data)
{

    if(DEBUG_MEM)
        printf("write32(0x%08X,0x%08X)\n", addr, data);
    switch (addr & 0xF0000000)
    {
    case 0xF0000000:           //halt
        //Close execution traces
        core_current.core_valid = false;
        return;
    case 0xE0000000:           //periph
        switch (addr)
        {
        case 0xE0000000:       //printbyte
            {
                Write_Byte(data & 0xFF);
                break;
            }
        case 0xE0000004:
            {                   // trigger
                if(data & 0x01)
                {
                    //Trigger start
                    OnTrace = true;
                }
                else
                {
                    //Trigger end
                    OnTrace = false;
                }
                break;
            }

        }
        break;
    default:                   // Do two write 16s
        if(DEBUG_MEM)
            printf("write32(0x%08X,0x%08X)\n", addr, data);
        write16(addr + 0, (data >> 0) & 0xFFFF);
        write16(addr + 2, (data >> 16) & 0xFFFF);
        return;
    }
    return;
}

//Read 16 bits, No ELMO functions, only for RAM or ROM
unsigned int read16(unsigned int addr)
{
    unsigned int data;

    //if(DEBUG_MEM) 
    //      printf("read16(0x%08X)",addr);

    switch (addr & 0xF0000000)
    {
    case 0x00000000:           //ROM
        addr &= ROMADDMASK;
        addr >>= 1;
        data = rom[addr];
        //if(DEBUG_MEM) printf("0x%04X\n",data);
        return (data);
    case 0x10000000:           //ROM
        addr &= ROMADDMASK;
        addr >>= 1;
        data = rom[addr];
        //if(DEBUG_MEM) printf("0x%04X\n",data);
        return (data);
    default:                   //RAM

        if(DEBUG_MEM)
            printf("read16(0x%08X)=", addr);
        addr &= RAMADDMASK;
        addr >>= 1;
        data = ram[addr];

        if(DEBUG_MEM)
            printf("0x%04X\n", data);

        return (data);
    }
}

//Read byte; from read16
uint8_t read8(unsigned int addr)
{

    uint8_t result = 0;
    if((addr & 0x01) == 1)
        result = (uint8_t) (read16(addr & 0xFFFFFFFE) >> 8);
    else
        result = (uint8_t) (read16(addr) & 0xff);

    return result;
}

//Read 32 bits, RAM +ROM+ ELMO defined functions (e.g. readbyte, randbyte, etc.)
unsigned int read32(unsigned int addr)
{
    unsigned int data;

    //if(DEBUG_MEM) 
    //      printf("read32(0x%08X)=",addr);

    switch (addr & 0xF0000000)
    {
    case 0xE0000000:
        {
            switch (addr)
            {
            case 0xE1000000:   //readbyte()
                {
                    data = Read_Byte();
                    if(DEBUG_MEM)
                    {
                        printf("read=%02x\n", data & 0xFF);
                    }
                    return (data);
                }
            case 0xE1000004:   //randbyte()
                {
                    data = Rand_Byte();
                    if(DEBUG_MEM)
                        printf("rand=%02x\n", data & 0xFF);
                    return (data);
                }
            }
        }

    default:                   //Do two read16s
        if(DEBUG_MEM)
            printf("read32(0x%08X)=", addr);
        data = read16(addr + 0);
        data |= ((unsigned int)read16(addr + 2)) << 16; //higher address->high bits
        if(DEBUG_MEM)
            printf("0x%08X\n", data);
        return (data);
    }

}

//One cycle of memory sub-system
//Returning false means execute can run 
bool Memory_OneCycle()
{
    unsigned int addr = 0;
    unsigned int value = 0;
    if(core_current.Read_valid) //Performing read
    {
        core_current.Read_valid = false;        //unset
        core_current.Memory_read_targetreg_buf =
            core_current.Memory_read_targetreg;
        addr = core_current.Memory_addr & 0xfffffffc;   //align with 4
        core_current.Memory_data = read32(addr);        //read a 32-bit word
#if USE_SEAL
        if(IsSymNull(sym_memrd_pending))
        {
            SymClear(sym_core_current.Memory_data);
        }
        else
        {
            SymAssign(sym_core_current.Memory_data, sym_memrd_pending);
            sym_memrd_pending = SYM_NULL;
        }
#endif
        value = core_current.Memory_data;
        switch (core_current.Read_type)
        {
        case 0:                //word
            //write_register(core_current.Memory_read_targetreg,value);//store result in destination register
            break;
        case 1:                //byte
            value = (value >> (8 * (core_current.Memory_addr & 0x3))) & 0xff;
            //write_register(core_current.Memory_read_targetreg,value&0xff);//store result in destination register
            break;
        case 2:                //half word
            value = (value >> (8 * (core_current.Memory_addr & 0x2))) & 0xffff;
            //write_register(core_current.Memory_read_targetreg,value&0xffff);//store result in destination register
            break;
        default:
            printf("Read Error!\n");
        }
        core_current.Memory_readbuf = value;
#if USE_SEAL
        SymCopy(sym_core_current.Memory_readbuf, sym_core_current.Memory_data);
#endif

        sprintf(core_current.Memory_instr_disp,
                "Memory: load [0x%X]=0x%X", core_current.Memory_addr, value);
        core_current.Read_reg_update = true;
        if(core_current.Memory_read_targetreg == 15)
        {
            //jump
            //Set the following two instruction to invalid
            core_current.Decode_destination_regindex = 0xff;
            core_current.Execute_destination_regindex = 0xff;
            core_current.Decode_valid = false;
            core_current.Execute_valid = false;
            return true;
        }
        else
            return false;
    }
    if(core_current.Write_valid_delayed == true)
    {
        core_current.Memory_writebuf_delayed = core_current.Memory_writebuf;
#if USE_SEAL
        SymCopy(sym_core_current.Memory_writebuf_delayed,
                sym_core_current.Memory_writebuf);
#endif

        core_current.Write_valid_delayed = false;
    }

    if(core_current.Write_valid)        //Performing write
    {
        core_current.Write_valid = false;       //unset
        core_current.Write_valid_delayed = true;
        core_current.Memory_writebuf = core_current.Memory_data;
#if USE_SEAL
        SymCopy(sym_core_current.Memory_writebuf, sym_core_current.Memory_data);
#endif

        switch (core_current.Write_type)
        {
        case 0:                //word
            addr = core_current.Memory_addr & 0xfffffffc;       //align with 4
            write32(addr, core_current.Memory_data);
            break;
        case 1:                //byte
            {
                switch (core_current.Memory_addr & 0x1)
                {
                case 0:
                    value = read16(core_current.Memory_addr & 0xfffffffe);
                    value = value & 0xff00;
                    value = value | (core_current.Memory_data & 0xff);
                    write16(core_current.Memory_addr & 0xfffffffe, value);
                    break;
                case 1:
                    value = read16(core_current.Memory_addr & 0xfffffffe);
                    value = value & 0xff;
                    value = value | ((core_current.Memory_data & 0xff) << 8);
                    write16(core_current.Memory_addr & 0xfffffffe, value);
                    break;
                }
            }
            break;
        case 2:                //half word
            addr = core_current.Memory_addr & 0xfffffffe;       //align with 2
            write16(addr, core_current.Memory_data & 0xffff);
            break;
        default:
            printf("Write Error!\n");
        }
        sprintf(core_current.Memory_instr_disp,
                "Memory: store [0x%X]=0x%X", core_current.Memory_addr,
                core_current.Memory_data);

        return false;
    }
    sprintf(core_current.Memory_instr_disp, "Memory: idle");
    return false;
}

unsigned int SignExtend_B(unsigned int rc, unsigned int rb)
{
    if(rb & 1)
    {
        rc >>= 8;
    }
    rc &= 0xFF;
    if(rc & 0x80)
    {
        unsigned int tmp = ~0;
        tmp <<= 8;
        rc |= tmp;
    }
    return rc;
}

unsigned int SignExtend_HB(unsigned int rc, unsigned int rb)
{
    rc &= 0xFFFF;
    if(rc & 0x8000)
    {
        unsigned int tmp = ~0;
        tmp <<= 16;
        rc |= tmp;
    }
    return rc;
}
