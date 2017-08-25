from csb.bio.io import HHpredOutputParser

from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.models import palettes
from bokeh.layouts import widgetbox, column, layout
from bokeh.models.widgets import Slider, Panel, Tabs, TextInput
from bokeh.models import HoverTool, CustomJS

import numpy as np

from sklearn.cluster import KMeans

################## Some helper functions ##################

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
        name.append((hitList[i]).id+' : '+str(pcent[i])+'%')
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



################## Script starts here ##################

pal = palettes.viridis(10)
cmap = LinearColorMapper(palette=pal, low=50, high=100)

### Empty defaults. Meaningful values and data will be read from
### the file that will be input from the widgets
xmax = 100
nhits = 100
prob_cutoff = 0.5
ref_data = dict(x1=[], x2=[], dx=[], y=[], name=[], pcent=[], detail=[])
source = ColumnDataSource( data=dict(ref_data) ) # source holds a COPY of the ref_data dict


###### Tab 1
### Tooltip
hover1 = HoverTool(
    tooltips = [ ("match No", "$index"),
                 ("description", "@detail") ]
    )

### Main figure
p1 = figure(tools=[hover1,'save','pan','wheel_zoom'], width=1500, height=25*nhits,
            x_range=(0,xmax), y_range=(nhits/2+1,0), x_axis_location="above")
p1.ygrid.visible=False
p1.yaxis.visible=False
### Need this callback mechanism in order to update the plots when reading new file/probThr
myCallback = CustomJS(args=dict(fig=p1), code="""
    var doc = fig.document;
    doc.resize();
""")
p1.y_range.callback = myCallback
###
p1.hbar(y="y", height=0.4, left="x1", right="x2", source=source,
       color={'field': 'pcent', 'transform': cmap})
labels_pname = LabelSet(x='x1', y='y', text='name', source=source, text_baseline='middle')
p1.add_layout(labels_pname)

### Clustering figure
pcl1 = figure(tools=['save','pan','wheel_zoom'], width=500, height=500, x_range=(0,xmax), y_range=(0,xmax))
pcl1.x(x="x1", y="dx", source=source,
       color={'field': 'pcent', 'transform': cmap})


###### Tab 2
### Tooltip
hover2 = HoverTool(
    tooltips = [ ("match No", "$index"),
                 ("description", "@detail") ]
    )

### Main figure
p2 = figure(tools=[hover2,'save','pan','wheel_zoom'], plot_width=1500, plot_height=25*nhits,
           x_range=(0,xmax), y_range=(nhits/2+1,0), x_axis_location="above")
p2.ygrid.visible=False
p2.yaxis.visible=False
### Need this callback mechanism in order to update the plots when reading new file/probThr
myCallback = CustomJS(args=dict(fig=p2), code="""
    var doc = fig.document;
    doc.resize();
""")
p2.y_range.callback = myCallback
###
p2.hbar(y="y", height=0.4, left="x1", right="x2", source=source,
       color={'field': 'pcent', 'transform': cmap})
labels_pname = LabelSet(x='x1', y='y', text='name', source=source, text_baseline='middle')
p2.add_layout(labels_pname)

### Clustering figure
pcl2 = figure(tools=['save','pan','wheel_zoom'], width=500, height=500, x_range=(0,xmax), y_range=(0,xmax))
pcl2.x(x="x1", y="dx", source=source,
       color={'field': 'pcent', 'transform': cmap})


### Tab 1 slider widget
ncl_slider1 = Slider(start=0, end=10, value=0, step=1, title="Number of clusters")
### Data-slider interaction
def slider_handler1(attrname, old, new):
    global ref_data
    ncl = ncl_slider1.value
    if ncl==0:
        source.data = ref_data
    else:
        x2d = np.vstack((ref_data['x1'], ref_data['dx'])).T
        clabels = cluster_data_pred(x2d, ncl)
        source.data['pcent'] = (clabels+1)*100./float(ncl)
        cmap.low = 0
ncl_slider1.on_change("value", slider_handler1)


### Tab 2 slider widget
ncl_slider2 = Slider(start=0, end=10, value=0, step=1, title="Number of clusters")
### Data-slider interaction
def slider_handler2(attrname, old, new):
    global ref_data
    ncl = ncl_slider2.value
    if ncl==0:
        source.data = ref_data
    else:
        x2d = np.vstack((ref_data['x1'], ref_data['dx'])).T
        x1, dx, y, pcentcl, name, detail, clabels = cluster_data(x2d, ref_data['pcent'], ncl)
        new_data = dict()
        new_data['x1'] = x1
        new_data['x2'] = x1+dx
        new_data['dx'] = dx
        new_data['y'] = y
        new_data['name'] = name
        new_data['pcent'] = pcentcl
        new_data['detail'] = detail
        new_data['cluster'] = [1]*ncl
        source.data = new_data
        ref_data['cluster'] = clabels*100./float(ncl)
ncl_slider2.on_change("value", slider_handler2)


### Tab 1 textInput widgets
filename_text = TextInput(value="", title="File name:")
threshold_text = TextInput(value="0.5", title="Probability threshold:")
### Data-textInput interaction
def text_handler1(attrname, old, new):
    ### TODO: these globals and manually recalling of the parser and stuff
    ### is ugly. Need to make the parser (or something) a class.
    global ref_data, p1, pcl1, p2, pcl2, filename, prob_cutoff
    filename = filename_text.value
    xmax, nhits, ref_data = parse_file(filename, prob_cutoff)
    p1.height = 25*nhits
    p1.plot_height = 25*nhits
    p1.x_range.end = xmax
    p1.y_range.start = nhits/2+1
    pcl1.x_range.end = xmax
    pcl1.y_range.end = xmax
    p2.height = 25*nhits
    p2.plot_height = 25*nhits
    p2.x_range.end = xmax
    p2.y_range.start = nhits/2+1
    pcl2.x_range.end = xmax
    pcl2.y_range.end = xmax
    source.data = ref_data
    ncl_slider1.value = 0
    ncl_slider2.value = 0
def text_handler2(attrname, old, new):
    global ref_data, p1, p2, prob_cutoff
    global filename
    prob_cutoff = float(threshold_text.value)
    xmax, nhits, ref_data = parse_file(filename, prob_cutoff)
    cmap.low = prob_cutoff*100
    p1.height = 25*nhits
    p1.y_range.start = nhits/2+1
    p2.height = 25*nhits
    p2.y_range.start = nhits/2+1
    source.data = ref_data
    ncl_slider1.value = 0
    ncl_slider2.value = 0
filename_text.on_change("value", text_handler1)
threshold_text.on_change("value", text_handler2)


### Page layouts
tab1 = Panel( child=layout( [ [widgetbox(ncl_slider1, filename_text, threshold_text), pcl1 ],
                              [p1] ] ),
              title="Passive clustering")
tab2 = Panel( child=layout( [widgetbox(ncl_slider2), pcl2 ],
                            [p2] ),
              title="Active clustering")

tabs = Tabs(tabs=[tab1, tab2])
curdoc().add_root(tabs)
