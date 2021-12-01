import numpy as np
#from Crypto.Cipher import AES
# Read the measured traces from the TRS file
# Riscure TRS trace set file wrapper
import struct
class TRS_Reader(object):
    Number_of_Traces=0
    index=0#Trace index
    number_of_samples=0
    isint=True
    cryptolen=0
    traces = None
    plaintext= None
    ciphertext= None
    pos=0#Starting position of data section

    def __init__(self,filename):
        self.f = open(filename, 'rb+')
    def __del__(self):
        self.f.close()

    def read_header(self):
        self.index = 0
        # Read Header Info
        # Tag   Len Discription
        # 0x41  4   Number of traces
        while(True):
            tag = self.f.read(1)
            if tag==b'\x41':
                len=int.from_bytes(self.f.read(1), byteorder='little')
                self.Number_of_Traces=int.from_bytes(self.f.read(len), byteorder='little')
                continue
            if tag==b'\x42':
                len=int.from_bytes(self.f.read(1), byteorder='little')
                self.number_of_samples=int.from_bytes(self.f.read(len), byteorder='little')
                continue
            if tag==b'\x43':
                len=int.from_bytes(self.f.read(1), byteorder='little')
                if self.f.read(len)==b'\x02':
                    self.isint=True
                else:
                    self.isint=False
                continue
            if tag == b'\x44':
                len = int.from_bytes(self.f.read(1), byteorder='little')
                self.cryptolen=int.from_bytes(self.f.read(len), byteorder='little')
                continue
            if tag == b'\x5F':
                len = int.from_bytes(self.f.read(1), byteorder='little')
                self.pos = self.f.tell()
                break
            len = int.from_bytes(self.f.read(1), byteorder='little')
            self.f.read(len)

    def read_traces(self,N=0,startp=0,endp=0):
        if(N==0):
            N=self.Number_of_Traces
        if(endp==0):
            endp=self.number_of_samples
        if(self.isint):
            self.traces=np.zeros((N,endp-startp),np.int16)
        else:
            self.traces = np.zeros((N, endp - startp), np.float)
        self.plaintext=np.zeros((N,int(self.cryptolen/2)), np.dtype('B'))
        self.ciphertext=np.zeros((N,int(self.cryptolen/2)),np.dtype('B'))
        while self.index<N:
            if self.index % 10000==0:
                print("Reading traces "+str(self.index))
            p=self.f.read(int(self.cryptolen/2))
            c=self.f.read(int(self.cryptolen/2))
            for i in range(int(self.cryptolen/2)):
                self.plaintext[self.index][i]  = p[i]
                self.ciphertext[self.index][i] = c[i]
            for i in range(self.number_of_samples):
                if(self.isint):
                    if(i<endp and i>=startp):
                        self.traces[self.index][i-startp]=int.from_bytes(self.f.read(2), byteorder='little', signed=True)
                    else:
                        self.f.read(2)
                else:
                    if(i<endp and i>=startp):
                        #self.traces[self.index][i-startp] = float.from_bytes(self.f.read(4))
                        b=self.f.read(4)
                        self.traces[self.index][i - startp] = struct.unpack('f',b)[0]
                    else:
                        self.f.read(4)
            self.index=self.index+1
        self.f.seek(self.pos,0)
        self.index=0
    def read_onesample(self,no,N=0):
        if(N==0):
            N=self.Number_of_Traces
        OneSample=np.zeros(N,np.int16)
        while self.index<N:
            if self.index % 10000==0:
                print("Reading Sample "+str(no)+":\t"+str(self.index))
            p=self.f.read(int(self.cryptolen/2))
            c=self.f.read(int(self.cryptolen/2))
            for i in range(self.number_of_samples):
                if(self.isint):
                    if(i==no):
                        OneSample[self.index]=int.from_bytes(self.f.read(2), byteorder='little', signed=True)
                    else:
                        self.f.read(2)
                else:
                    if (i == no):
                        OneSample[self.index]  = float.from_bytes(self.f.read(4))
                    else:
                        self.f.read(4)
            self.index=self.index+1
        self.f.seek(self.pos,0)
        self.index=0
        return OneSample
    def read_plainciphertext(self,N=0):
        if(N==0):
            N=self.Number_of_Traces
        self.plaintext=np.zeros((N,int(self.cryptolen/2)), np.dtype('B'))
        self.ciphertext=np.zeros((N,int(self.cryptolen/2)),np.dtype('B'))
        while self.index<N:
            if self.index % 10000==0:
                print("Reading Plaintext/Ciphertext "+str(self.index))
            p=self.f.read(int(self.cryptolen/2))
            c=self.f.read(int(self.cryptolen/2))
            for i in range(int(self.cryptolen/2)):
                self.plaintext[self.index][i]  = p[i]
                self.ciphertext[self.index][i] = c[i]
            for i in range(self.number_of_samples):
                if(self.isint):
                    self.f.read(2)
                else:
                    self.f.read(4)
            self.index=self.index+1
        self.f.seek(self.pos,0)
        self.index=0
        return self.plaintext,self.ciphertext

    def WriteOneTrace(self,no):
        filename="Trace_{0}.txt".format(no)
        f=open(filename,"w")
        for i in range(np.size(self.traces,1)):
            f.writelines("{0}\n".format(self.traces[no,i]))
        f.close()
    def WriteAvgTrace(self,filename):
        f=open(filename,"w")
        for i in range(np.size(self.traces,1)):
            f.writelines("{0}\n".format(np.mean(self.traces[:,i])))
        f.close()




if __name__ == "__main__":
    trs = TRS_Reader("../DL_MaskedAES_fixedkey_49000Samples_5000Traces.trs")
    trs.read_header()
    trs.read_traces(10)
    key = bytearray(
        [0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
                      0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C ])
    for i in range(trs.Number_of_Traces):
        plaintext=trs.plaintext[i,0:16]
        ciphertext=trs.ciphertext[i,3:19]
        cipher = AES.new(key, AES.MODE_ECB)
        ciphertext1=cipher.encrypt(plaintext)
        for j in range(len(ciphertext)):
            if(cipher[j]!=ciphertext[j]):
                print("error!")
                break

    del (trs)