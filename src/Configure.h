#ifndef CONFIG_H_
#define CONFIG_H_
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//#define bool int
#include <stdbool.h>

#define true 1
#define false 0
#define DEBUG_MEM 0
#define DEBUG_CORE 0
extern bool fvr;
extern int N;
extern int N_ind;
extern bool ioSupported;
extern bool useInputFile;
extern bool useSealTrace;
extern bool useScript;
#endif
