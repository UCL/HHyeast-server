import sys
from enum import Enum, auto

# Enum for the different cases of overlap
class Overlap(Enum):
    FULL = auto()
    PARTIAL = auto()
    ZERO = auto()


class Clustering:
    def __init__(self, ov_min=10, ov_min_r=0.2):
        self._cluster_x1_min = []
        self._cluster_x1_max = []
        self._cluster_x2_min = []
        self._cluster_x2_max = []
        self._nhits_in_cluster = []
        self._cluster_labels = []
        # If edges are similar within max of those two, match will be included in cluster:
        self._overlap_min = ov_min   # number of residues
        self._overlap_min_ratio = ov_min_r # ratio

    def _clean(self):
        self._cluster_x1_min = []
        self._cluster_x1_max = []
        self._cluster_x2_min = []
        self._cluster_x2_max = []
        self._nhits_in_cluster = []
        self._cluster_labels = []

    # Given lists of hit beginings and ends, fill up the cluster lists data members,
    # as well as the list of cluster labels that each hit belongs to.
    def fill_clusters(self, x1l, x2l):
        self._clean()
        for x1, x2 in zip(x1l, x2l):
            icl = self._cluster_id(x1,x2)
            self._cluster_labels.append(icl)

    # List of cluster labels for each hit
    @property
    def clabels(self):
        return self._cluster_labels

    # Number of clusters
    @property
    def ncl(self):
        return len(self._nhits_in_cluster)

    # Check if hit with limits [x1,x2] overlaps with any of the existing clusters.
    # If yes, re-calculate cluster limits, increment its hit count, and return the cluster id.
    # If no, add new cluster and return the new cluster id.
    def _cluster_id(self, x1, x2):
        for i in range(self.ncl):
            overlaps = self._overlap(x1, x2, i)
            if overlaps==Overlap.FULL:
                self._cluster_x1_min[i] = min(self._cluster_x1_min[i],x1)
                self._cluster_x1_max[i] = max(self._cluster_x1_max[i],x1)
                self._cluster_x2_min[i] = min(self._cluster_x2_min[i],x2)
                self._cluster_x2_max[i] = max(self._cluster_x2_max[i],x2)
                self._nhits_in_cluster[i] += 1
                return i
        self._cluster_x1_min.append(x1)
        self._cluster_x1_max.append(x1)
        self._cluster_x2_min.append(x2)
        self._cluster_x2_max.append(x2)
        self._nhits_in_cluster.append(1)
        return self.ncl-1

    # Check if hit with limits [x1,x2] overlaps with index-th cluster.
    def _overlap(self, x1, x2, index):
        # Min and max cluster edges limits
        x1cl_min = self._cluster_x1_min[index]
        x1cl_max = self._cluster_x1_max[index]
        x2cl_min = self._cluster_x2_min[index]
        x2cl_max = self._cluster_x2_max[index]
        # Min and max cluster length
        dx_min = float(x2cl_min-x1cl_max)
        dx_max = float(x2cl_max-x1cl_min)
        # Min and max cluster edges overlap limits
        lo_min = x1cl_min-max(self._overlap_min_ratio*dx_max,self._overlap_min)
        lo_max = x1cl_max+max(self._overlap_min_ratio*dx_min,self._overlap_min)
        hi_min = x2cl_min-max(self._overlap_min_ratio*dx_min,self._overlap_min)
        hi_max = x2cl_max+max(self._overlap_min_ratio*dx_max,self._overlap_min)
        # Closter edges overlap flags
        ov_lo = x1>lo_min and x1<lo_max
        ov_hi = x2>hi_min and x2<hi_max
        if ov_lo and ov_hi:
            return Overlap.FULL
        else:
            return Overlap.ZERO
