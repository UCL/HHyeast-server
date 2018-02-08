import sys
from enum import Enum, auto

# Enum for the different cases of overlap
class Overlap(Enum):
    FULL = auto()
    PARTIAL = auto()
    ZERO = auto()


class Clustering:
    def __init__(self):
        self._x1cl = []
        self._x2cl = []
        self._ncl = []
        self._clabels = []
        self._ov_min1 = 0.1 # Below this, there's no overlap
        self._ov_min2 = 0.5 # Above this, there's definitely overlap

    def _clean(self):
        self._x1cl = []
        self._x2cl = []
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
            if self._overlap(x1, x2, self._x1cl[i], self._x2cl[i])==Overlap.FULL:
                self._x1cl[i] = min(self._x1cl[i],x1)
                self._x2cl[i] = max(self._x2cl[i],x2)
                self._ncl[i] += 1
                return i
        self._x1cl.append(x1)
        self._x2cl.append(x2)
        self._ncl.append(1)
        return len(self._ncl)-1

    def _overlap(self, x1, x2, x1cl, x2cl):
        dx_min = min(x2-x1, x2cl-x1cl)
        if (x2-x1cl>self._ov_min2*dx_min and x2<=x2cl) or (x2cl-x1>self._ov_min2*dx_min and x2>x2cl):
            return Overlap.FULL
