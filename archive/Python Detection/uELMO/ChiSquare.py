# Two sample ChiSquared Test implementation by [1]. Histogram version from the scope
# [1]: Leakage Detection with the χ2-Test,  Amir Moradi, Bastian Richter, Tobias Schneider and François-Xavier Standaert
import math
import numpy as np
from scipy.stats import chi2
from scipy.special import comb


# Structure for Chi2 test result.
class Chi2SquareResult:
    def __init__(self, chi2=0, p=0):
        self.statistic = chi2
        self.pvalue = p
        return

# Perform two sample Chi2 Test with null hypothesis A == B.
# Both A and B must be historgrams, not raw data!!!
# minv and maxv mark the smallest/largest bin with non-zero entry
def Chisquare_2_samp(histA, histB, minv=0,maxv=65535):
    n = sum(histA)
    m = sum(histB)
    ret = Chi2SquareResult()

    # Compute Chi2 statistics.
    # Start with the frequency of the average histogram
    Freq=(histA+histB)/(n+m)
    zero_entry=0
    Chi2=0
    for i in range(minv,(maxv+1).astype('uint')):
        if(Freq[i]==0):
            zero_entry=zero_entry+1
            continue
        Chi2=Chi2+(histA[i]-Freq[i]*n)**2/(Freq[i]*n)+(histB[i]-Freq[i]*m)**2/(Freq[i]*m);

    # Compute the degree of freedom
    df=(maxv+1-minv-zero_entry)

    # Compute p-value.
    p =chi2.sf(Chi2, df)

    ret.statistic = Chi2
    ret.pvalue = p

    return ret
