#!/usr/bin/env python3
import numpy as np
import math
from scipy import linalg
from scipy.stats import f
import TRS_Reader
import LeakyStateReader
class ModelVerifier(object):
    def __init__(self):
        self.lsReader = None
# Basic math
    def PCA(self, data):
        centered_data = data - np.mean(data)
        if(np.isnan(centered_data).any()):
            return
        U, S, V = linalg.svd(centered_data, full_matrices=False, lapack_driver='gesvd')
        components = V
        coefficients = np.dot(U, np.diag(S))
        return coefficients
    def FullbaseFtest(self,X,Y):
        N=len(Y)
        m=len(set(X))
        XY=sorted(list(zip(X,Y)))
        dictavg = {}
        dictcount={}
        avg=np.sum(Y)/N
        Xv=XY[0][0]
        sumy=float(XY[0][1])
        count=1
        for i in range(1,N):
            if(XY[i][0]==Xv):#Same entry
               sumy=sumy+XY[i][1]
               count=count+1
            else: #A new entry
                dictavg.update({Xv:sumy/count})
                dictcount.update({Xv:count})
                Xv=XY[i][0]
                count=1
                sumy=float(XY[i][1])
        #Last key
        dictavg.update({Xv: sumy / count})
        dictcount.update({Xv: count})
        #Now dictavg has all the means
        #Upper
        Upper=0
        for x in set(X):
            Upper=Upper+dictcount[x]*((dictavg[x]-avg)**2)
        Upper=Upper/float(m-1)
        #Lower
        Lower=0
        for x,y in XY:
            Lower=Lower+((y-dictavg[x])**2)
        Lower=Lower/float(N-m)

        #F-test
        F=Upper/Lower
        p_value=f.sf(F,m-1,N-m)

        #Compute SSE for further test
        SSE=Lower*(N-m)
        SST=np.sum((Y-avg)**2)
        R2=1-SSE/SST

        return [p_value, R2, SSE, SST]
    def FullbaseFtest_CV(self,X,Y, X_cv, Y_cv):
        N=len(Y)
        N_cv = len(Y_cv)
        m_cv = len(set(X_cv))
        m=len(set(X))
        XY=sorted(list(zip(X,Y)))
        XY_cv = sorted(list(zip(X_cv, Y_cv)))
        dictavg = {}
        dictcount={}
        avg=np.sum(Y)/N
        avg_cv = np.sum(Y_cv) / N_cv
        Xv=XY[0][0]
        sumy=float(XY[0][1])
        count=1
        for i in range(1,N):
            if(XY[i][0]==Xv):#Same entry
               sumy=sumy+XY[i][1]
               count=count+1
            else: #A new entry
                dictavg.update({Xv:sumy/count})
                dictcount.update({Xv:count})
                Xv=XY[i][0]
                count=1
                sumy=float(XY[i][1])
        #Last key
        dictavg.update({Xv: sumy / count})
        dictcount.update({Xv: count})
        #Now dictavg has all the means
        #Upper
        Upper=0
        for x in set(X):
            Upper=Upper+dictcount[x]*((dictavg[x]-avg_cv)**2)
        Upper=Upper/float(m_cv-1)
        #Lower
        Lower=0
        for x,y in XY_cv:
            Lower=Lower+((y-dictavg[x])**2)
        Lower=Lower/float(N_cv-m_cv)

        #F-test
        F=Upper/Lower
        p_value=f.sf(F,m_cv-1,N_cv-m_cv)

        #Compute SSE for further test
        SSE=Lower*(N_cv-m_cv)
        SST=np.sum((Y_cv-avg_cv)**2)
        R2=1-SSE/SST

        return [p_value, R2, SSE, SST]
    # Each bit of X will be added as one variable; upto to m bit
    def LinearbaseR2(self,Xm,m, Y,B):
        N=len(Y)
        avg=np.mean(Y)
        #Xm=np.zeros((N,m+1))
        #for i in range(m):
        #    Xm[:,i]=(X>>i)&0x01
        #Xm[:, m] = 1
        #if(B==None):
        #    B=np.linalg.pinv(Xm)
        #beta=np.matmul(B,Y)
        beta = B.dot(Y)
        Ye=np.matmul(Xm,beta)
        #Calculate SSE
        SSE=0.0
        SST=0.0
        for i in range(N):
            SSE=SSE+(Y[i]-Ye[i])**2
            SST=SST+(Y[i]-avg)**2
        R2=1-SSE/SST
        #Calculate p-vale
        F=((SST-SSE)/(m))/(SSE/(N-m-1))
        p_value = f.sf(F, m , N - m-1)

        return [p_value,R2, SSE]
    # Each bit of X will be added as one variable; upto to m bit
    def LinearbaseR2_CV(self,Xm_m,Xm_cv, m, Y_m, Y_cv,B_m,N):
        N_cv=len(Y_cv)
        avg_cv=np.mean(Y_cv)
        beta = B_m.dot(Y_m)
        Ye=np.matmul(Xm_cv,beta)
        #Calculate SSE
        SSE=0.0
        SST=0.0
        for i in range(N_cv):
            SSE=SSE+(Y_cv[i]-Ye[i])**2
            SST=SST+(Y_cv[i]-avg_cv)**2
        R2=1-SSE/SST
        #Calculate p-vale
        F=((SST-SSE)/(m))/(SSE/(N-m-1))
        p_value = f.sf(F, m , N - m-1)

        return [p_value,R2, SSE]
    # 2^m for full base; m for linear base
    def LinearbaseVSFullBase(self,m,N, SSEL, SSEF):

        #Calculate p-vale
        F=((SSEL-SSEF)/(2**m-m-1))/(SSEF/(N-(2**m)))
        p_value = f.sf(F, (2**m-m-1) ,N-(2**m))

        return p_value
    # Ftest for nested base; p1,p2
    def Ftest_nested(self,p1,p2,N, SSE1, SSE2):

        #Calculate p-vale
        F=((SSE1-SSE2)/(p2-p1))/(SSE2/(N-p2))
        p_value = f.sf(F, p2-p1, N-p2)

        return [p_value,F]
# Analysis tools; with or without output
    def FvLTest(self,trs,XL,X,N,start,end,threshold,filename=None):
        if(filename!=None):
            fo1 = open(filename, "w")
        maxpv=0
        pv=np.zeros((1,end-start))
        m=np.linalg.matrix_rank(XL)
        print('m= {0} vars\n'.format(m))
        B=np.linalg.pinv(XL)
        for i in range(start, end):
            if (i % 100 == 0):
                print("i=" + str(i))
            Y = trs.traces[:, i]
            if(m<len(set(X))):
                [pv[0, i - start], R2, SSEF, SST] = self.FullbaseFtest(X, Y)
                [pv[0, i - start], R2, SSEL] = self.LinearbaseR2(XL,m, Y,B)
                [pv[0, i - start],Fstat] =self.Ftest_nested(m, len(set(X)), N, SSEL, SSEF)
                pv[0, i - start] = -np.log10(pv[0, i-start])
            else:
                pv[0, i - start] =0
            if (filename != None):
                fo1.write(str(pv[0, i-start])+'\r\n')
            if(i-start>20 and end-i>20 and pv[0, i-start]>maxpv):
                maxpv=pv[0, i-start]
                if(maxpv>threshold):
                    if (filename != None):
                        fo1.close()
                    return maxpv

        if (filename != None):
            #fo1.writelines('\r\n')
            fo1.close()
        return maxpv
    def FvLTest_Details(self,trs,XL,X,N,start,end,CV_start,filename=None,mode='append'):
        #Result File Format:
        #SSE_F   df_F    SSE_L    df_L    Fstat   -log(pv_Ftest)  SST
        if(filename!=None):
            if(mode=='append'):
                fo1 = open(filename, "a")
            else:
                fo1 = open(filename, "w")
        maxpv=0

        XL_cv=XL[CV_start:N,:]
        XL = XL[0:CV_start, :]
        X_m=X[0:CV_start]
        X_cv=X[CV_start:N]
        m=np.linalg.matrix_rank(XL)
        B=np.linalg.pinv(XL)
        for i in range(start, end):
            if (i % 100 == 0):
                print("i=" + str(i))
            Y = trs.traces[:, i]
            Y_m = Y[0:CV_start]
            Y_cv =Y[CV_start:N]
            [pv, R2_F, SSEF_cv, SST_cv] = self.FullbaseFtest_CV(X_m, Y_m,X_cv,Y_cv)
            [pv, R2_L, SSEL_cv] = self.LinearbaseR2_CV(XL,XL_cv, m, Y_m,Y_cv, B,N)
            if(m<len(set(X))):
                [pv, R2_F, SSEF, SST] = self.FullbaseFtest(X_m, Y_m )
                [pv, R2_L, SSEL] = self.LinearbaseR2(XL, m, Y_m, B)
                [pv,Fstat] =self.Ftest_nested(m, len(set(X)), CV_start, SSEL, SSEF)
                pv = -np.log10(pv)
            else:
                pv =0
                Fstat=0
            if (filename != None):
                fo1.write(str(np.log10(SSEF_cv))+'\t')
                fo1.write(str(len(set(X))) + '\t')
                fo1.write(str(np.log10(SSEL_cv)) + '\t')
                fo1.write(str(m) + '\t')
                fo1.write(str(Fstat) + '\t')
                fo1.write(str(pv) + '\t')
                fo1.write(str(np.log10(SST_cv)) + '\n')
            if(pv>maxpv):
                maxpv=pv
        if (filename != None):
            fo1.close()
        return maxpv
    def LRA(self,trs,X,m,start,end,filename=None):
        if (filename != None):
            fo = open(filename, "w")
        maxpv = 0
        pv = np.zeros((1, end - start))
        B = np.linalg.pinv(X)
        for i in range(start, end):
            if (i % 100 == 0):
                print("i=" + str(i))
            Y = trs.traces[:, i]
            [pv[0, i - start], R2, SSEL] = self.LinearbaseR2(X,m, Y,B)
            pv[0, i - start] = -np.log10(pv[0, i-start])
            if (filename != None):
                fo.write(str(pv[0, i-start])+'\r\n')
            if(i-start>10 and end-i>10 and pv[0, i-start]>maxpv):
                maxpv=pv[0, i-start]

        if (filename != None):
            fo.close()
    def LRA_Fullbase(self, trs, X, start, end, filename=None):
            if (filename != None):
                fo = open(filename, "w")
            maxpv = 0
            pv = np.zeros((1, end - start))
            for i in range(start, end):
                if (i % 100 == 0):
                    print("i=" + str(i))
                Y = trs.traces[:, i]
                [pv[0, i - start], R2, SSEL, SST] = self.FullbaseFtest(X, Y);
                pv[0, i - start] = -np.log10(pv[0, i - start])
                if (filename != None):
                    fo.write(str(pv[0, i - start]) + '\n')
                if (i - start > 10 and end - i > 10 and pv[0, i - start] > maxpv):
                    maxpv = pv[0, i - start]

            if (filename != None):
                fo.close()
