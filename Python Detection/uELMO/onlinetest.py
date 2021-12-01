import numpy


# Class for Online Test.
class OnlineTest:
    def __init__(self, tracelen, nbins=2**16, binrange=(-32768, 32768)):
        # Output data structure.
        self.records = dict()
        self.max=numpy.zeros(tracelen, dtype='uint')
        self.min= numpy.ones(tracelen, dtype='uint')*2*binrange[1]
        # Internal data structure.
        self.tracelen = tracelen  # Trace length, i.e. number of time points.
        self.ntracefixed = 0  # Number of fixed traces.
        self.ntracerandom = 0  # Number of random traces.
        # Histogram representing fixed traces.
        self.fixed_histogram = numpy.zeros((nbins, tracelen), dtype='uint')
        self.fixed_histogram = numpy.zeros((nbins, tracelen), dtype='uint')
        # Histogram representing random traces.
        self.random_histogram = numpy.zeros((nbins, tracelen), dtype='uint')
        self.nbins = nbins  # Number of bins.
        self.binrange = binrange  # Range of bins.
        self.binshift = -binrange[0]  # Shift of minimum bin towards 0.
        return

    # Update Records.
    def UpdateRecord(self):
        raise(Exception("Virtual function invoked."))
        return

    # Record traces by histogram.
    def UpdateTrace(self, trace, groupid):
        if 0 == groupid:  # 0 for FIXED traces.
            self.ntracefixed += 1
            for t in range(len(trace)):
                self.fixed_histogram[trace[t] + self.binshift, t] += 1
                if trace[t]+ self.binshift<self.min[t]:
                    self.min[t]=trace[t]+ self.binshift
                if trace[t] + self.binshift > self.max[t]:
                    self.max[t] = trace[t] + self.binshift
                pass
        elif 1 == groupid:  # 1 for RANDOM traces.
            self.ntracerandom += 1
            for t in range(len(trace)):
                self.random_histogram[trace[t] + self.binshift, t] += 1
                if trace[t]+ self.binshift<self.min[t]:
                    self.min[t]=trace[t]+ self.binshift
                if trace[t] + self.binshift > self.max[t]:
                    self.max[t] = trace[t] + self.binshift
                pass
        else:
            raise(Exception('Invalid flag.'))
            pass

        return

    # Write records specified by ${key} into file named ${filename}.
    def WriteTrace(self, filename, key=None):
        self.UpdateRecord()
        if None == key:
            for k in records:
                fn = str(k) + filename
                numpy.savetxt(fn, self.records[k],delimiter="\n")
            pass

        else:
            numpy.savetxt(filename, self.records[key],delimiter="\n")

        return
