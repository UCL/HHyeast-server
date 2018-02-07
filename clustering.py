import sys

class Clustering:
    def __init__(self):
        self.x1cl = []
        self.x2cl = []
        self.ncl = []
        self.ov_min1 = 0.1 # Below this, there's no overlap
        self.ov_min2 = 0.1 # Above this, there's definitely overlap

    # Passive clustering
    # Given lists of hit beginnnings and ends, returns list of cluster labels that each
    # hit belongs to.
    def passive(self, x1l, x2l):
        c_labels = []
        for x1, x2 in zip(x1l, x2l):
            icl = self._cluster_id(x1,x2)
            c_labels.append(icl)
        return c_labels, len(set(c_labels))



    # Check if hit with limits [x1,x2] overlaps with any of the existing clusters.
    # If yes, re-calculate cluster limits, increment its hit count, and return the cluster id.
    # If no, add new cluster and return the new cluster id.
    def _cluster_id(self, x1, x2):
        for i in range(len(self.ncl)):
            dx_min = min(x2-x1, self.x2cl[i]-self.x1cl[i])
            if ((x2-self.x1cl[i])>(self.ov_min2*dx_min) and x2<=self.x2cl[i]) or ((self.x2cl[i]-x1)>(self.ov_min2*dx_min) and x2>self.x2cl[i]): # There is overlap
                self.x1cl[i] = min(self.x1cl[i],x1)
                self.x2cl[i] = max(self.x2cl[i],x2)
                self.ncl[i] += 1
                return i
        self.x1cl.append(x1)
        self.x2cl.append(x2)
        self.ncl.append(1)
        return len(self.ncl)-1