# Operations on the regression basis
    def AddTerm(self,XL,Xt,m):
        if(XL is None):
            XL=np.ones(np.size(Xt)).transpose()
        else:
            XL=XL.transpose()
        for i in range(m):
            t = np.ones(np.size(Xt), dtype='uint8')
            t = t & ((Xt >> i) & 0x1)
            XL = np.vstack((XL, t.transpose()))
        XL=XL.transpose()
        return XL
    def RegressionExtend(self,X,m,Terms=None, Linear=None,bit=2):
        #Xe=np.zeros(np.size(X),dtype='uint64')
        Xe=np.ones(np.size(X)).transpose()
        count=0
        for i in range(1, 2**m):
            t=np.ones(np.size(X),dtype='uint8')
            bin_i= '{0:0{1}b}'.format(i,m)[::-1]
            v=0
            TouchedBits=[False for k in range(bit)]#Do not allow cross-bit interaction
            for j in range(0,m):
                if(bin_i[j]=='1'):
                    t=t&((X>>j)&0x1)
                    v=v|(0x1<<int(j/bit))
                    TouchedBits[j%bit]=True
            # Count touched bits
            tcount=0
            for k in range(bit):
                if(TouchedBits[k]):
                    tcount=tcount+1
            if(tcount>1 and Linear!=None and Linear[v]==True):#None-linear forbidden
                continue
            if(Terms==None or Terms[v]==True):#Allowed Term
                #Xe=Xe^t
                Xe=np.vstack((Xe,t.transpose()))
                count=count+1
                #Xe=Xe<<1
        #Xe=Xe>>1
        Xe=Xe.transpose()
        return [Xe,count]
    def Model2Terms(self,Model,m):
        Terms=[False for i in range(2**m)]
        for i in range(2**m):
            if((Model>>i)&0x1==1):
                Terms[i]=True
        return Terms
