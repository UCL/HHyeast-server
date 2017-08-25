from csb.bio.io import HHpredOutputParser
from sklearn.cluster import KMeans


# Parse HHSearch output file up to probability cutoff
def parse_file(filename, prob_cutoff):
    hhpParser = HHpredOutputParser()
    hitList = hhpParser.parse_file(filename)
    xmax = hitList.match_columns

    nhits = 0
    for i in range(0,len(hitList)):
        if (hitList[i]).probability < prob_cutoff:
            break
        nhits += 1
    x1, x2, dx, y, pcent, name, detail = fill_data(nhits, hitList)
    data = dict(x1=x1, x2=x2, dx=dx, y=y, name=name, pcent=pcent, detail=detail)

    return xmax, nhits, data

# Read data from hitList structure
def fill_data(nhits,hitList):
    x1 = []
    x2 = []
    dx = []
    y = []
    pcent = []
    name = []
    detail = []
    for i in range(0,nhits):
        x1.append((hitList[i]).qstart)
        x2.append((hitList[i]).qend)
        dx.append((hitList[i]).qend-(hitList[i]).qstart)
        y.append(float(i+1)/2.)
        pcent.append(100*(hitList[i]).probability)
        name.append((hitList[i]).id+' : {:.2f}%'.format(pcent[i]))
        if hasattr(hitList[i],'name'):
            detail.append(hitList[i].name)
        else :
            detail.append("no detail")

    return x1, x2, dx, y, pcent, name, detail

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



