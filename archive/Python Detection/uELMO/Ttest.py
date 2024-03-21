import random
import numpy as np
from scipy.stats import t as Tdist
#import serial
#import scope
#import TRS_TraceSet
# Si Gao 2017.11.21
# Online Test up to 3 order
# From "Leakage Assessment Methodology: A Clear Roadmap for Side-Channel Evaluations"
class Ttest:

    def __init__(self,n):
        self.u_fix= np.zeros((1,n))
        self.CS_fix = np.zeros((7,n))
        self.u_random = np.zeros((1,n))
        self.CS_random = np.zeros((7,n))
        self.num_fix = 0
        self.num_random = 0

    def choose(self,n, k):
        if 0 <= k <= n:
            ntok = 1
            ktok = 1
            for t in range(1, min(k, n - k) + 1):
                ntok *= n
                ktok *= t
                n -= 1
            return ntok // ktok
        else:
            return 0
    def GetUandVar(self):
        e_fix = self.u_fix[0]
        e_random = self.u_random[0]
        var_fix = self.CS_fix[2] / self.num_fix
        var_random = self.CS_random[2] / self.num_random
        return [e_fix, e_random, np.sqrt(var_fix), np.sqrt(var_random)]
    def UpdateTrace(self,trace,flag):
        if(flag):
            # Update n
            self.num_fix = self.num_fix + 1
            # Update mean
            delta=trace-self.u_fix
            self.u_fix= self.u_fix+delta/self.num_fix
            if(self.num_fix<2):
                return
            # Update CS
            tempCS=np.copy(self.CS_fix)
            for d in range(2,7):
                self.CS_fix[d]=tempCS[d]
                for k in range(1,d-1):
                    self.CS_fix[d]=self.CS_fix[d]+self.choose(d, k)*tempCS[d-k]*np.power(-1*delta/self.num_fix,k)
                self.CS_fix[d]=self.CS_fix[d]+np.power((self.num_fix-1)/self.num_fix*delta,d)*(1-np.power((1.0/(1.0-self.num_fix)),d-1))
        else:
            # Update n
            self.num_random = self.num_random + 1
            # Update mean
            delta = trace - self.u_random
            self.u_random = self.u_random + delta / self.num_random

            if(self.num_random<2):
                return
            # Update CS
            tempCS = np.copy(self.CS_random)
            for d in range(2, 7):
                self.CS_random[d] = tempCS[d]
                for k in range(1, d - 1):
                    self.CS_random[d] = self.CS_random[d] + self.choose(d, k) * tempCS[d - k] * np.power(-1 * delta / self.num_random, k)
                self.CS_random[d] = self.CS_random[d] + np.power((self.num_random - 1) / self.num_random * delta, d) * (
                1 - np.power((1.0 / (1.0 - self.num_random)), d - 1))


    def WriteTTrace(self,filename,d,mode='Tvalue'):
        fo = open(filename, "w")
        if(d==1):
            e_fix= self.u_fix[0]
            e_random=self.u_random[0]
            var_fix=self.CS_fix[2]/self.num_fix
            var_random = self.CS_random[2] / self.num_random
            Tvalue=(e_fix-e_random)/np.sqrt((var_fix/self.num_fix)+(var_random/self.num_random)+0.000001)
        if (d == 2):
            e_fix = self.CS_fix[2]/self.num_fix
            e_random = self.CS_random[2]/self.num_random
            var_fix = (self.CS_fix[4]/self.num_fix)-np.power((self.CS_fix[2]/self.num_fix),2)
            var_random = (self.CS_random[4]/self.num_random)-np.power((self.CS_random[2]/self.num_random),2)
            Tvalue = (e_fix - e_random) / np.sqrt((var_fix / self.num_fix) + (var_random / self.num_random))
        if (d == 3):
            e_fix = (self.CS_fix[3]/self.num_fix)/np.power(np.sqrt(self.CS_fix[2]/self.num_fix),3)
            e_random = (self.CS_random[3]/self.num_random)/np.power(np.sqrt(self.CS_random[2]/self.num_random),3)
            var_fix = ((self.CS_fix[6]/self.num_fix)-np.power(self.CS_fix[3]/self.num_fix,2))/np.power((self.CS_fix[2]/self.num_fix),3)
            var_random = ((self.CS_random[6]/self.num_random)-np.power(self.CS_random[3]/self.num_random,2))/np.power((self.CS_random[2]/self.num_random),3)
            Tvalue = (e_fix - e_random) / np.sqrt((var_fix / self.num_fix) + (var_random / self.num_random))
        if(self.num_fix<=1 or self.num_random<=1):
            v=1
        else:
            v = ((var_fix / self.num_fix) + (var_random / self.num_random)) ** 2 / (
                    ((var_fix / self.num_fix) ** 2) / (self.num_fix - 1) + ((var_random / self.num_random) ** 2) / (
                        self.num_random - 1))
        maxpv=0
        for i in range(0, len(Tvalue)):
            if(mode=='Tvalue'):
                fo.write(str(Tvalue[i]) + '\n')
            else:
                fo.write(str(-np.log10(2*Tdist.sf(np.abs(Tvalue[i]),v[i]))) + '\n')
                if(maxpv<-np.log10(2*Tdist.sf(np.abs(Tvalue[i]),v[i]))):
                    maxpv=-np.log10(2 * Tdist.sf(np.abs(Tvalue[i]), v[i]))
        print("d={2}, maxT={0}, logp={1}".format(np.max(np.abs(Tvalue)),-np.log10(2*Tdist.sf(np.abs(np.max(np.abs(Tvalue))),self.num_fix+self.num_random-2)),d))
        fo.close()
        if (mode == 'Tvalue'):
            return np.max(np.abs(Tvalue))
        else:
            return maxpv
    def GetFixMean(self):
        return self.u_fix[0]
    def GetFixVariance(self):
        return self.CS_fix[2]/self.num_fix
    def GetT(self,d):
        if(d==1):
            e_fix= self.u_fix[0]
            e_random=self.u_random[0]
            var_fix=self.CS_fix[2]/self.num_fix
            var_random = self.CS_random[2] / self.num_random
            Tvalue=(e_fix-e_random)/np.sqrt((var_fix/self.num_fix)+(var_random/self.num_random)+0.00001)
        if (d == 2):
            e_fix = self.CS_fix[2]/self.num_fix
            e_random = self.CS_random[2]/self.num_random
            var_fix = (self.CS_fix[4]/self.num_fix)-np.power((self.CS_fix[2]/self.num_fix),2)
            var_random = (self.CS_random[4]/self.num_random)-np.power((self.CS_random[2]/self.num_random),2)
            Tvalue = (e_fix - e_random) / np.sqrt((var_fix / self.num_fix) + (var_random / self.num_random))
        if (d == 3):
            e_fix = (self.CS_fix[3]/self.num_fix)/np.power(np.sqrt(self.CS_fix[2]/self.num_fix),3)
            e_random = (self.CS_random[3]/self.num_random)/np.power(np.sqrt(self.CS_random[2]/self.num_random),3)
            var_fix = ((self.CS_fix[6]/self.num_fix)-np.power(self.CS_fix[3]/self.num_fix,2))/np.power((self.CS_fix[2]/self.num_fix),3)
            var_random = ((self.CS_random[6]/self.num_random)-np.power(self.CS_random[3]/self.num_random,2))/np.power((self.CS_random[2]/self.num_random),3)
            Tvalue = (e_fix - e_random) / np.sqrt((var_fix / self.num_fix) + (var_random / self.num_random))
        return -np.log10(2*Tdist.sf(np.abs(Tvalue),self.num_fix+self.num_random-2))

    def GetMaxT(self,d):
        if(d==1):
            e_fix= self.u_fix[0]
            e_random=self.u_random[0]
            var_fix=self.CS_fix[2]/self.num_fix
            var_random = self.CS_random[2] / self.num_random
            Tvalue=(e_fix-e_random)/np.sqrt((var_fix/self.num_fix)+(var_random/self.num_random))
        if (d == 2):
            e_fix = self.CS_fix[2]/self.num_fix
            e_random = self.CS_random[2]/self.num_random
            var_fix = (self.CS_fix[4]/self.num_fix)-np.power((self.CS_fix[2]/self.num_fix),2)
            var_random = (self.CS_random[4]/self.num_random)-np.power((self.CS_random[2]/self.num_random),2)
            Tvalue = (e_fix - e_random) / np.sqrt((var_fix / self.num_fix) + (var_random / self.num_random))
        if (d == 3):
            e_fix = (self.CS_fix[3]/self.num_fix)/np.power(np.sqrt(self.CS_fix[2]/self.num_fix),3)
            e_random = (self.CS_random[3]/self.num_random)/np.power(np.sqrt(self.CS_random[2]/self.num_random),3)
            var_fix = ((self.CS_fix[6]/self.num_fix)-np.power(self.CS_fix[3]/self.num_fix,2))/np.power((self.CS_fix[2]/self.num_fix),3)
            var_random = ((self.CS_random[6]/self.num_random)-np.power(self.CS_random[3]/self.num_random,2))/np.power((self.CS_random[2]/self.num_random),3)
            Tvalue = (e_fix - e_random) / np.sqrt((var_fix / self.num_fix) + (var_random / self.num_random))
        return np.max(np.abs(Tvalue))
    def WritelogPTrace(self,filename,d):
        Tv=self.GetT(d)
        Pv=-np.log10(2*Tdist.sf(np.abs(Tv),self.num_fix+self.num_random-2))
        fo = open(filename, "w")
        for i in range(0, len(Pv)):
            fo.write(str(Pv[i]) + '\n')
        if(np.max(Pv)>5):
           print("Error! Pv={}".format(np.max(Pv)))

if __name__ == '__main__':
        n=1000
        test=Ttest(n)

        for i in range(1000):
            trace=np.array([random.random() for i in range(n)])
            if(random.random()>0.5):
                test.UpdateTrace(trace,True)
            else:
                test.UpdateTrace(trace, False)
        test.WriteTTrace("T-test-O1.txt", 1)
        test.WriteTTrace("T-test-O2.txt", 2)
        test.WriteTTrace("T-test-O3.txt", 3)