# Regression with manually written models
    def SboxSimulator(self,trs,bitn,mode='standard'):
        #mode='standard': standard model without incorrect access/glitches
        #mode='extend': model with incorrect access/glitches
        #model='elmo': model with only Op1/Op2/Op1HD/Op2HD
        #model='hw' model with only Op2 HW
        bitmask=2**bitn-1
        r1=trs.plaintext[:, 0]&bitmask
        r2=trs.plaintext[:, 1]&bitmask
        r3=trs.plaintext[:, 2]&bitmask
        r4=trs.plaintext[:, 3]&bitmask
        r5=r1^r1# r6=0
        r6=r1^r1# r6=0
        X=r1^(r2<<bitn)^(r3.astype(dtype='uint16')<<(2*bitn))^(r4.astype(dtype='uint16')<<(3*bitn))
        ExpVar=[]

        regB = r1^r1
        regA = r1^r1
        reg_desti_HD=r1^r1
        Port1 = r6
        Port2 = r6
        reg_desti=r1^r1
        reg_desti_new=r1^r1
        Zflag_new = r1 ^ r1
        Nflag_new = r1 ^ r1
        Zflag = r1 ^ r1
        Nflag = r1 ^ r1
        regB = r1 ^ r1
        regA = r1 ^ r1

        #0-250
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new = r1^r1
        regA_new = r1^r1
        reg_desti = r6
        r6= r1^r1#r6=0
        reg_desti_new = r6
        Port1_new = r5
        Port2_new = r3
        Nflag=Nflag_new
        Zflag=Zflag_new
        Nflag_new=r6>>(bitn-1)
        Zflag_new=np.multiply(r6==0,1)

        [XExecute, count_e] = self.RegressionExtend(
          (regA << (2*bitn))  ^ (regB << bitn), (2 * bitn))

        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)

        #count = np.size(XSum, 1)
        #print('Cycle 0-250:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 0, 250, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))

        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        #250-500
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new = r3
        regA_new = regA
        reg_desti = r5
        r5= r3
        reg_desti_new = r5
        Port1_new = r5
        Port2_new = r1
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (3 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 250-500:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 250, 500, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new



        # 500-750
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new = r1
        regA_new = r5
        reg_desti = r5
        r5 = r5&r1
        reg_desti_new = r5
        Port1_new = r2
        Port2_new = r5
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r5 >> (bitn - 1)
        Zflag_new = np.multiply(r5 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
           (regA << (3 * bitn)) ^(regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 500-750:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 500, 750, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        # 750-1000
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
        # Incorrect Access
        regB_new = r5
        regA_new = r2
        reg_desti = r2
        r2 = r2 ^ r5
        reg_desti_new = r2
        Port1_new = r5
        Port2_new = r4
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r2 >> (bitn - 1)
        Zflag_new = np.multiply(r2 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))

        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 750-1000:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 750, 1000, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new


        # 1000-1250
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new = r4
        regA_new = regA
        reg_desti = r5
        r5 = r4
        reg_desti_new = r5
        Port1_new = r5
        Port2_new = r2
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (2 * bitn))  ^ (regB << bitn) ^ regB_new, (3 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 1000-1250:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 1000, 1250, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        # 1250-1500
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        if(mode=='extend'):
        # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r3, bitn)
        regB_new=r2
        regA_new=r5
        reg_desti = r5
        r5=r5&r2
        reg_desti_new = r5
        Port1_new=r5
        Port2_new=r1
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r5 >> (bitn - 1)
        Zflag_new = np.multiply(r5 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))

        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)

        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 1250-1500:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 1250, 1500, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new


        # 1500-1750
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new=r1
        regA_new=r5
        reg_desti = r5
        r5=r5^r1
        reg_desti_new = r5
        Port1_new=r6
        Port2_new=r2
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r5 >> (bitn - 1)
        Zflag_new = np.multiply(r5 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))

        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 1500-1750:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 1500, 1750, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new

        # 1750-2000
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            #XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            #XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            #XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r3, bitn)
            #XLeft = self.AddTerm(XLeft, r4, bitn)
            #XLeft = self.AddTerm(XLeft, r4 ^ r6, bitn)
        regB_new=r2
        regA_new=regA
        reg_desti = r6
        r6=r2
        reg_desti_new = r6
        Port1_new=r6
        Port2_new=r5
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (3 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 1750-2000:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, 20000, 1750, 2000, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new

        # 2000-2250
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            #XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            #XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            #XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r4, bitn)
            #XLeft = self.AddTerm(XLeft, r4 ^ r6, bitn)
        regB_new=r5
        regA_new=r6
        reg_desti = r6
        r6=r6|r5
        reg_desti_new = r6
        Port1_new=r3
        Port2_new=r6
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r6 >> (bitn - 1)
        Zflag_new = np.multiply(r6 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^(regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        count = np.size(XSum, 1)
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 2000, 2250, 10, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new

        # 2250-2500
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
           # Common
           XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
           XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
           XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
           XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
           XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
           # Incorrect Access
           XLeft = self.AddTerm(XLeft, r4, bitn)
           XLeft = self.AddTerm(XLeft, r4 ^ r6, bitn)
        regB_new=r6
        regA_new=r3
        reg_desti = r3
        r3=r3^r6
        reg_desti_new = r3
        Port1_new=r1
        Port2_new=r3
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r3 >> (bitn - 1)
        Zflag_new = np.multiply(r3 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn))^(regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        #count = np.size(XSum, 1)
        ExpVar.append(XSum)
        #print('Cycle 2250-2500:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 2250, 2500, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new
        reg_desti_HD = reg_desti ^ reg_desti_new

        # 2500-2750
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new=r3
        regA_new=regA
        reg_desti = r1
        r1=r3
        reg_desti_new = r1
        Port1_new=r1
        Port2_new=r4
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (3 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:,0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 2500-2750:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 2500, 2750, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new


        # 2750-3000
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r5, bitn)
        regB_new = r4
        regA_new = r1
        reg_desti = r1
        r1 = r1 ^ r4
        reg_desti_new = r1
        Port1_new = r2
        Port2_new = r1
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r1 >> (bitn - 1)
        Zflag_new = np.multiply(r1 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
           (regA << (3 * bitn)) ^(regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 2750-3000:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 2750, 3000, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        # 3000-3250
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r3, bitn)
            #XLeft = self.AddTerm(XLeft, r6, bitn)
        regB_new=r1
        regA_new=r2
        reg_desti = r2
        r2=r2^r1
        Nflag_new=r2>>(bitn-1)
        Zflag_new=np.multiply(r2==0,1)
        reg_desti_new = r2
        Port1_new=r1
        Port2_new=r1
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r2 >> (bitn - 1)
        Zflag_new = np.multiply(r2 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 3000-3250:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 3000, 3250, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new

        # 3250-3500
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r6, bitn)
        regB_new=r1
        regA_new=regA
        reg_desti = r1
        r1=bitmask^r1
        reg_desti_new = r1
        Port1_new=r6
        Port2_new=r2
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r1 >> (bitn - 1)
        Zflag_new = np.multiply(r1 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #
        #count = np.size(XSum, 1)
        #print('Cycle 3250-3500:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 3250, 3500, 10, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new


        # 3500-3750
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            #XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            #XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            #XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r4, bitn)
            XLeft = self.AddTerm(XLeft, r3, bitn)

        regB_new=r2
        regA_new=regA
        reg_desti = r6
        r6=r2
        reg_desti_new = r6
        Port1_new=r6
        Port2_new=r5

        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)

        #count = np.size(XSum, 1)
        #print('Cycle 3500-3750:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, 20000, 3500, 3750, 10, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new



        # 3750-4000
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        if(mode=='extend'):
            # Common
            #XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            #XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            #XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r4, bitn)
            XLeft = self.AddTerm(XLeft, r4^r6, bitn)
        regB_new = r5
        regA_new = r6
        reg_desti = r6
        r6 = r5&r6
        reg_desti_new = r6
        Port1_new = r3
        Port2_new = r6
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r6 >> (bitn - 1)
        Zflag_new = np.multiply(r6 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #
        #count = np.size(XSum, 1)
        #print('Cycle 3750-4000:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, 20000, 3750, 4000, 10, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        # 4000 - 4250
        XLeft=None
        XLoad=None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            #XLeft = self.AddTerm(XLeft, r1^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            #XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            #XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLoad= self.AddTerm(XLoad, r4, bitn)
            #XLeft = self.AddTerm(XLeft, r4 ^ r6, bitn)

        regB_new = r6
        regA_new = r3
        reg_desti = r3
        r3 = r3^r6
        reg_desti_new = r3
        Port1_new = r4
        Port2_new = r5
        Nflag=Nflag_new
        Zflag=Zflag_new
        Nflag_new=r3>>(bitn-1)
        Zflag_new=np.multiply(r3==0,1)

        [XExecute, count_e] = self.RegressionExtend(
          (regA << (3*bitn)) ^(regA_new << (2*bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))

        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 4000-4250:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 4000, 4250, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        #4250-4500
        XLeft=None
        XLoad=None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            #XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
           # XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            #XLoad= self.AddTerm(XLoad, r1, bitn)
        regB_new = r5
        regA_new = regA
        r4 = r5
        Port1_new = r1^r1
        Port2_new = r1
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (2 * bitn))  ^ (regB << bitn) ^ regB_new, (3 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        count = np.size(XSum, 1)
        print('Cycle 4250-4500:\n')
        print('Left {0} vars\n'.format(count))
        pv = self.FvLTest(trs, XSum, X, 20000, 4250, 4500, 5, filename="NestedF.txt")
        print('pv={0} \n'.format(pv))
        return ExpVar
    def MidoriPSimulator(self,trs,bitn,mode='standard'):
        #mode='standard': standard model without incorrect access/glitches
        #mode='extend': model with incorrect access/glitches
        #model='elmo': model with only Op1/Op2/Op1HD/Op2HD
        #model='hw' model with only Op2 HW
        bitmask=2**bitn-1
        r1=trs.plaintext[:, 0]&bitmask
        r2=trs.plaintext[:, 1]&bitmask
        r3=trs.plaintext[:, 2]&bitmask
        r4=trs.plaintext[:, 3]&bitmask
        r5=r1^r1# r6=0
        r6=r1^r1# r6=0
        X=r1^(r2<<bitn)^(r3.astype(dtype='uint16')<<(2*bitn))^(r4.astype(dtype='uint16')<<(3*bitn))
        ExpVar=[]

        #self.LRA_Fullbase(trs, r1^r2^r3^r4, 0, 2250, filename="LRA_Fullbase_r1234.txt")

        #self.LRA_Fullbase(trs, r1^r2, 0, 2250, filename="LRA_Fullbase_r1xr2.txt")
        #self.LRA_Fullbase(trs, r2^r3, 0, 2250, filename="LRA_Fullbase_r2xr3.txt")
        #self.LRA_Fullbase(trs, r3^r4, 0, 2250, filename="LRA_Fullbase_r3xr4.txt")
        #self.LRA_Fullbase(trs, r1^r3, 0, 2250, filename="LRA_Fullbase_r1xr3.txt")
        #self.LRA_Fullbase(trs, r1^r4, 0, 2250, filename="LRA_Fullbase_r1xr4.txt")
        #self.LRA_Fullbase(trs, r2^r4, 0, 2250, filename="LRA_Fullbase_r2xr4.txt")

        #self.LRA_Fullbase(trs, r1^r2^r3, 0, 2250, filename="LRA_Fullbase_r123.txt")
        #self.LRA_Fullbase(trs, r2^r3^r4, 0, 2250, filename="LRA_Fullbase_r234.txt")
        #self.LRA_Fullbase(trs, r1^r2^r4, 0, 2250, filename="LRA_Fullbase_r124.txt")
        #self.LRA_Fullbase(trs, r1^r3^r4, 0, 2250, filename="LRA_Fullbase_r134.txt")

        regB = r1^r1
        regA = r1^r1
        reg_desti_HD=r1^r1
        Port1 = r6
        Port2 = r6
        reg_desti=r1^r1
        reg_desti_new=r1^r1
        Zflag_new = r1 ^ r1
        Nflag_new = r1 ^ r1
        Zflag = r1 ^ r1
        Nflag = r1 ^ r1
        regB = r1 ^ r1
        regA = r1 ^ r1

        #0-250
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new = r1^r1
        regA_new = r1^r1
        reg_desti = r6
        r6= r1^r1#r6=0
        reg_desti_new = r6
        Port1_new = r5
        Port2_new = r1
        Nflag=Nflag_new
        Zflag=Zflag_new
        Nflag_new=r6>>(bitn-1)
        Zflag_new=np.multiply(r6==0,1)

        [XExecute, count_e] = self.RegressionExtend(
          (regA_new << (3*bitn)) ^(regA << (2*bitn))  ^ (regB_new << bitn)^regB, (4 * bitn))

        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)

        count = np.size(XSum, 1)
        #print('Cycle 0-250:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 0, 250, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))

        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        #250-500
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new = r1
        regA_new = r5
        reg_desti = r5
        r5= r5^r1
        reg_desti_new = r5
        Port1_new = r5
        Port2_new = r2
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r5 >> (bitn - 1)
        Zflag_new = np.multiply(r5 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA_new << (3 * bitn)) ^ (regA << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 250-500:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 250, 500, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        # 500-750
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new = r2
        regA_new = r5
        reg_desti = r5
        r5 = r5^r2
        reg_desti_new = r5
        Port1_new = r5
        Port2_new = r3
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r5 >> (bitn - 1)
        Zflag_new = np.multiply(r5 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
           (regA << (3 * bitn)) ^(regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        count = np.size(XSum, 1)
        #print('Cycle 500-750:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 500, 750, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        # 750-1000
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r2, bitn)
            XLeft = self.AddTerm(XLeft, r2^r4, bitn)
        regB_new = r3
        regA_new = r5
        reg_desti = r5
        r5 = r5 ^ r3
        reg_desti_new = r5
        Port1_new = r5
        Port2_new = r4
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r5 >> (bitn - 1)
        Zflag_new = np.multiply(r5 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))

        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 750-1000:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 750, 1000, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new


        # 1000-1250
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r2, bitn)
        regB_new = r4
        regA_new = r5
        reg_desti = r5
        r5 = r5^r4
        reg_desti_new = r5
        Port1_new = r1
        Port2_new = r5
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r5 >> (bitn - 1)
        Zflag_new = np.multiply(r5 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA_new << (3 * bitn))  ^(regA << (2 * bitn))  ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 1000-1250:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 1000, 1250, 5, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB = regB_new
        regA = regA_new
        Port1 = Port1_new
        Port2 = Port2_new

        # 1250-1500
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
        # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            #XLeft = self.AddTerm(XLeft, r3, bitn)
        regB_new=r5
        regA_new=r1
        reg_desti = r1
        r1=r5^r1
        reg_desti_new = r1
        Port1_new=r2
        Port2_new=r5
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r1 >> (bitn - 1)
        Zflag_new = np.multiply(r1 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))

        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)

        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 1250-1500:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 1250, 1500, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new


        # 1500-1750
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
        regB_new=r5
        regA_new=r2
        reg_desti = r2
        r2=r5^r2
        reg_desti_new = r2
        Port1_new=r3
        Port2_new=r5
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r2 >> (bitn - 1)
        Zflag_new = np.multiply(r2 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^ (regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))

        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 1500-1750:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 1500, 1750, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new

        # 1750-2000
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r2, bitn)
        regB_new=r5
        regA_new=r3
        reg_desti = r3
        r3=r3^r5
        reg_desti_new = r3
        Port1_new=r4
        Port2_new=r5
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r3 >> (bitn - 1)
        Zflag_new = np.multiply(r3 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA_new << (3 * bitn))^(regA << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 1750-2000:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 1750, 2000, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new

        # 2000-2250
        XLeft = None
        XLoad = None
        XLeft = self.AddTerm(XLeft, reg_desti, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, reg_desti ^ reg_desti_new, bitn)
        XLeft = self.AddTerm(XLeft, Zflag_new, 1)
        XLeft = self.AddTerm(XLeft, Nflag_new, 1)
        ##If last instruction updated CPSR
        XLeft = self.AddTerm(XLeft, Nflag, 1)
        XLeft = self.AddTerm(XLeft, Zflag, 1)
        XLeft = self.AddTerm(XLeft, Nflag ^ Nflag_new, 1)
        XLeft = self.AddTerm(XLeft, Zflag ^ Zflag_new, 1)
        if(mode=='extend'):
            # Common
            XLeft = self.AddTerm(XLeft, r1 ^ r2, bitn)
            XLeft = self.AddTerm(XLeft, r2 ^ r3, bitn)
            XLeft = self.AddTerm(XLeft, r3 ^ r4, bitn)
            XLeft = self.AddTerm(XLeft, r4 ^ r5, bitn)
            XLeft = self.AddTerm(XLeft, r5 ^ r6, bitn)
            # Incorrect Access
            XLeft = self.AddTerm(XLeft, r1, bitn)
            XLeft = self.AddTerm(XLeft, r1^r5, bitn)
        regB_new=r5
        regA_new=r4
        reg_desti = r4
        r4=r4^r5
        reg_desti_new = r4
        Port1_new=r1^r1
        Port2_new=r1^r1
        Nflag = Nflag_new
        Zflag = Zflag_new
        Nflag_new = r4 >> (bitn - 1)
        Zflag_new = np.multiply(r4 == 0, 1)
        [XExecute, count_e] = self.RegressionExtend(
            (regA << (3 * bitn)) ^(regA_new << (2 * bitn)) ^ (regB << bitn) ^ regB_new, (4 * bitn))
        XLoad = self.AddTerm(XLoad, Port1_new, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new, bitn)
        XLoad = self.AddTerm(XLoad, Port1_new ^ Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2_new ^ Port2, bitn)
        XLoad = self.AddTerm(XLoad, Port1, bitn)
        XLoad = self.AddTerm(XLoad, Port2, bitn)
        #
        XSum = np.hstack((XLoad, XExecute, XLeft))
        XSum = self.PCA(XSum)
        XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode == 'elmo'):
            XSum=None
            XSum=self.AddTerm(XSum, regA_new, bitn)
            XSum = self.AddTerm(XSum, regB_new, bitn)
            XSum = self.AddTerm(XSum, regB_new^regB, bitn)
            XSum = self.AddTerm(XSum, regA_new ^ regA, bitn)
            XSum = self.PCA(XSum)
            XSum = XSum[:, 0:np.linalg.matrix_rank(XSum)]
        if (mode=='hw'):
            XSum = None
            XSum = self.AddTerm(XSum, regB_new, bitn)
        ExpVar.append(XSum)
        #count = np.size(XSum, 1)
        #print('Cycle 2000-2250:\n')
        #print('Left {0} vars\n'.format(count))
        #pv = self.FvLTest(trs, XSum, X, N, 2000, 2250, 20, filename="NestedF.txt")
        #print('pv={0} \n'.format(pv))
        regB=regB_new
        regA=regA_new
        Port1=Port1_new
        Port2=Port2_new

        return ExpVar
    def autoRegression(self,trs,ExpVar,bitn, drift,cv_start,filename,N,cycle_len):
        bitmask = 2 ** bitn - 1
        r1 = trs.plaintext[:, 0] & bitmask
        r2 = trs.plaintext[:, 1] & bitmask
        r3 = trs.plaintext[:, 2] & bitmask
        r4 = trs.plaintext[:, 3] & bitmask
        X = r1 ^ (r2 << bitn) ^ (r3.astype(dtype='uint16') << (2 * bitn)) ^ (r4.astype(dtype='uint16') << (3 * bitn))
        for i in range(cycle_len):
            print('Cycle {0}-{1}:\n'.format(250*i,250*(i+1)))
            ##drifting begining
            if(i==0):
                Ev = ExpVar[i]
                pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i, 250 * i + drift,cv_start, filename,mode='create')
            else:
                Ev = np.hstack((ExpVar[i-1], ExpVar[i]))
                Ev = self.PCA(Ev)
                Ev = Ev[:, 0:np.linalg.matrix_rank(Ev)]
                pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i, 250 * i+drift,cv_start, filename,mode='append')
            ##Current cycle
            Ev=ExpVar[i]
            print('Left {0} vars\n'.format(np.size(Ev, 1)))
            pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i+drift,250*(i+1)-drift,cv_start, filename,mode='append')
            print('max_pv={0} \n'.format(pv))
            ##drifting ending
            if (i == cycle_len-1):
                Ev = ExpVar[i]
            else:
                Ev = np.hstack((ExpVar[i], ExpVar[i+1]))
                Ev = self.PCA(Ev)
                Ev = Ev[:, 0:np.linalg.matrix_rank(Ev)]
            pv = self.FvLTest_Details(trs, Ev, X, N, 250*(i+1)-drift, 250*(i+1),cv_start, filename,mode='append')
    def autoRegression_5bit(self,trs,ExpVar,bitn, drift,cv_start,filename,N,cycle_len):
        bitmask = 2 ** bitn - 1
        r1 = trs.plaintext[:, 0] & bitmask
        r2 = trs.plaintext[:, 1] & bitmask
        r3 = trs.plaintext[:, 2] & bitmask
        r4 = trs.plaintext[:, 3] & bitmask
        r5 = trs.plaintext[:, 4] & bitmask
        X = r1 ^ (r2 << bitn) ^ (r3.astype(dtype='uint16') << (2 * bitn)) ^ (r4.astype(dtype='uint16') << (3 * bitn))^ (r5.astype(dtype='uint16') << (4 * bitn))
        for i in range(cycle_len):
            print('Cycle {0}-{1}:\n'.format(250*i,250*(i+1)))
            ##drifting begining
            if(i==0):
                Ev = ExpVar[i]
                pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i, 250 * i + drift,cv_start, filename,mode='create')
            else:
                Ev = np.hstack((ExpVar[i-1], ExpVar[i]))
                Ev = self.PCA(Ev)
                Ev = Ev[:, 0:np.linalg.matrix_rank(Ev)]
                pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i, 250 * i+drift,cv_start, filename,mode='append')
            ##Current cycle
            Ev=ExpVar[i]
            print('Left {0} vars\n'.format(np.size(Ev, 1)))
            pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i+drift,250*(i+1)-drift,cv_start, filename,mode='append')
            print('max_pv={0} \n'.format(pv))
            ##drifting ending
            if (i == cycle_len-1):
                Ev = ExpVar[i]
            else:
                Ev = np.hstack((ExpVar[i], ExpVar[i+1]))
                Ev = self.PCA(Ev)
                Ev = Ev[:, 0:np.linalg.matrix_rank(Ev)]
            pv = self.FvLTest_Details(trs, Ev, X, N, 250*(i+1)-drift, 250*(i+1),cv_start, filename,mode='append')
    def autoRegression_general(self,trs,X,ExpVar,bitn, drift,cv_start,filename,N,cycle_len):
        for i in range(cycle_len):
            print('Cycle {0}-{1}\n'.format(250*i,250*(i+1)))
            ##drifting begining
            if(i==0):
                Ev = ExpVar[i]
                pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i, 250 * i + drift,cv_start, filename,mode='create')
            else:
                Ev = np.hstack((ExpVar[i-1], ExpVar[i]))
                Ev = self.PCA(Ev)
                Ev = Ev[:, 0:np.linalg.matrix_rank(Ev)]
                pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i, 250 * i+drift,cv_start, filename,mode='append')
            ##Current cycle
            Ev=ExpVar[i]
            print('Left {0} vars\n'.format(np.size(Ev, 1)))
            pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i+drift,250*(i+1)-drift,cv_start, filename,mode='append')
            print('max_pv={0} \n'.format(pv))
            ##drifting ending
            if (i == cycle_len-1):
                Ev = ExpVar[i]
            else:
                Ev = np.hstack((ExpVar[i], ExpVar[i+1]))
                Ev = self.PCA(Ev)
                Ev = Ev[:, 0:np.linalg.matrix_rank(Ev)]
            pv = self.FvLTest_Details(trs, Ev, X, N, 250*(i+1)-drift, 250*(i+1),cv_start, filename,mode='append')
    def PTransRegression(self,trs,ExpVar,bitn, drift,cv_start,filename,N):
        bitmask = 2 ** bitn - 1
        r1 = trs.plaintext[:, 0] & bitmask
        r2 = trs.plaintext[:, 1] & bitmask
        r3 = trs.plaintext[:, 2] & bitmask
        r4 = trs.plaintext[:, 3] & bitmask
        X = r1 ^ (r2 << bitn) ^ (r3.astype(dtype='uint16') << (2 * bitn)) ^ (r4.astype(dtype='uint16') << (3 * bitn))
        for i in range(9):
            print('Cycle {0}-{1}:\n'.format(250*i,250*(i+1)))
            ##drifting begining
            if(i==0):
                Ev = ExpVar[i]
                pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i, 250 * i + drift,cv_start, filename,mode='create')
            else:
                Ev = np.hstack((ExpVar[i-1], ExpVar[i]))
                Ev = self.PCA(Ev)
                Ev = Ev[:, 0:np.linalg.matrix_rank(Ev)]
                pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i, 250 * i+drift,cv_start, filename,mode='append')
            ##Current cycle
            Ev=ExpVar[i]
            print('Left {0} vars\n'.format(np.size(Ev, 1)))
            pv = self.FvLTest_Details(trs, Ev, X, N, 250 * i+drift,250*(i+1)-drift,cv_start, filename,mode='append')
            print('max_pv={0} \n'.format(pv))
            ##drifting ending
            if (i == 8):
                Ev = ExpVar[i]
            else:
                Ev = np.hstack((ExpVar[i], ExpVar[i+1]))
                Ev = self.PCA(Ev)
                Ev = Ev[:, 0:np.linalg.matrix_rank(Ev)]
            pv = self.FvLTest_Details(trs, Ev, X, N, 250*(i+1)-drift, 250*(i+1),cv_start, filename,mode='append')

