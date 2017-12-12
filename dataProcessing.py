from csb.bio.io import HHpredOutputParser
from sklearn.cluster import KMeans

import sys

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


# Read data from hitList structure
def fill_data_dict(nhits, hitList, db):
    if db in ['pdb', 'pfam', 'yeast']:
        x1, x2, dx, y, pcent, name, detail = fill_data(nhits, hitList, db)
        data = dict(x1=x1, x2=x2, dx=dx, y=y, name=name, pcent=pcent, detail=detail)
        
        return len(x1), data
    else:
        raise ValueError("Data for database "+db+" does not exist. Please choose between pdb, pfam or yeast.")

def fill_data(nhits, hitList, db):
    x1 = []
    x2 = []
    dx = []
    y = []
    pcent = []
    name = []
    detail = []
    for i in range(0,nhits):
        hit = hitList[i]
        if (hit.id)[0:2]=='PF':
            if db!='pfam':
                continue
        elif (hit.id)[0:3]=='NP_':
            if db!='yeast':
                continue
            else:
                fixed = yeast_name_fixed(hit.id)
                hit.id = fixed[0]
                if hasattr(hit,'name'):
                    hit.name = fixed[1]
        elif db!='pdb':
            continue
        x1.append(hit.qstart)
        x2.append(hit.qend)
        dx.append(hit.qend-hit.qstart)
        y.append(float(len(y)+1)/2.)
        pcent.append(100*hit.probability)
        name.append(hit.id+' : {:.2f}%'.format(pcent[-1]))
        if hasattr(hit,'name'):
            detail.append(hit.name)
        else :
            detail.append("no detail")

    return x1, x2, dx, y, pcent, name, detail


yeast_name_map = {}
syst_name_map = {}
std_name_map = {}
# Fill name mapping dictionaries
def fill_name_maps():
    global yeast_name_map, syst_name_map, std_name_map
    with open("yeast_names_ref.txt", "r") as f:
        for line in f:
            words = line.split()
            yeast_name = words[0]
            syst_name = words[1]
            std_name = ''
            new_name = syst_name
            description = syst_name+' (hypothetical protein)'
            if len(words)==3:
                std_name = words[2]
                new_name = std_name
                description = std_name
                syst_name_map[std_name] = syst_name
            yeast_name_map[yeast_name] = new_name, description
            std_name_map[syst_name] = std_name

# Fix ORF name from yeast database
def yeast_name_fixed(name):
    global yeast_name_map
    if len(yeast_name_map)==0:
        fill_name_maps()
    return yeast_name_map[name]

# Return systematic/standard name from the other
def systematic_name(name):
    global syst_name_map
    if len(syst_name_map)==0:
        fill_name_maps()
    return syst_name_map[name]

def standard_name(name):
    global std_name_map
    if len(std_name_map)==0:
        fill_name_maps()
    return std_name_map[name]


# Active clustering: override input data per hit  with data per cluster
def cluster_data(x2d, pcent, n_clust):
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
                break
        namecl.append(str(pcentcl[i])+'%')
        detailcl.append('Some detail...')

    return x1cl, x2cl, ycl, pcentcl, namecl, detailcl, c_labels

# Passive clustering: return cluster labels only
def cluster_data_pred(x2d, n_clust):
    kmeans = KMeans(n_clusters=n_clust, random_state=77)
    c_labels = kmeans.fit_predict(x2d)

    return c_labels



