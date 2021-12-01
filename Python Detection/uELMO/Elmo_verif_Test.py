import numpy as np
import LeakyStateReader
import Ttest
import hashlib
import datetime
from Chi2online import Chi2OnlineTest
class Elmo_verif_Test(object):
    def HW(self, X):
        y = np.zeros(len(X)).astype(int)
        for i in range(len(X)):
            y[i] = bin(X[i]).count("1")
        return y
    def ConvertHW(self,lsReader):
        slen=len(lsReader.Samples)
        traces=None
        no=[]
        for i in range(slen):
            sample=lsReader.Samples[i]
            len_old=len(no)
            for j in range(len(sample.Terms)):
                term=sample.Terms[j]
                X = np.array(term.data)
                # Check if X is constant
                if (np.all(X == X[0, :])):  # constant
                    continue

                sp= np.zeros(np.size(X,0))
                for k in range(np.size(X,1)):
                    sp=sp+self.HW(X[:,k])
                if (traces is None):
                    traces = sp.reshape((np.size(sp,0),1))
                    no.append([i,sample.inst,term.disp])
                else:
                    traces = np.hstack(( traces,sp.reshape((np.size(sp,0),1))))
                    no.append([i,sample.inst,term.disp])
            len_new = len(no)
            if(len_new==len_old):
                if (traces is None):
                    traces = np.random.rand(lsReader.tracenum, 1)
                    no.append([i, sample.inst, 'Pseudo term'])
                else:
                    traces = np.hstack((traces, np.random.rand(lsReader.tracenum, 1)))
                    no.append([i, sample.inst, 'Pseudo term'])

        return [traces,no]
    #Convert each non-linear term throught the compressing oracle, then do Chi^2 in the following
    def ConvertHO_term(self,lsReader):
        slen=len(lsReader.Samples)
        traces=None
        no=[]
        for i in range(slen):
            sample=lsReader.Samples[i]
            len_old=len(no)
            for j in range(len(sample.Terms)):
                term=sample.Terms[j]
                X = np.array(term.data)
                # Check if X is constant
                if (np.all(X == X[0, :])):  # constant
                    continue
                if(term.type==1):#ignoring linear term
                    continue
                sp= self.CompressOracle(X)
                if (traces is None):
                    traces = sp.reshape((np.size(sp,0),1))
                    no.append([i,sample.inst,term.disp])
                else:
                    traces = np.hstack(( traces,sp.reshape((np.size(sp,0),1))))
                    no.append([i,sample.inst,term.disp])
            len_new = len(no)
            if(len_new==len_old):
                if (traces is None):
                    traces = np.random.randint(256, size=(np.size(X, 0), 1))
                    no.append([i, sample.inst, 'Pseudo term'])
                else:
                    traces = np.hstack((traces, np.random.randint(256, size=(np.size(X, 0), 1))))
                    no.append([i, sample.inst, 'Pseudo term'])

        return [traces,no]
    def ConvertHWext(self,lsReader):
        slen=len(lsReader.Samples)
        traces=None
        no=[]
        for i in range(slen):
            sample=lsReader.Samples[i]
            len_old = len(no)
            for j in range(len(sample.Terms)):
                term=sample.Terms[j]
                X = np.array(term.data)
                # Check if X is constant
                if (np.all(X == X[0, :])):  # constant
                    continue
                sp= np.zeros(np.size(X,0))
                for k in range(np.size(X,1)):
                    sp=sp+self.HW(X[:,k])
                if(term.type==0):#Full
                    if(np.size(X,1)==4):#32 bit
                        sp=sp+self.HW(X[:,0]^X[:,1])+self.HW(X[:,1]^X[:,2])+self.HW(X[:,2]^X[:,3])
                    else:
                        sp = sp + self.HW(X[:, 0] ^ X[:, 4]) + self.HW(X[:, 1] ^ X[:, 5]) + self.HW(X[:, 2] ^ X[:, 6]) + self.HW(X[:, 3] ^ X[:, 7])
                if (traces is None):
                    traces = sp.reshape((np.size(sp,0),1))
                    no.append([i,sample.inst,term.disp])
                else:
                    traces = np.hstack(( traces,sp.reshape((np.size(sp,0),1))))
                    no.append([i,sample.inst,term.disp])
            len_new = len(no)
            if (len_new == len_old):
                if (traces is None):
                    traces = np.random.rand(np.size(X, 0), 1)
                    no.append([i, sample.inst, 'Pseudo term'])
                else:
                    traces = np.hstack((traces, np.random.rand(np.size(X, 0), 1)))
                    no.append([i, sample.inst, 'Pseudo term'])
        return [traces,no]
    def AddStates(self,Xprev, Xin):
        if(Xprev is None):
            return Xin
        if (np.all(Xin == Xin[0, :])):  # constant
            return Xprev
        byte_len=np.size(Xprev,1)
        for i in range(0,byte_len,4):
            Xt=Xin-Xprev[:,i:i+4]
            if (np.all(Xt == Xt[0, :])):  # constant
                return Xprev
        #not in the previous matrix; adding in
        return np.hstack((Xprev,Xin))

    def CompressOracle(self, X, no=0):
        y = np.zeros(len(X)).astype(int)
        for i in range(len(X)):
            y[i] = ((hashlib.md5(X[i].astype('uint8').tobytes())).digest())[no]
        return y
    def ConvertUnivariateHO(self,lsReader,compress_id):#Higher order detection
        slen=len(lsReader.Samples)
        traces=None
        no=[]
        for i in range(slen):
            sample=lsReader.Samples[i]#Each time sample
            Xsum=None

            for j in range(len(sample.Terms)):#Each term
                term=sample.Terms[j]
                X = np.array(term.data)


                # Check if X is constant
                if (np.all(X == X[0, :])):  # constant
                    continue
                for k in range(0,np.size(X,1),4):
                    Xsum=self.AddStates(Xsum,X[:,k:k+4])
            if(Xsum is not None):
                sp= self.CompressOracle(Xsum, compress_id)
                if (traces is None):
                    traces = sp.reshape((np.size(sp,0),1))
                    no.append([i,sample.inst,"All"])
                else:
                    traces = np.hstack(( traces,sp.reshape((np.size(sp,0),1))))
                    no.append([i,sample.inst,"All"])
            else:
                if (traces is None):
                    traces = np.random.randint(256, size=(np.size(X, 0), 1))
                    no.append([i, sample.inst, 'Pseudo term'])
                else:
                    traces = np.hstack((traces, np.random.randint(256, size=(np.size(X, 0), 1))))
                    no.append([i, sample.inst, 'Pseudo term'])
        return [traces,no]
    # Convert leaky states to bivariate leakage through the compression oracle
    # mode='cross term': same cycle, different terms
    # mode='cross cycle': different cycles
    def ConvertBivariateHO(self,lsReader,compress_id,mode='cross term',c1=None,c2=None):#Higher order detection
        slen=len(lsReader.Samples)
        traces=None
        no=[]
        states=[]
        for i in range(slen):
            sample=lsReader.Samples[i]#Each time sample
            if(i<1 or i>44):
                continue
            Xsum=None
            len_old=len(states)
            for j in range(len(sample.Terms)):#Each term
                term=sample.Terms[j]
                X = np.array(term.data)
                # Check if X is constant
                if (np.all(X == X[0, :])):  # constant
                    continue
                for k in range(0,np.size(X,1),4):
                    Xsum=self.AddStates(Xsum,X[:,k:k+4])

                #Add X to states
                states.append(X)
                no.append([i, sample.inst, term.disp])
            len_new = len(states)
            if(len_old==len_new):
                #no valid data for this cycle, add a pseudo term
                X=np.random.randint(256, size=(np.size(X, 0), 4))
                states.append(X)
                no.append([i, sample.inst, 'Pseudo term'])
            else:
                if (Xsum is not None):
                    states.append(Xsum)
                    no.append([i, sample.inst, "All"])
        no1=[]
        #now generate the bivariate leakage
        for i in range(len(no)):
            sid1 = no[i][0]
            print("i={0}".format(i))
            if((c1 is not None) and (c1!=sid1)):
                continue
            for j in range(len(no)):
                Xsum = None
                #select two terms
                sid2=no[j][0]
                if ((c2 is not None) and (c2 != sid2)):
                    continue
                #if(sid1==sid2 and mode=='cross cycle'):
                #    continue
                if (sid1 != sid2 and mode=='cross term'):
                    continue
                X1=states[i]
                for k in range(0, np.size(X1, 1), 4):
                    Xsum = self.AddStates(Xsum, X1[:, k:k + 4])
                X2=states[j]
                for k in range(0, np.size(X2, 1), 4):
                    Xsum = self.AddStates(Xsum, X2[:, k:k + 4])
                sp= self.CompressOracle(Xsum, compress_id)
                if (traces is None):
                    traces = sp.reshape((np.size(sp,0),1))
                    no1.append([no[i][0],no[j][0],no[i][2],no[j][2]])
                else:
                    traces = np.hstack(( traces,sp.reshape((np.size(sp,0),1))))
                    no1.append([no[i][0],no[j][0], no[i][2], no[j][2]])
        return [traces,no1]
    # Convert leaky states to bivariate leakage through the compression oracle
    # mode='cross term': same cycle, different terms
    # mode='cross cycle': different cycles
    def ConvertBivariateHW(self,lsReader,c1=None,c2=None):#Higher order detection
        slen=len(lsReader.Samples)
        traces=None
        no=[]
        states=[]
        for i in range(slen):
            sample=lsReader.Samples[i]#Each time sample
            if(i<1 or i>44):
                continue
            Xsum=None
            len_old=len(states)
            for j in range(len(sample.Terms)):#Each term
                term=sample.Terms[j]
                X = np.array(term.data)
                # Check if X is constant
                if (np.all(X == X[0, :])):  # constant
                    continue
                for k in range(0,np.size(X,1),4):
                    Xsum=self.AddStates(Xsum,X[:,k:k+4])
                if(term.type==0):
                    for k in range(1,int(np.size(X,1)/4)):
                        X[:,0]=X[:,0]^X[:,k*4]
                        X[:, 1] = X[:, 1] ^ X[:, k * 4+1]
                        X[:, 2] = X[:, 2] ^ X[:, k * 4 + 2]
                        X[:, 3] = X[:, 3] ^ X[:, k * 4 + 3]
                    X=X[:,0:4]
                #Add X to states
                states.append(X)
                no.append([i, sample.inst, term.disp])
            len_new = len(states)
            if(len_old==len_new):
                #no valid data for this cycle, add a pseudo term
                X=np.random.randint(256, size=(np.size(X, 0), 4))
                states.append(X)
                no.append([i, sample.inst, 'Pseudo term'])
            else:
                if (Xsum is not None):
                    states.append(Xsum)
                    no.append([i, sample.inst, "All"])
        no1=[]
        #now generate the bivariate leakage
        for i in range(len(no)):
            sid1 = no[i][0]
            print("i={0}".format(i))
            if((c1 is not None) and (c1!=sid1)):
                continue
            for j in range(len(no)):
                Xsum = None
                #select two terms
                sid2=no[j][0]
                if ((c2 is not None) and (c2 != sid2)):
                    continue
                X1 = states[i]
                sp1 = np.zeros(np.size(X1, 0))
                for k in range(np.size(X1, 1)):
                    sp1 = sp1 + self.HW(X1[:, k])
                X2 = states[j]
                sp2 = np.zeros(np.size(X2, 0))
                for k in range(np.size(X2, 1)):
                    sp2 = sp2 + self.HW(X2[:, k])
                if (traces is None):
                    traces = np.multiply(sp1,sp2).reshape((np.size(sp1,0),1))
                    no1.append([no[i][0],no[j][0],no[i][2],no[j][2]])
                else:
                    traces = np.hstack(( traces,np.multiply(sp1,sp2).reshape((np.size(sp1,0),1))))
                    no1.append([no[i][0],no[j][0], no[i][2], no[j][2]])
        return [traces,no1]
    def Elmo_verif_Test_Bivariate(self, file,N,header_name=None, no=0,mode='cross term',c1=None,c2=None):
        self.lsReader = LeakyStateReader.LeakyStateReader(file)
        self.lsReader.ReadInstrHeader()
        if(header_name is not None):
            self.lsReader.PrintInstrHeader(header_name)
        self.lsReader.ReadTraces(N)
        [traces,Info]=self.ConvertBivariateHO(self.lsReader, no,mode,c1,c2)
        Chi2OL = Chi2OnlineTest(
            tracelen=np.size(traces,1), nbins=256,binrange=(0, 256))
        for i in range(np.size(traces,0)):
            if(i%1000==0):
                print("Update trace #{0}\n".format(i))
            if(i>np.size(traces,0)/2):
                Chi2OL.UpdateTrace(traces[i, :], True)
            else:
                Chi2OL.UpdateTrace(traces[i,:],False)
        Chi2OL.UpdateRecord()
        print('Chi2 Statistics = ', np.max(Chi2OL.records['statistic']))
        print('Chi2 p-values = ', np.max(-np.log10(Chi2OL.records['pvalue'])))
        fo = open("Positive_T-test_cycle-Bivariate.txt", "w")
        fo1 = open("elmo_T-test-Bivariate.txt", "w")
        cycle1=-1
        cycle2=-1
        pv=(-np.log10(Chi2OL.records['pvalue'])).tolist()[0]
        maxpv=0
        for i in range(np.size(traces,1)):
            info=Info[i]
            sid1=info[0]
            sid2=info[1]
            if(sid1!=cycle1 or sid2!=cycle2):#when cycle changes
                if(cycle1!=-1 or cycle2!=-1):#except for the first one
                    fo1.writelines("{0}\n".format(maxpv))#output the current max pv
                    print("Cycle {0}* Cycle{1}: logpv={2}\n".format(cycle1+1, cycle2+1,maxpv))
                #move on the next
                maxpv = pv[i]
                cycle1 = sid1
                cycle2 = sid2
            else: #cycle did not change
                if (pv[i] > maxpv):
                    maxpv = pv[i]

            if(pv[i]>5):
                fo.writelines("Cycle {0}* Cycle{1}: Term1={2}, Term2={3}, logpv={4}\n".format(sid1+1,sid2+1,info[2],info[3],pv[i]))
        fo1.writelines("{0}\n".format(maxpv))  # output the current max pv
        print("Cycle {0}* Cycle{1}: logpv={2}\n".format(cycle1 + 1, cycle2 + 1, maxpv))
        fo.close()
        fo1.close()
    def Elmo_verif_Test_HWBivariate(self, file,N,header_name=None,c1=None,c2=None):
        self.lsReader = LeakyStateReader.LeakyStateReader(file)
        self.lsReader.ReadInstrHeader()
        if(header_name is not None):
            self.lsReader.PrintInstrHeader(header_name)
        self.lsReader.ReadTraces(N)
        [traces,Info]=self.ConvertBivariateHW(self.lsReader, c1,c2)
        tvla = Ttest.Ttest(np.size(traces, 1))
        for i in range(np.size(traces,0)):
            if(i%1000==0):
                print("Update trace #{0}\n".format(i))
            if(i>np.size(traces,0)/2):
                tvla.UpdateTrace(traces[i, :], True)
            else:
                tvla.UpdateTrace(traces[i, :], False)
        Tv=tvla.GetT(1)
        fo = open("Positive_T-test_cycle-BivariateHW.txt", "w")
        fo1 = open("elmo_T-test-BivariateHW.txt", "w")
        cycle1=-1
        cycle2=-1
        maxpv=0
        for i in range(np.size(traces,1)):
            info=Info[i]
            sid1=info[0]
            sid2=info[1]
            if(sid1!=cycle1 or sid2!=cycle2):#when cycle changes
                if(cycle1!=-1 or cycle2!=-1):#except for the first one
                    fo1.writelines("{0}\n".format(maxpv))#output the current max pv
                    print("Cycle {0}* Cycle{1}: logpv={2}\n".format(cycle1+1, cycle2+1,maxpv))
                #move on the next
                maxpv = Tv[i]
                cycle1 = sid1
                cycle2 = sid2
            else: #cycle did not change
                if (Tv[i] > maxpv):
                    maxpv = Tv[i]

            if(Tv[i]>5):
                fo.writelines("Cycle {0}* Cycle{1}: Term1={2}, Term2={3}, logpv={4}\n".format(sid1+1,sid2+1,info[2],info[3],Tv[i]))
        fo1.writelines("{0}\n".format(maxpv))  # output the current max pv
        print("Cycle {0}* Cycle{1}: logpv={2}\n".format(cycle1 + 1, cycle2 + 1, maxpv))
        fo.close()
        fo1.close()
    def Elmo_verif_Test_HO(self, file,N,header_name=None, no=0):
        self.lsReader = LeakyStateReader.LeakyStateReader(file)
        self.lsReader.ReadInstrHeader()
        if(header_name is not None):
            self.lsReader.PrintInstrHeader(header_name)
        self.lsReader.ReadTraces(N)
        [traces,Info]=self.ConvertUnivariateHO(self.lsReader, no)
        Chi2OL = Chi2OnlineTest(
            tracelen=np.size(traces,1), nbins=256,binrange=(0, 256))
        for i in range(np.size(traces,0)):
            if(i%1000==0):
                print("Update trace #{0}\n".format(i))
            if(i>np.size(traces,0)/2):
                Chi2OL.UpdateTrace(traces[i, :], True)
            else:
                Chi2OL.UpdateTrace(traces[i,:],False)
        Chi2OL.UpdateRecord()
        print('Chi2 Statistics = ', np.max(Chi2OL.records['statistic']))
        print('Chi2 p-values = ', np.max(-np.log10(Chi2OL.records['pvalue'])))
        fo = open("Positive_T-test_cycle-HO.txt", "w")
        fo1 = open("elmo_T-test-HO.txt", "w")
        cycle=-1
        pv=(-np.log10(Chi2OL.records['pvalue'])).tolist()[0]
        for i in range(np.size(traces,1)):
            info=Info[i]
            if(info[0]>cycle):
                if(info[0]!=0):
                    fo1.writelines("{0}\n".format(pv[i]))
            if(pv[i]>5):
                fo.writelines("Cycle {0}: Instr={1}, Term={2}, logpv={3}\n".format(info[0]+1,info[1],info[2],pv[i]))
        fo.close()
        fo1.close()
    def Elmo_verif_Test_1st_linear(self, file,N,header_name=None):
        self.lsReader = LeakyStateReader.LeakyStateReader(file)
        self.lsReader.ReadInstrHeader()
        if(header_name is not None):
            self.lsReader.PrintInstrHeader(header_name)
        self.lsReader.ReadTraces(N)
        [traces,Info]=self.ConvertHW(self.lsReader)

        tvla = Ttest.Ttest(np.size(traces,1))
        for i in range(np.size(traces,0)):
            if(i%1000==0):
                print("Update trace #{0}\n".format(i))
            if(i>np.size(traces,0)/2):
                tvla.UpdateTrace(traces[i, :], True)
            else:
                tvla.UpdateTrace(traces[i,:],False)
        Tv=tvla.GetT(1)
        fo = open("Positive_T-test_cycle-linear.txt", "w")
        fo1 = open("elmo_T-test-linear.txt", "w")
        cycle=-1
        maxT=0
        for i in range(np.size(traces,1)):
            info=Info[i]
            if(info[0]>cycle):
                if(info[0]!=0):
                    fo1.writelines("{0}\n".format(maxT))
                maxT=abs(Tv[i])
                cycle=info[0]
            else:
                if(abs(Tv[i])>maxT):
                    maxT=abs(Tv[i])
            if(abs(Tv[i])>4.5):
                fo.writelines("Cycle {0}: Instr={1}, Term={2}, Tvalue={3}\n".format(info[0]+1,info[1],info[2],Tv[i]))
        fo.close()
        fo1.close()
    def Elmo_verif_Test_1st_nonlinear(self, file,N,header_name=None):
        self.lsReader = LeakyStateReader.LeakyStateReader(file)
        self.lsReader.ReadInstrHeader()
        if(header_name is not None):
            self.lsReader.PrintInstrHeader(header_name)
        self.lsReader.ReadTraces(N)
        [traces,Info]=self.ConvertHO_term(self.lsReader)

        Chi2OL = Chi2OnlineTest(
            tracelen=np.size(traces, 1), nbins=256, binrange=(0, 256))
        for i in range(np.size(traces,0)):
            if(i%1000==0):
                print("Update trace #{0}\n".format(i))
            if(i>np.size(traces,0)/2):
                Chi2OL.UpdateTrace(traces[i, :], True)
            else:
                Chi2OL.UpdateTrace(traces[i,:],False)
        Chi2OL.UpdateRecord()
        print('Chi2 Statistics = ', np.max(Chi2OL.records['statistic']))
        print('Chi2 p-values = ', np.max(-np.log10(Chi2OL.records['pvalue'])))
        fo = open("Positive_T-test_cycle-1st-nL.txt", "w")
        fo1 = open("elmo_T-test-1st-nL.txt", "w")
        pv = (-np.log10(Chi2OL.records['pvalue'])).tolist()[0]
        cycle=-1
        maxT=0
        for i in range(np.size(traces,1)):
            info=Info[i]
            if(info[0]>cycle):
                if(info[0]!=0):
                    fo1.writelines("{0}\n".format(maxT))
                maxT=pv[i]
                cycle=info[0]
            else:
                if(pv[i]>maxT):
                    maxT=pv[i]
            if(pv[i]>5):
                fo.writelines("Cycle {0}: Instr={1}, Term={2}, Tvalue={3}\n".format(info[0]+1,info[1],info[2],pv[i]))
        fo.close()
        fo1.close()