# Tools for aligning the captured traces and simulation verification
    def ExportInputs_GiftSbox(self,trsname,randname):# write the used random data in the trace set to the input of ELMO
        trs = TRS_Reader.TRS_Reader(
               trsname)
        trs.read_header()
        N = trs.Number_of_Traces
        trs.read_traces(N,0,100)# does not matter here
        f=open(randname,'w')
        f1 = open("outputs.txt", 'w')
        for i in range(N):
            f.writelines("{0:2x}\n".format(trs.plaintext[i][0]))
            f.writelines("{0:2x}\n".format( trs.plaintext[i][1]))
            f.writelines("{0:2x}\n".format(trs.plaintext[i][2]))
            f.writelines("{0:2x}\n".format(trs.plaintext[i][3]))
            f.writelines("{0:2x}\n".format( trs.plaintext[i][4]))
            f.writelines("0\n")
            f1.writelines("{0:2x}\n".format( trs.ciphertext[i][0]))
            f1.writelines("{0:2x}\n".format(trs.ciphertext[i][1]))
            f1.writelines("{0:2x}\n".format( trs.ciphertext[i][2]))
            f1.writelines("{0:2x}\n".format( trs.ciphertext[i][3]))
            f1.writelines("0\n")
        f.close()
        f1.close()
    def ExportInputs_MidoriP(self,trsname,randname):# write the used random data in the trace set to the input of ELMO
        trs = TRS_Reader.TRS_Reader(
               trsname)
        trs.read_header()
        N = trs.Number_of_Traces
        trs.read_traces(N,0,100)# does not matter here
        f=open(randname,'w')
        f1 = open("outputs.txt", 'w')
        for i in range(N):
            f.writelines("{0:2x}\n".format(trs.plaintext[i][0]))
            f.writelines("{0:2x}\n".format( trs.plaintext[i][1]))
            f.writelines("{0:2x}\n".format(trs.plaintext[i][2]))
            f.writelines("{0:2x}\n".format(trs.plaintext[i][3]))
            f.writelines("{0:2x}\n".format( trs.plaintext[i][4]))
            f.writelines("0\n")
            f1.writelines("{0:2x}\n".format( trs.ciphertext[i][0]))
            f1.writelines("{0:2x}\n".format(trs.ciphertext[i][1]))
            f1.writelines("{0:2x}\n".format( trs.ciphertext[i][2]))
            f1.writelines("{0:2x}\n".format( trs.ciphertext[i][3]))
            f1.writelines("0\n")
        f.close()
        f1.close()
    def ExportInputs_ISWd2(self,trsname,randname):# write the used random data in the trace set to the input of ELMO
        trs = TRS_Reader.TRS_Reader(
               trsname)
        trs.read_header()
        N = trs.Number_of_Traces
        trs.read_traces(N,0,100)# does not matter here
        f=open(randname,'w')
        f1 = open("outputs.txt", 'w')
        for i in range(N):
            f.writelines("{0:2x}\n".format(trs.plaintext[i][0]))
            f.writelines("{0:2x}\n".format( trs.plaintext[i][1]))
            f.writelines("{0:2x}\n".format(trs.plaintext[i][2]))
            f.writelines("{0:2x}\n".format(trs.plaintext[i][3]))
            f.writelines("{0:2x}\n".format( trs.plaintext[i][4]))
            f.writelines("0\n")
            f1.writelines("{0:2x}\n".format( trs.ciphertext[i][0]))
            f1.writelines("{0:2x}\n".format(trs.ciphertext[i][1]))
            f1.writelines("{0:2x}\n".format( trs.ciphertext[i][2]))
            f1.writelines("{0:2x}\n".format( trs.ciphertext[i][3]))
            f1.writelines("0\n")
        f.close()
        f1.close()
    def ExportInputs_MaskedAES_Sbox(self,trsname,randname):
        trs = TRS_Reader.TRS_Reader(
               trsname)
        trs.read_header()
        N = trs.Number_of_Traces
        trs.read_traces(N,0,100)# does not matter here
        f=open(randname,'w')
        for i in range(N):
            for j in range(18):
                f.writelines("{0:2x}\n".format(trs.plaintext[i][j]))
        f.close()
    def ReadLeakyStates(self, leakyfilename,headerfile,N,start=0,limit=None):
        self.lsReader = LeakyStateReader.LeakyStateReader(leakyfilename)
        self.lsReader.ReadInstrHeader()
        self.lsReader.PrintInstrHeader(headerfile)
        self.lsReader.ReadTraces(N,start,limit)
    def GenRegressionBasis_OneSample(self,sampleno, randbit):#Generate the regression for sampleno, randbit defines how many bits are considered in 32 bits
        bitmask=2**randbit-1
        Sample=self.lsReader.Samples[sampleno]
        Termcount=len(Sample.Terms)
        ExpVars=None
        for tind in range(Termcount):
            term=Sample.Terms[tind]

            X=np.array(term.data)
            #Check if X is constant
            if(np.all(X == X[0, :])):#constant
                continue;
            datalen=X.shape[1]
            Xt=np.zeros((X.shape[0]),dtype='uint32')
            datalen=math.ceil(datalen/4)
            if("bus" in term.disp or "buffer" in term.disp):

                if ("Readbus HD" in term.disp):
                    #datalen = 16
                    #Xt = Xt ^ ((X[:, 0] & 0xff) << (0 * randbit)) ^ ((X[:, 1] & 0xff) << (4 * randbit)) ^ (
                    #            (X[:, 2] & 0xff) << (8 * randbit)) ^ ((X[:, 3] & 0xff) << (12 * randbit))
                    for i in range(datalen):
                        Xt=Xt^((X[:,i*4]&bitmask)<<(i*randbit))
                else:
                    #datalen = 4
                    #Xt = Xt ^ ((X[:, 0] & bitmask) << (0*randbit))^ ((X[:, 1] & bitmask) << (1*randbit))^ ((X[:, 2] & bitmask) << (2*randbit))^ ((X[:, 3] & bitmask) << (3*randbit))
                    for i in range(datalen):
                        Xt=Xt^((X[:,i*4]&bitmask)<<(i*randbit))
            else:
                for i in range(datalen):
                    if('CPSR' not in term.disp):
                        Xt=Xt^((X[:,i*4]&bitmask)<<(i*randbit))
                    else:# CPSR takes the high regs
                        Xt=Xt^(((X[:,i*4+3]>>4)&0x0f)<<(i*randbit))
            #if ('Neighbour' in term.disp):
            #    continue;
            if(term.type==0):#Full
                [X,count]=self.RegressionExtend(Xt, randbit*datalen, Terms=None, Linear=None, bit=randbit)
                if (ExpVars is None):
                    ExpVars = X
                else:
                    ExpVars = np.hstack((X[:,1:X.shape[1]], ExpVars))
            else:
                if('CPSR' not in term.disp):
                    ExpVars=self.AddTerm(ExpVars,Xt,randbit*datalen)
                else:
                    ExpVars=self.AddTerm(ExpVars,Xt,4)
        #the end
        if(ExpVars is None):
            print("Current cycle is not data-dependent!")
            return np.ones(X[:,0].size)
        ExpVars=self.PCA(ExpVars)
        ExpVars = ExpVars[:, 0:np.linalg.matrix_rank(ExpVars)]
        return ExpVars
    def Regression_OneSample(self,trs,cycle_no,ExpVar,bitn,drift,cv_start,filename,N):
        bitmask = 2 ** bitn - 1
        r1 = trs.plaintext[:, 0] & bitmask
        r2 = trs.plaintext[:, 1] & bitmask
        r3 = trs.plaintext[:, 2] & bitmask
        r4 = trs.plaintext[:, 3] & bitmask
        X = r1 ^ (r2 << bitn) ^ (r3.astype(dtype='uint16') << (2 * bitn)) ^ (r4.astype(dtype='uint16') << (3 * bitn))
        print('Cycle {0}-{1}:\n'.format(250 * cycle_no, 250 * (cycle_no + 1)))
        pv = self.FvLTest(trs, ExpVar, X, N, 250 * cycle_no+drift, 250 * (cycle_no+1)-drift, 200, filename)
        print('max_pv={0} \n'.format(pv))
    def Regression_OneSample_ISWd2(self,trs,cycle_no,ExpVar,bitn,drift,cv_start,filename,N):
        bitmask = 2 ** bitn - 1
        a1 = trs.plaintext[:, 0] & bitmask
        a2 = trs.plaintext[:, 1] & bitmask
        b1 = trs.plaintext[:, 2] & bitmask
        b2 = trs.plaintext[:, 3] & bitmask
        r = trs.plaintext[:, 4] & bitmask
        X = a1 ^ (a2 << bitn) ^ (b1.astype(dtype='uint16') << (2 * bitn)) ^ (b2.astype(dtype='uint16') << (3 * bitn))^ (r.astype(dtype='uint16') << (4 * bitn))
        print('Cycle {0}-{1}:\n'.format(250 * cycle_no, 250 * (cycle_no + 1)))
        pv = self.FvLTest(trs, ExpVar, X, N, 250 * cycle_no, 250 * (cycle_no+1), 200, filename)
        print('max_pv={0} \n'.format(pv))

