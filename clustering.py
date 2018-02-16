import sys
from enum import Enum, auto

# Enum for the different cases of overlap
class Overlap(Enum):
    FULL = auto()
    PARTIAL = auto()
    ZERO = auto()


class Clustering:
    def __init__(self, ov_min=10, ov_min1=0.1, ov_min2=0.5):
        self._x1cl_min = []
        self._x1cl_max = []
        self._x2cl_min = []
        self._x2cl_max = []
        self._ncl = []
        self._clabels = []
        self._ov_min = ov_min # Below this number of overlapping residues, there's no overlap
        self._ov_min1 = ov_min1 # Below this overlap ratio (if it's larger than _ov_min residues), there's no overlap
        self._ov_min2 = ov_min2 # Above this overlap ratio, there's definitely overlap

    def _clean(self):
        self._x1cl_min = []
        self._x1cl_max = []
        self._x2cl_min = []
        self._x2cl_max = []
        self._ncl = []
        self._clabels = []

    # Given lists of hit beginings and ends, fill up the cluster lists data members,
    # as well as the list of cluster labels that each hit belongs to.
    def fill_clusters(self, x1l, x2l):
        self._clean()
        for x1, x2 in zip(x1l, x2l):
            icl = self._cluster_id(x1,x2)
            self._clabels.append(icl)

    # List of cluster labels for each hit
    @property
    def clabels(self):
        return self._clabels

    # Number of clusters
    @property
    def ncl(self):
        return len(self._ncl)

    # Check if hit with limits [x1,x2] overlaps with any of the existing clusters.
    # If yes, re-calculate cluster limits, increment its hit count, and return the cluster id.
    # If no, add new cluster and return the new cluster id.
    def _cluster_id(self, x1, x2):
        o_clusters = ()
        for i in range(len(self._ncl)):
            overlaps, o_ratio = self._overlap(x1, x2, self._x1cl_min[i], self._x1cl_max[i], self._x2cl_min[i], self._x2cl_max[i])
            if overlaps==Overlap.FULL:
                o_clusters = (o_ratio, i)
                break
            elif overlaps==Overlap.PARTIAL:
                if (o_clusters and o_clusters[0]<o_ratio) or not o_clusters:
                    o_clusters = (o_ratio, i)
        if o_clusters:
            i = o_clusters[1]
            self._x1cl_min[i] = min(self._x1cl_min[i],x1)
            self._x1cl_max[i] = max(self._x1cl_max[i],x1)
            self._x2cl_min[i] = min(self._x2cl_min[i],x2)
            self._x2cl_max[i] = max(self._x2cl_max[i],x2)
            self._ncl[i] += 1
            return i
        self._x1cl_min.append(x1)
        self._x1cl_max.append(x1)
        self._x2cl_min.append(x2)
        self._x2cl_max.append(x2)
        self._ncl.append(1)
        return len(self._ncl)-1

    def _overlap(self, x1, x2, x1cl_min, x1cl_max, x2cl_min, x2cl_max):
        dx_max = float(x2cl_max-x1cl_min)
        dx_min = float(x2cl_min-x1cl_max)
        if x1>(x1cl_min-max(self._ov_min1*dx_max,self._ov_min)) and x1<(x1cl_max+max(self._ov_min1*dx_min,self._ov_min)) and x2>(x2cl_min-max(self._ov_min1*dx_min,self._ov_min)) and x2<(x2cl_max+max(self._ov_min1*dx_max,self._ov_min)):
            return Overlap.FULL, 0
        else:
            return Overlap.ZERO, 0