if __name__ == '__main__':
        N = 1000
        #RegressionTest().ISWMultd2Analysis()
        start = datetime.datetime.now()
        #Elmo_verif_Test().Elmo_verif_Test_HWBivariate("/home/IWAS/gaosi/Documents/Tooling paper/Into-the-unknown-a-unifed-leakage-verifcation-framework/Detecting/ISWd3/Detection/Input A/ISWMult_LeakyStates.bin",N,"ISWd3.txt",None,5)
        Elmo_verif_Test().Elmo_verif_Test_1st_linear(
            "C:\\Users\\gs\\Documents\\GitHub\\uELMO\\Windows\\uELMO\\Examples\\ISWd2\\Detection\\ISWd2_LeakyState.bin",
            N, "uELMO_ISWd2.txt")
        #Elmo_verif_Test().Elmo_verif_Test_HWBivariate(
        #    "/home/IWAS/gaosi/Documents/Tooling paper/Into-the-unknown-a-unifed-leakage-verifcation-framework/Detecting/ISWd3/Detection/Input A/ISWMult_LeakyStates.bin",
        #    N, "ISWd3.txt", None, 8)
        end= datetime.datetime.now()
        delta = end- start
        print("Total verification time: {0} us\n".format(delta.total_seconds()*1000000/N))
        #Elmo_verif_Test().Elmo_verif_Test_HWBivariate("/home/IWAS/gaosi/Documents/Tooling paper/Into-the-unknown-a-unifed-leakage-verifcation-framework/Detecting/ISWd3/Detection/Input A/ISWMult_LeakyStates.bin", N,"ISWd3.txt",None,5)