# Model evaluation for GiftSbox
    def GiftSbox_manual_evaluation(self):
        drift = 30
        cv_start = 20000
        trs = TRS_Reader.TRS_Reader(
            "SboxFtest_5000Samples_Rand2.trs")
        trs.read_header()
        N = 20000
        trs.read_traces(N, 0, 4500)  # does not matter here
        r1=trs.ciphertext[:,0]&0x3
        r2 = trs.ciphertext[:,1] & 0x3
        #self.LRA_Fullbase(trs, r1^r2, 3500, 4500, filename="LRA_Fullbase_r12.txt")
        #self.LRA_Fullbase(trs, r1, 3500, 4500, filename="LRA_Fullbase_r1.txt")
        #self.LRA_Fullbase(trs, r2, 3500, 4500, filename="LRA_Fullbase_r2.txt")
        #ExpVar = self.SboxSimulator(trs, 2, mode='standard')
        #self.SboxRegression(trs, ExpVar, 2, drift, cv_start, "Sbox_Ftest_Ori_20k_standard.txt",N)
        ExpVar = self.SboxSimulator(trs, 2, mode='extend')
        self.Regression_OneSample(trs, 8, ExpVar[8], 2, drift, cv_start, "F-test.txt", N)
        self.SboxRegression(trs, ExpVar, 2, drift, cv_start, "Sbox_Ftest_Ori_20k_extend.txt",N)
        ExpVar = self.SboxSimulator(trs, 2, mode='elmo')
        self.SboxRegression(trs, ExpVar, 2, drift, cv_start, "Sbox_Ftest_Ori_20k_elmo.txt",N)
        ExpVar = self.SboxSimulator(trs, 2, mode='hw')
        self.SboxRegression(trs, ExpVar, 2, drift, cv_start, "Sbox_Ftest_Ori_20k_hw.txt",N)
    def GiftSbox_auto_evaluation(self,tracefilename,leakystate_filename,header_filename,drift,cv_start):
        trs = TRS_Reader.TRS_Reader(
            tracefilename)
        trs.read_header()
        N = 40000
        trs.read_traces(N, 0, 4500)  # does not matter here
        print("Read leaky states\n")
        self.ReadLeakyStates(
            leakystate_filename,
            header_filename, N)
        Expvar=[]
        print("Analysing leaky states\n")
        for cycle_no in range(3,21):
            print("Cycle {0}\n".format(cycle_no))
            Expvar_sample = self.GenRegressionBasis_OneSample(cycle_no, randbit)
            Expvar.append(Expvar_sample)
        self.autoRegression(trs, Expvar, 2, drift, cv_start, "GiftSbox_Ftest_Auto_Board0.txt",N,18)
    def MidoriP_auto_evaluation(self,tracefilename,leakystate_filename,header_filename,drift,cv_start,outfile):
        trs = TRS_Reader.TRS_Reader(
            tracefilename)
        trs.read_header()
        N = 40000
        trs.read_traces(N, 0, 2500)  # does not matter here
        print("Read leaky states\n")
        self.ReadLeakyStates(
            leakystate_filename,
            header_filename, N)
        Expvar=[]
        print("Analysing leaky states\n")
        for cycle_no in range(3,12):
            print("Cycle {0}\n".format(cycle_no))
            Expvar_sample = self.GenRegressionBasis_OneSample(cycle_no, randbit)
            Expvar.append(Expvar_sample)
        self.autoRegression(trs, Expvar, 2, drift, cv_start, outfile,N,9)
    def ISWd2_auto_evaluation(self,tracefilename,leakystate_filename,header_filename,drift,cv_start,outfile):
        trs = TRS_Reader.TRS_Reader(
            tracefilename)
        trs.read_header()
        N = 50000
        trs.read_traces(N, 750, 3250+250*6)  # does not matter here
        #Terms = self.Model2Terms(0x0117, 4)
        #[XL, count] = self.RegressionExtend((x16 ^ x15) ^ ((x12 ^ x11) << 2) ^ ((x8 ^ x7) << 4) ^ ((x4 ^ x3) << 6), 8,
        #                                    Terms)
        #a1 = (trs.plaintext[:, 0]) & 0x03
        #a2 = (trs.plaintext[:, 1]) & 0x03
        #b1 = (trs.plaintext[:, 2]) & 0x03
        #b2 = (trs.plaintext[:, 3]) & 0x03
        #r = (trs.plaintext[:, 4]) & 0x03
        #self.LRA_Fullbase(trs,a1,0,7000,"LRA_a1.txt")
        #self.LRA_Fullbase(trs,a2,0,7000,"LRA_a2.txt")
        #self.LRA_Fullbase(trs,b1,0,7000,"LRA_b1.txt")
        #self.LRA_Fullbase(trs,b2,0,7000,"LRA_b2.txt")
        #self.LRA_Fullbase(trs,r,0,7000,"LRA_r.txt")
        #self.LRA_Fullbase(trs,r^a1,0,7000,"LRA_rxa1.txt")
        #self.LRA_Fullbase(trs,b1^b2,0,500,"LRA_r3xr4.txt")
        #self.LRA_Fullbase(trs,r^b2,0,500,"LRA_r4xr5.txt")
        #self.LRA_Fullbase(trs,(a1&b1)^(a1&b2)&(a2&b1),0,500,"LRA_r5xr6.txt")
        #self.LRA_Fullbase(trs,b1^a2,0,7000,"LRA_b1xa2.txt")
        #self.LRA_Fullbase(trs,b2^a2,0,7000,"LRA_b2xa2.txt")
        #self.LRA(trs, XL, 8, 0, 5500, "LRA_xHD_linear.txt")
        print("Read leaky states\n")
        self.ReadLeakyStates(
            leakystate_filename,
            header_filename, N)
        Expvar=[]
        print("Analysing leaky states\n")
        for cycle_no in range(5,21):
            print("Cycle {0}\n".format(cycle_no))
            Expvar_sample = self.GenRegressionBasis_OneSample(cycle_no, randbit)
            Expvar.append(Expvar_sample)
        self.autoRegression_5bit(trs, Expvar, 2, drift, cv_start, outfile,N,16)
        # no=25
        #Expvar_sample = self.GenRegressionBasis_OneSample(no, 2)
        #print("Instr={0}".format(self.lsReader.Samples[no].inst))
        #self.Regression_OneSample_ISWd2(trs,0, Expvar_sample,2, drift, cv_start, "F-test.txt", N)
    def ADK_auto_evaluation(self,tracefilename,leakystate_filename,header_filename,drift,cv_start,outfile):
        trs = TRS_Reader.TRS_Reader(
            tracefilename)
        trs.read_header()
        N =50000
        print("Read leaky states\n")
        #self.ReadLeakyStates(
        #    leakystate_filename,
        #    header_filename, N,23,44)
        trs.read_traces(N,9000,9250)  # does not matter here
        bitn=randbit
        bitmask = 2 ** bitn - 1
        U = trs.plaintext[:, 16] & bitmask
        V = trs.plaintext[:, 17] & bitmask
        x1 = trs.plaintext[:, 0] & bitmask
        x2 = trs.plaintext[:, 1] & bitmask
        x3 = trs.plaintext[:, 2] & bitmask
        x4 = trs.plaintext[:, 3] & bitmask
        x7=trs.plaintext[:, 6] & bitmask
        x8=trs.plaintext[:, 7] & bitmask
        x11=trs.plaintext[:, 10] & bitmask
        x12=trs.plaintext[:, 11] & bitmask
        x15=trs.plaintext[:, 14] & bitmask
        x16=trs.plaintext[:, 15] & bitmask
        x1=x1^U
        x2 = x2 ^ U
        x3 = x3 ^ U
        x4 = x4 ^ U
        X = x2 ^ (x1 << bitn) ^ (V.astype(dtype='uint16') << (2 * bitn)) ^ (x4.astype(dtype='uint16') << (3 * bitn))^ (x3.astype(dtype='uint16') << (4 * bitn))
        Terms = self.Model2Terms(0x00f7, 4)
        [XL, count] = self.RegressionExtend(X, 8, Terms)
        pv = self.FvLTest(trs, XL, X,  N,0, 250, 100,"F-test.txt")
        print('pv={0} \n'.format(pv))
        #self.LRA_Fullbase(trs,x1,0,5000,"LRA_x1.txt");
        #self.LRA_Fullbase(trs,x2,0,5000,"LRA_x2.txt");
        #self.LRA_Fullbase(trs,V,0,5000,"LRA_V.txt");
        #self.LRA_Fullbase(trs,x1^V,0,5000,"LRA_x1V.txt");
        #self.LRA_Fullbase(trs,x2^V,0,5000,"LRA_x2V.txt");
        #self.LRA_Fullbase(trs,x1^x2^V,0,5000,"LRA_x1x2V.txt");
        #self.LRA_Fullbase(trs,x1^x2,0,5000,"LRA_x1x2.txt");
        #XL=self.AddTerm(None,x1^x2,2);
        #self.LRA(trs,XL,2,0,5000,"LRA_x1x2_linear.txt")
        #self.LRA_Fullbase(trs, (x16 ^ x12) ^ ((x12 ^ x8) << 2) ^ ((x8 ^ x4) << 4) , 0, 5500,
        #                  "LRA_int.txt");
        #self.LRA_Fullbase(trs,x12^U,0,5500,"LRA_x12.txt");
        #self.LRA_Fullbase(trs,x16^U,0,5500,"LRA_x16.txt");
        #self.LRA_Fullbase(trs,x7^U,0,5500,"LRA_x7.txt");
        #self.LRA_Fullbase(trs,x11^U,0,5500,"LRA_x11.txt");
        #self.LRA_Fullbase(trs,x15^U,0,5500,"LRA_x15.txt");
        #self.LRA_Fullbase(trs,x3,0,5500,"LRA_x3.txt");
        #self.LRA_Fullbase(trs,x4^V,0,5500,"LRA_x4UV.txt");
        #self.LRA_Fullbase(trs,V,0,5500,"LRA_V.txt");
        #Expvar=[]
        #print("Analysing leaky states\n")
        #for cycle_no in range(23,44):
        #    print("Cycle {0}: {1}\n".format(cycle_no+1,self.lsReader.Samples[cycle_no].inst))
        #    Expvar_sample = self.GenRegressionBasis_OneSample(cycle_no, randbit)
        #    Expvar.append(Expvar_sample)
        #self.autoRegression_general(trs, X,Expvar, bitn, drift, cv_start, outfile,N,21)
    def ShiftRow_auto_evaluation(self,tracefilename,leakystate_filename,header_filename,drift,cv_start,outfile):
        trs = TRS_Reader.TRS_Reader(
            tracefilename)
        trs.read_header()
        N =50000
        print("Read leaky states\n")
        self.ReadLeakyStates(
            leakystate_filename,
            header_filename, N)
        trs.read_traces(N,750,4250)  # does not matter here
        bitn=randbit
        bitmask = 2 ** bitn - 1
        U = trs.plaintext[:, 16] & bitmask
        V = trs.plaintext[:, 17] & bitmask
        x1 = trs.plaintext[:, 0] & bitmask
        x2 = trs.plaintext[:, 1] & bitmask
        x3 = trs.plaintext[:, 2] & bitmask
        x4 = trs.plaintext[:, 3] & bitmask
        x6 = trs.plaintext[:, 5] & bitmask
        x11 = trs.plaintext[:, 10] & bitmask
        x16 = trs.plaintext[:, 15] & bitmask
        x1=x1^U^V
        x2 = x2 ^ U^V
        x3 = x3 ^ U^V
        x4 = x4 ^ U^V
        x6 = x6 ^ U^V
        x11 = x11 ^ U^V
        x16 = x16 ^ U^V
        X = x2 ^ (x3 << bitn)  ^ (x4.astype(dtype='uint16') << (2 * bitn))^ (x1.astype(dtype='uint16') << (3 * bitn))^ (U.astype(dtype='uint16') << (4 * bitn))^ (V.astype(dtype='uint16') << (5 * bitn))
        #Terms = self.Model2Terms(0x0057, 4)
        #[XL, count] = self.RegressionExtend(X, 8, Terms)
        #pv = self.FvLTest(trs, XL, X,  N,0, 250, 100,"F-test.txt")
        #print('pv={0} \n'.format(pv))
        #self.LRA_Fullbase(trs,x1,0,5000,"LRA_x1.txt");
        #self.LRA_Fullbase(trs,x2,0,5000,"LRA_x2.txt");
        #self.LRA_Fullbase(trs,x3,0,5000,"LRA_x3.txt");
        #self.LRA_Fullbase(trs,x4,0,5000,"LRA_x4.txt");
        #self.LRA_Fullbase(trs,x1^x2,0,5000,"LRA_x1x2.txt");
        #self.LRA_Fullbase(trs,x2^x3,0,5000,"LRA_x2x3.txt");
        #self.LRA_Fullbase(trs,x3^x4,0,5000,"LRA_x3x4.txt");
        #self.LRA_Fullbase(trs,x2^x6,0,5000,"LRA_x2x6.txt");
        #self.LRA_Fullbase(trs,x3^x11,0,5000,"LRA_x3x11.txt");
        #self.LRA_Fullbase(trs,x4^x16,0,5000,"LRA_x4x16.txt");
        Expvar=[]
        print("Analysing leaky states\n")
        for cycle_no in range(4,18):
            print("Cycle {0}: {1}\n".format(cycle_no+1,self.lsReader.Samples[cycle_no].inst))
            Expvar_sample = self.GenRegressionBasis_OneSample(cycle_no, randbit)
            Expvar.append(Expvar_sample)
        self.autoRegression_general(trs, X,Expvar, bitn, drift, cv_start, outfile,N,14)
    def MixColumn_auto_evaluation(self,tracefilename,leakystate_filename,header_filename,drift,cv_start,outfile):
        trs = TRS_Reader.TRS_Reader(
            tracefilename)
        trs.read_header()
        N =50000
        print("Read leaky states\n")
        self.ReadLeakyStates(
            leakystate_filename,
            header_filename, N,0,20)
        trs.read_traces(N,1500,5000)  # does not matter here
        bitn=randbit
        bitmask = 2 ** bitn - 1
        U = trs.plaintext[:, 16] & bitmask
        V = trs.plaintext[:, 17] & bitmask
        x1 = trs.plaintext[:, 0] & bitmask
        x2 = trs.plaintext[:, 1] & bitmask
        x3 = trs.plaintext[:, 2] & bitmask
        x4 = trs.plaintext[:, 3] & bitmask
        x6 = trs.plaintext[:, 5] & bitmask
        x11 = trs.plaintext[:, 10] & bitmask
        x16 = trs.plaintext[:, 15] & bitmask
        x1=x1^U
        x2 = x2 ^ U
        x3 = x3 ^ U
        x4 = x4 ^ U
        X = x2 ^ (x3 << bitn)  ^ (x4.astype(dtype='uint16') << (2 * bitn))^ (x1.astype(dtype='uint16') << (3 * bitn))^ (U.astype(dtype='uint16') << (4 * bitn))^ (V.astype(dtype='uint16') << (5 * bitn))
        #Terms = self.Model2Terms(0x0057, 4)
        #[XL, count] = self.RegressionExtend(X, 8, Terms)
        #pv = self.FvLTest(trs, XL, X,  N,0, 250, 100,"F-test.txt")
        #print('pv={0} \n'.format(pv))
        #self.LRA_Fullbase(trs,x1,0,5000,"LRA_x1.txt");
        #self.LRA_Fullbase(trs,x2,0,5000,"LRA_x2.txt");
        #self.LRA_Fullbase(trs,x3,0,5000,"LRA_x3.txt");
        #self.LRA_Fullbase(trs,x4,0,5000,"LRA_x4.txt");
        #self.LRA_Fullbase(trs,x1^x2,0,5000,"LRA_x1x2.txt");
        #self.LRA_Fullbase(trs,x2^x3,0,5000,"LRA_x2x3.txt");
        #self.LRA_Fullbase(trs,x3^x4,0,5000,"LRA_x3x4.txt");
        #self.LRA_Fullbase(trs,x2^x6,0,5000,"LRA_x2x6.txt");
        #self.LRA_Fullbase(trs,x3^x11,0,5000,"LRA_x3x11.txt");
        #self.LRA_Fullbase(trs,x4^x16,0,5000,"LRA_x4x16.txt");
        Expvar=[]
        print("Analysing leaky states\n")
        for cycle_no in range(6,20):
            print("Cycle {0}: {1}\n".format(cycle_no+1,self.lsReader.Samples[cycle_no].inst))
            Expvar_sample = self.GenRegressionBasis_OneSample(cycle_no, randbit)
            Expvar.append(Expvar_sample)
        self.autoRegression_general(trs, X,Expvar, bitn, drift, cv_start, outfile,N,14)
    global sbox
    sbox = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,#0
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,#1
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,#2
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,#3
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,#4
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,#5
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,#6
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
    def Sbox(self,x):
        for i in range(len(x)):
            x[i]=sbox[int(x[i])]
        return x
    def Sbox_auto_evaluation(self,tracefilename,leakystate_filename,header_filename,drift,cv_start,outfile):
        trs = TRS_Reader.TRS_Reader(
            tracefilename)
        trs.read_header()
        N = trs.Number_of_Traces
        #N=1000
        trs.read_traces(N, 4750,8750)  # does not matter here
        print("Read leaky states\n")
        self.ReadLeakyStates(
            leakystate_filename,
            header_filename, N,19,35)
        bitn=randbit
        bitmask = 2 ** bitn - 1
        U = trs.plaintext[:, 16] & bitmask
        V = trs.plaintext[:, 17] & bitmask
        x15 = trs.plaintext[:, 15] & bitmask
        x11 = trs.plaintext[:, 11] & bitmask
        x7 = trs.plaintext[:, 7] & bitmask
        x3 = trs.plaintext[:, 3] & bitmask
        x15 = x15 ^ U ^ V
        x11 = x11 ^U^V
        x7 = x7 ^U^V
        x3 = x3 ^U^V
        s15=trs.ciphertext[:,15]^trs.ciphertext[:,16]^trs.ciphertext[:,17]

        X = x15 ^ (x11.astype(dtype='uint16') << (1 * bitn))^ (x7.astype(dtype='uint16') << (2 * bitn))^ (x3.astype(dtype='uint16') << (3 * bitn))^ (U.astype(dtype='uint16') << (4 * bitn))^ (V.astype(dtype='uint16') << (5 * bitn))
        #X1 = x15 ^ (V.astype(dtype='uint16') << (1 * bitn)) ^ (x11.astype(dtype='uint16') << (2 * bitn))
        #X2 = x15 ^ (x7.astype(dtype='uint16') << (1 * bitn)) ^ (V.astype(dtype='uint16') << (2 * bitn))
        #X3 = x15 ^ (x3.astype(dtype='uint16') << (1 * bitn)) ^ (V.astype(dtype='uint16') << (2 * bitn))
        #Terms = self.Model2Terms(0xffff, 4)
        #[XL, count] = self.RegressionExtend(X, 8, Terms)
        #[XL1, count] = self.RegressionExtend(X1, 6, self.Model2Terms(0xff, 3))
        #[XL2, count] = self.RegressionExtend(X2, 6, self.Model2Terms(0xff, 3))
        #[XL3, count] = self.RegressionExtend(X3, 6, self.Model2Terms(0xff, 3))
        #XL = np.hstack((XL, XL1, XL2, XL3))
        #XL = self.AddTerm(XL,V,2)
        #XL = self.AddTerm(XL,x15^V^x7,2)
        #XL = self.AddTerm(XL, s15^x7^(x7<<2)^(x7<<4)^(x7<<6)^0xA6, 8)
        #pv = self.FvLTest(trs, XL, X,  N,0, 250, 100,"F-test.txt")
        #print('pv={0} \n'.format(pv))
        #self.LRA_Fullbase(trs, x15, 0, 9000, "LRA_x15.txt")
        #self.LRA_Fullbase(trs, x15^V, 0, 9000, "LRA_x15_MaskedSboxOut.txt")
        #self.LRA_Fullbase(trs,x15^x11,0,9000,"LRA_x15x11.txt")
        #self.LRA_Fullbase(trs, V, 0, 9000, "LRA_x11_MaskedSboxHD.txt")
        #self.LRA_Fullbase(trs, x11, 0, 9000, "LRA_x11.txt")
        #self.LRA_Fullbase(trs, x11^V, 0, 9000, "LRA_x11_MaskedSboxOut.txt")
        #self.LRA_Fullbase(trs,x11^x7,0,9000,"LRA_x11x7.txt")
        #self.LRA_Fullbase(trs, x7, 0, 9000, "LRA_x7.txt")
        #self.LRA_Fullbase(trs, x7^V, 0, 9000, "LRA_x7_MaskedSboxOut.txt")
        #self.LRA_Fullbase(trs,x3^x7,0,9000,"LRA_x3x7.txt")
        #self.LRA_Fullbase(trs, x3, 0, 9000, "LRA_x3.txt")
        #self.LRA_Fullbase(trs, x3^V, 0, 9000, "LRA_x3_MaskedSboxOut.txt")
        Expvar=[]
        print("Analysing leaky states\n")
        for cycle_no in range(19,35):
            print("Cycle {0}\n".format(cycle_no))
            Expvar_sample = self.GenRegressionBasis_OneSample(cycle_no, randbit)
            Expvar.append(Expvar_sample)
        self.autoRegression_general(trs, X,Expvar, bitn, drift, cv_start, outfile,N,16)
