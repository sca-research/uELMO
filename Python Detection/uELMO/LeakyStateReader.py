#!/usr/bin/env python3
import sys
import numpy as np
class LeakyStateReader:
    tracenum=0
    Samples=None
    fp=None
    filename=None
    def __init__(self,inputfile):
        self.filename= inputfile
        self.Samples=list()
        self.fp= open(inputfile, "rb")
    class Term:
        def __init__(self, type, disp):
            self.type=type
            self.disp=disp
            self.data=list()
    class Sample:
        def __init__(self,no,inst):
            self.Terms=list()
            self.inst=inst
            self.no=no
        def add(self,Term):
            self.Terms.append(Term)
    # Read in all instruction infor
    def ReadInstrHeader(self):
        count=0
        while(1):
            # Sample start
            len=int.from_bytes(self.fp.read(1),byteorder='big')
            if(len==0):# End of trace
                break
            count=count+1
            inst=self.fp.read(len).decode()
            print("inst={0}".format(inst))
            print("Sample={0}".format(count))
            sample=self.Sample(count,inst)
            tcount=1
            # Within this sample
            while(1):
                type = int.from_bytes(self.fp.read(1),byteorder='big')
                if(type==0xff):#end of sample
                    break
                if(type==0x0):
                    print("Type=Full\t")
                else:
                    print("Type=Linear\t")
                print("Term {0}".format(tcount))
                len = int.from_bytes(self.fp.read(1),byteorder='big')
                label=self.fp.read(len).decode()
                print("Label={0}".format(label))
                #Add term to this sample
                term=self.Term(type,label)
                sample.add(term)
                tcount=tcount+1
            #End sample
            print("\n\n\n")
            #Add sample to the list
            self.Samples.append(sample)

    # Print out header to a text file
    def PrintInstrHeader(self, filename):
        f=open(filename, "w")
        for sample in self.Samples:
            f.writelines("Sample {0}:\t {1} \n".format(sample.no,sample.inst))
            tcount=1
            for term in sample.Terms:
                f.writelines("\t Term {0}: \n".format(tcount))
                if(term.type==0):
                    f.writelines("\t\t{0},\tType=Full\n".format(term.disp))
                else:
                    f.writelines("\t\t{0},\tType=Linear\n".format(term.disp))
                tcount=tcount+1
            f.writelines("\n\n")
        f.close()

    # Read in all instruction data
    def ReadInstrData_OneTrace(self,start=0,limit=None):
        count=0
        if(limit == None):
            limit=len(self.Samples)
        try:
            while(1):
                # Sample start
                #print("Sample={0}".format(count+1))
                tcount=0
                # Within this sample
                while(1):
                    t=self.fp.read(1)
                    if(t==b''):#EOF
                        return 0
                    type = int.from_bytes(t,byteorder='big')
                    if(type==0xff):#end of sample
                        break
                    if(type==0xfe):#end of trace
                        self.tracenum=self.tracenum+1
                        return 1
                    #if(type==0x0):
                    #    print("Type=Full\t")
                    #else:
                    #    print("Type=Linear\t")
                    leng = int.from_bytes(self.fp.read(1),byteorder='big')
                    data=list(self.fp.read(leng))
                    #print("Term {0}={1}\n".format(tcount + 1, data.hex()))
                    #Add data to this term
                    sample=self.Samples[count]
                    term=sample.Terms[tcount]
                    if(term.type!=type):
                        print("Inconsistent types!\n")
                    if(count<limit and count>=start):
                        term.data.append(data)
                    tcount=tcount+1
                #End sample
                #print("\n\n\n")
                count=count+1
        except IOError:
            print("Error: flawed file format!\n")
    def ReadAllTraces(self):
        self.tracenum = 0
        while (1):
            if (self.ReadInstrData_OneTrace() == 0):
                break
            if (self.tracenum % 10000 == 0):
                print("Trace {0}".format(self.tracenum))
        print("Read {0} traces\n".format(self.tracenum))
    def ReadTraces(self,N,start=0,limit=None):
        self.tracenum = 0
        while (1):
            if (self.ReadInstrData_OneTrace(start,limit) == 0):
                break
            if(self.tracenum>=N):
                break
            if (self.tracenum % 100 == 0):
                print("Trace {0}".format(self.tracenum))
        print("Read {0} traces\n".format(self.tracenum))
    def __del__(self):
       self.fp.close()
       self.Samples.clear()

if __name__ == '__main__':
        n=10
        test=LeakyStateReader("C:\\Users\\gs\\Documents\\GitHub\\uELMO\\Windows\\uELMO\\Examples\\ISWd2\\ISWd2_LeakyState.bin")
        test.ReadInstrHeader()
        test.PrintInstrHeader("uELMO_ISWd2.txt")
        test.ReadTraces(10)
