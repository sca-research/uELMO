#pragma once
#include <stdint.h>
void OpenLeakageFile(char*);
void CloseLeakageFile();
//a string that constains the discription of the leakage node
void Write_string(char* str);
void Write_leakage_label(char*, uint8_t);
void Write_headender();
void Write_frameender();
void Write_traceender();
void Write_leakage_data(uint8_t*, uint8_t, uint8_t);
void Write_Instr(char* disp);