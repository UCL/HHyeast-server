from csb.bio.io import HHpredOutputParser
from sklearn.cluster import KMeans

import sys

import nameProcessing

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
        nhitsDB, data = fill_data_dict(nhits, hitList, db)
        return xmax, nhitsDB, data


# Fill data dictionary from hitList structure and do some post-processing
def fill_data_dict(nhits, hitList, db):
    if db in ['pdb', 'pfam', 'yeast']:
        data, hasLongHits = fill_data(nhits, hitList, db)
        if hasLongHits:
            data = filter_short_hits(data)
        ymax, data = squash_data(data)
        
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
def fill_data(nhits, hitList, db):
    x1 = []
    x2 = []
    dx = []
    x1t = []
    x2t = []
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
        # Fill data lists
        x1.append(hit.qstart)
        x2.append(hit.qend)
        dx.append(hit.qend-hit.qstart)
        x1t.append(hit.start)
        x2t.append(hit.end)
        y.append(float(len(y)+1)/2.)
        pcent.append(100*hit.probability)
        name.append(hit.id+' : {:d}%'.format(int(pcent[-1])))
        if hasattr(hit,'name'):
            detail.append(hit.name)
        else:
            detail.append(hit.id)
        if hit.probability<prob_cutoff and hit.qend-hit.qstart>=min_hit_length2:
            hasLongHits = True

    data = dict(x1=x1, x2=x2, xm=[beg+dif/2 for beg,dif in zip(x1,dx)], dx=dx, x1t=x1t, x2t=x2t,
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


# Active clustering: override input data per hit  with data per cluster
def cluster_data(x2d, pcent, detail, n_clust):
    kmeans = KMeans(n_clusters=n_clust, random_state=77)
    c_labels = kmeans.fit_predict(x2d)
    c_centers = kmeans.cluster_centers_

    nhits = x2d.shape[0]
    x1cl = c_centers[:,0]
    x2cl = c_centers[:,1]
    ycl = []
    pcentcl = []
    namecl = []
    detailcl = []
    for i in range(0,n_clust):
        ycl.append(float(i+1)/2.)
        for j in range(0,nhits):
            if c_labels[j]==i:
                pcentcl.append(pcent[j])
                detailcl.append(detail[j])
                break
        namecl.append(str(int(pcentcl[i]))+'%')

    return x1cl, x2cl, ycl, pcentcl, namecl, detailcl, c_labels

# Passive clustering: return cluster labels only
def cluster_data_pred(x2d, n_clust):
    kmeans = KMeans(n_clusters=n_clust, random_state=77)
    c_labels = kmeans.fit_predict(x2d)

    return c_labels