if __name__ == '__main__':
        N = 50000
        threshold = 5
        randbit=2
        cycle_no=9
        drift=40
        cv_start=20000
        #ModelVerifier().GiftSbox_manual_evaluation()
        mv=ModelVerifier()
        #mv.ExportInputs_MidoriP("MidoriP_Ftest_2500Samples_Rand2_Board1.trs","/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/Midori_P/randdata_Midori_Board1.txt")
        #mv.ExportInputs_ISWd2("ISWd2Mult_Ftest_7500Samples.trs",
        #                        "/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/ISWd2/randdata_ISWd2_Board0.txt")
        #mv.ExportInputs_GiftSbox("SboxFtest_5000Samples_Rand2_Board1.trs","/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/GIFT_Sbox/randdata_GiftSbox_Board1.txt")#mv.ExportInputs_MidoriP()
        #mv.ReadLeakyStates("/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/ISWd2/ISWd2_LeakyStates_board0.bin","ISWd2_Leaky_header.txt",N)
        #ExpVar=mv.GenRegressionBasis_OneSample(cycle_no, randbit)
        #trs = TRS_Reader.TRS_Reader(
        #       "SboxFtest_5000Samples_Rand2.trs")
        #trs.read_header()
        #N = trs.Number_of_Traces
        #trs.read_traces(N,0,4500)
        #mv.Regression_OneSample(trs, cycle_no-3, ExpVar,  randbit, drift, cv_start, "F-test.txt", N)
        #mv.GiftSbox_auto_evaluation("SboxFtest_5000Samples_Rand2.trs",
        #                            "/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/GIFT_Sbox/GiftSbox_LeakyStates_board0.bin",
        #                            "GiftSbox_header.txt", drift, cv_start)
        #mv.MidoriP_auto_evaluation("MidoriP_Ftest_2500Samples_Rand2_Board1.trs",
        #                            "/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/Midori_P/MidoriP_LeakyStates_board1.bin",
        #                            "MidoriP_header.txt", drift, cv_start,"MidoriP_Ftest_Auto_Board1.txt")
        mv.ISWd2_auto_evaluation("ISWd2Mult_Ftest_7500Samples.trs",
                                   "C:\\Users\\si-ga\\Documents\\GitHub\\uELMO\\Windows\\uELMO\\Examples\\ISWd2\\ModelEvaluation\\ISWMult_LeakyState.bin",
                                   "ISWd2_header.txt", drift, cv_start,"ISWd2_Ftest_Auto.txt")
        #mv.ISWd2_auto_evaluation("ISWd2Mult_Ftest_7500Samples.trs",
        #                           "C:\\Users\\si-ga\\Documents\\Klagenfurt_Oct_26\\Documents\\Elmo_verif\\ELMO_verif\\elmo_verif\\Examples\\ISWd2\\Model_Evaluation\\ISWd2_LeakyStates_board0.bin",
        #                           "ISWd2_header.txt", drift, cv_start,"ISWd2_Ftest_Auto_Part2.txt")
        #mv.ExportInputs_MaskedAES_Sbox("MaskedAES_MixColumn_Ttest.trs",
        #                        "/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/MaskedAES_R1/MixColumn/Model_Evaluation/randdata_MixColumn.txt")
        #mv.Sbox_auto_evaluation("/home/IWAS/gaosi/Documents/Python/MaskedAES_Sbox_Ttest.trs",
        #                         "/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/MaskedAES_R1/Sbox/Model_Evaluation/MaskedAES_Sbox_LeakyStates.bin",
        #                         "Sbox_header.txt", drift, cv_start, "Sbox_Ftest_Auto_Part2.txt")
        #mv.ADK_auto_evaluation("/home/IWAS/gaosi/Documents/Python/MaskedAES_ADK_Ttest.trs",
        #                         "/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/MaskedAES_R1/ADK/Model_Evaluation/MaskedAES_ADK_LeakyStates.bin",
        #                         "ADK_header.txt", drift, cv_start, "ADK_Ftest_Auto_Part2.txt")
        #mv.ShiftRow_auto_evaluation("/home/IWAS/gaosi/Documents/Python/MaskedAES_ShiftRow_Ttest.trs",
        #                       "/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/MaskedAES_R1/ShiftRow/Model_Evaluation/MaskedAES_ShiftRow_LeakyStates.bin",
        #                       "ShiftRow_header.txt", drift, cv_start, "ShiftRow_Ftest_Auto.txt")
        #mv.MixColumn_auto_evaluation("/home/IWAS/gaosi/Documents/Python/MaskedAES_MixColumn_Ttest.trs",
        #                       "/home/IWAS/gaosi/Documents/Elmo_verif/ELMO_verif/elmo_verif/Examples/MaskedAES_R1/MixColumn/Model_Evaluation/MaskedAES_MixColumn_LeakyStates.bin",
        #                       "MixColumn_header.txt", drift, cv_start, "MixColumn_Ftest_Auto.txt")