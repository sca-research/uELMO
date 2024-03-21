import numpy
from onlinetest import OnlineTest
import ChiSquare

FIX = True
RANDOM = False

# Class for ChiSquare test online using histograms.
class Chi2OnlineTest(OnlineTest):
    def __init__(self, tracelen, nbins=2**16, binrange=(-32768, 32767)):
        super().__init__(tracelen, nbins, binrange)
        # Neyman's statistics.
        self.records['statistic'] = numpy.zeros((1, tracelen))
        # p-values of Neyman's tests.
        self.records['pvalue'] = numpy.zeros((1, tracelen))
        return

    def UpdateRecord(self):
        n = int(self.fixed_histogram[:, 0].sum())
        m = int(self.random_histogram[:, 0].sum())
        # Update records for by each time point.
        for i in range(self.tracelen):
            if 0 == n or 0 == m:
                raise(Exception("# No data."))
                return
            ret = ChiSquare.Chisquare_2_samp(self.fixed_histogram[:, i], self.random_histogram[:, i],self.min[i], self.max[i])
            self.records['statistic'][:, i] = ret.statistic
            self.records['pvalue'][:, i] = ret.pvalue
        return
