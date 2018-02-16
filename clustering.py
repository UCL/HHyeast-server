import sys
from enum import Enum, auto

# Enum for the different cases of overlap
class Overlap(Enum):
    FULL = auto()
    PARTIAL = auto()
    ZERO = auto()


class Clustering:
    def __init__(self, ov_min=10, ov_min1=0.2, ov_min2=0.5):
        self._x1cl_min = []
        self._x1cl_max = []
        self._x2cl_min = []
        self._x2cl_max = []
        self._ncl = []
        self._clabels = []
        # If edges are similar within max of those two, match will be included in cluster:
        self._ov_min = ov_min   # number of residues
        self._ov_min_r1 = ov_min1 # ratio
        # Not currently used
        self._ov_min_r2 = ov_min2

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
        for i in range(len(self._ncl)):
            overlaps = self._overlap(x1, x2, i)
            if overlaps==Overlap.FULL:
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

    # Check if hit with limits [x1,x2] overlaps with index-th cluster.
    def _overlap(self, x1, x2, index):
        # Min and max cluster edges limits
        x1cl_min = self._x1cl_min[index]
        x1cl_max = self._x1cl_max[index]
        x2cl_min = self._x2cl_min[index]
        x2cl_max = self._x2cl_max[index]
        # Min and max cluster length
        dx_min = float(x2cl_min-x1cl_max)
        dx_max = float(x2cl_max-x1cl_min)
        # Min and max cluster edges overlap limits
        lo_min = x1cl_min-max(self._ov_min_r1*dx_max,self._ov_min)
        lo_max = x1cl_max+max(self._ov_min_r1*dx_min,self._ov_min)
        hi_min = x2cl_min-max(self._ov_min_r1*dx_min,self._ov_min)
        hi_max = x2cl_max+max(self._ov_min_r1*dx_max,self._ov_min)
        # Closter edges overlap flags
        ov_lo = x1>lo_min and x1<lo_max
        ov_hi = x2>hi_min and x2<hi_max
        if ov_lo and ov_hi:
            return Overlap.FULL
        else:
            return Overlap.ZERO
