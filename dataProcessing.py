from csb.bio.io import HHpredOutputParser

import sys
import os

import nameProcessing
from clustering import Clustering

# Parse HHSearch output file up to probability cutoff
def parse_file(filename, prob_cutoff, db=''):
    hhpParser = HHpredOutputParser()
    hitList = hhpParser.parse_file(filename)
    xmax = hitList.match_columns

    nhits = 0
    for i in range(0,len(hitList)):
        if (hitList[i]).probability < prob_cutoff:
            break
        nhits += 1

    if not db:
        return xmax, nhits, hitList
    else:
        protein = os.path.basename(filename).split('.')[0].upper()
        nhitsDB, data = fill_data_dict(nhits, hitList, db, protein)
        print(nhitsDB, file=sys.stderr)
        return xmax, nhitsDB, data


# Fill data dictionary from hitList structure and do some post-processing
def fill_data_dict(nhits, hitList, db, protein, squash=True):
    if db in ['pdb', 'pfam', 'yeast']:
        print(nhits, file=sys.stderr)
        data, hasLongHits = fill_data(nhits, hitList, db, protein)
        if hasLongHits:
            data = filter_short_hits(data)
            print(len(data['y']), file=sys.stderr)
        ymax = int(data['y'][-1]*2.)
        if squash:
            ymax, data = squash_data(data)
        print(ymax, file=sys.stderr)
        
        return ymax, data
    else:
        raise ValueError("Data for database "+db+" does not exist. Please choose between pdb, pfam or yeast.")

# These globals control the filtering of short hits:
# Taking into account only hits with probability<prob_cutoff,
# - if there are any hits with length>=min_hit_length2, filter out all hits with length<min_hit_length2
# - if not, filter out all hits with length<min_hit_length1, i.e. keep min_hit_length1 <= length < min_hit_length2
#
# According to this logic, the really short hits (length<min_hit_length1) are always filtered out.
# Therefore, this part of the filtering, as well as some of the length<min_hit_length2 one if appropriate, 
# is done pre-emptively inside fill_data, in order to speed-up execution. The rest of the filtering,
# if needed, is done in the separate function filter_short_hits.
min_hit_length1 = 20
min_hit_length2 = 30
prob_cutoff = 0.99

# Fill data dictionary from hitList structure
def fill_data(nhits, hitList, db, protein):
    x1 = []
    x2 = []
    dx = []
    x1t = []
    x2t = []
    dxt = []
    y = []
    pcent = []
    name = []
    detail = []
    hasLongHits = False

    for i in range(0,nhits):
        hit = hitList[i]
        # Pre-filter out some short hits
        if hit.qend-hit.qstart<min_hit_length1:
            continue
        if hasLongHits and hit.qend-hit.qstart<min_hit_length2:
            continue
        # Do some database-related filtering and pre-processing
        if (hit.id)[0:2]=='PF':
            if db!='pfam':
                continue
            hit.id = hit.id.split('.')[0]
        elif (hit.id)[0:3]=='NP_':
            if db!='yeast':
                continue
            else:
                fixed = nameProcessing.yeast_name_fixed(hit.id)
                hit.id = fixed[0]
                if hasattr(hit,'name'):
                    hit.name = fixed[1]
        elif db!='pdb':
            continue
        # Get rid of hits with the same name as current protein
        if nameProcessing.systematic_name(hit.id)==protein or (hasattr(hit,'name') and hit.name.find(nameProcessing.standard_name(protein))>=0):
            continue
        # Fill data lists
        x1.append(hit.qstart)
        x2.append(hit.qend)
        dx.append(hit.qend-hit.qstart)
        x1t.append(hit.start)
        x2t.append(hit.end)
        dxt.append(hit.slength)
        y.append(float(len(y)+1)/2.)
        pcent.append(100*hit.probability)
        name.append(hit.id+' : {:d}%'.format(int(pcent[-1])))
        if hasattr(hit,'name'):
            detail.append(hit.name)
        else:
            detail.append(hit.id)
        if hit.probability<prob_cutoff and hit.qend-hit.qstart>=min_hit_length2:
            hasLongHits = True

    data = dict(x1=x1, x2=x2, xm=[beg+dif/2 for beg,dif in zip(x1,dx)], dx=dx, x1t=x1t, x2t=x2t, dxt=dxt,
                y=y, name=name, pcent=pcent, detail=detail)

    return data, hasLongHits


# Filter out short hits from data dictionary
def filter_short_hits(data):
    nhits = len(data['x1'])
    for i in range(nhits):
        if data['dx'][i]<min_hit_length2:
            for key in data.keys():
                data[key].pop(i)
    return data


# Squash y-coordinate of data for compact view
def squash_data(data):
    nhits = len(data['x1'])
    if nhits==0:
        return 0, data

    ymax = data['y'][0]
    gap = 5
    for i in range(nhits): # loop over hits
        for j in range(nhits): # loop over y positions
            y = float(j+1)/2.
            isGap = True
            for k in range(nhits): # loop over hits in this y position
                if k!=i and data['y'][k]==y:
                    if data['x2'][k]>data['x1'][i]-gap and data['x1'][k]<data['x2'][i]+gap:
                        isGap = False
                        break
            if isGap:
                data['y'][i] = y
                break
        ymax = max(ymax,data['y'][i])
    return int(ymax*2.), data


# Active clustering: override input data per hit with data per cluster
def cluster_data(data, ov_min=10, ov_min1=0.2):
    cl = Clustering(ov_min, ov_min1)
    cl.fill_clusters(data['x1'], data['x2'])

    c_labels = cl.clabels
    nhits = len(c_labels)
    n_clust = cl.ncl
    x1cl = cl.cluster_x1
    x2cl = cl.cluster_x2
    ycl = []
    pcentcl = []
    namecl = []
    detailcl = []
    x1tcl = []
    x2tcl = []
    dxtcl = []
    for i in range(0,n_clust):
        ycl.append(float(i+1)/2.)
        for j in range(0,nhits):
            if c_labels[j]==i:
                pcentcl.append(data['pcent'][j])
                namecl.append(data['name'][j])
                detailcl.append(data['detail'][j])
                x1tcl.append(data['x1t'][j])
                x2tcl.append(data['x2t'][j])
                dxtcl.append(data['dxt'][j])
                break

    new_data = dict(x1=x1cl, x2=x2cl, dx=[end-beg for beg,end in zip(x1cl,x2cl)],
                    xm=[(beg+end)/2 for beg,end in zip(x1cl,x2cl)],
                    x1t=x1tcl, x2t=x2tcl, dxt=dxtcl,
                    y=ycl, nhits=cl.nhits, name=namecl, pcent=pcentcl, detail=detailcl)

    return new_data, n_clust

# Passive clustering: return cluster labels only
def cluster_pred(x1l, x2l, ov_min=10, ov_min1=0.2):
    cl = Clustering(ov_min, ov_min1)
    cl.fill_clusters(x1l, x2l)

    return cl.clabels, cl.ncl


