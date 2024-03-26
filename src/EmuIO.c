//This file describe the inpuut-output functions for the emulator
//i.e. need to be rewritten for SEAL
#include "Configure.h"
#include "core.h"
#include "EmuIO.h"
#include "uelmo.h"

//Get input from IO , emulated input
unsigned int Read_Byte()
{
    unsigned int ret = 0;

    if(ioSupported)             //Use Seal IO.
    {
        if(NULL == sio || SEAL_IO_READY != sio->stat)
        {
            INFO("#SealIO not ready.\n");
            return 0;
        }
        ret = SioGetchar(sio);
    }
    else                        //Use stdin by default.
    {
        ret = getchar();
    }
    return ret;
}

void Write_Byte(uint8_t input)
{
    if(NULL == sio)
    {
        //INFO("SIO not initialised.\n");
        putchar(input);
        return;
    }

    if(SEAL_IO_READY == sio->stat)
    {
        SioPutchar(sio, input);
    }
    printf("#Trying to write but SealIO not ready: %x\n", input);
    return;
}

//Get randomised input from IO (SEAL should not have this!!!)
//SEAL_ADAPTING, delete this!
unsigned int Rand_Byte()
{
    return rand() & 0xff;
}

//Write out current cycle to Frame
//SEAL_ADAPTING, rewrite this
//Frame data in CORE_STATUS core_current
void Write_Frame()
{
    if(OnTrace == true)
    {
#ifdef USE_SEAL
        if(useSealTrace)
        {
            SealSync(seal);
            SealWrite(seal);
        }
#endif
        frameno++;
    }
    return;
}
