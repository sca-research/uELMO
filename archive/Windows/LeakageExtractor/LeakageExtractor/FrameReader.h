#pragma once
//open output file
void Open_Exefile(char*);
//Close output stream
void Close_Exefile();
//Read in one Frame/cycle
//Require space allocation before calling
void Read_Frame(CORE_STATUS*);
//check if reach the end of execution file, i.e. all traces have been read already
bool IsEof();

//point back to begining, for print out header
void Rewind();