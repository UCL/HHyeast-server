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
import dataProcessing

import sys

pal = palettes.viridis(10)
cmap = LinearColorMapper(palette=pal, low=50, high=100)

# Retrieving the arguments
args = curdoc().session_context.request.arguments
filename = args.get('filename')[0]

### Read data
prob_cutoff = 0.5
xmax1, nhits1, ref_data1 = dataProcessing.parse_file(filename, prob_cutoff, 'pfam')
source1 = ColumnDataSource( data=dict(ref_data1) ) # source holds a COPY of the ref_data dict
xmax2, nhits2, ref_data2 = dataProcessing.parse_file(filename, prob_cutoff, 'pfam')
source2 = ColumnDataSource( data=dict(ref_data2) ) # source holds a COPY of the ref_data dict

### Need this callback mechanism in order to update the plots when reading new probThr
myCallback = CustomJS(code="""
    window.dispatchEvent(new Event('resize'));
""")

page = column()

if nhits1!=0:
    ncl = 10
    #print(nhits1, file=sys.stderr)
    if nhits1>=ncl:
        ### Cluster data
        x2d = np.vstack((ref_data1['x1'], ref_data1['dx'])).T
        x1, dx, y, pcentcl, name, detail, clabels = dataProcessing.cluster_data(x2d, ref_data1['pcent'], ncl)
        new_data = dict()
        new_data['x1'] = x1
        new_data['x2'] = x1+dx
        new_data['dx'] = dx
        new_data['y'] = y
        new_data['name'] = name
        new_data['pcent'] = pcentcl
        new_data['detail'] = detail
        new_data['cluster'] = [1]*ncl
        source1.data = new_data
        ref_data1['cluster'] = clabels*100./float(ncl)


    ### Tooltip
    hover1 = HoverTool(
        tooltips = [ ("match No", "$index"),
                     ("description", "@detail") ]
    )
    
    ### Main figure
    p1 = figure(tools=[hover1,'save','pan','wheel_zoom'], title='Database PDB, hits clustered in 10.', width=1500, height=25*ncl,
                x_range=(0,xmax1), y_range=(min(ncl,nhits1)/2+1,0), x_axis_location="above")
    p1.ygrid.visible=False
    p1.yaxis.visible=False
    p1.y_range.callback = myCallback
    p1.hbar(y="y", height=0.4, left="x1", right="x2", source=source1,
            color={'field': 'pcent', 'transform': cmap})
    labels_pname1 = LabelSet(x='x1', y='y', text='name', source=source1, text_baseline='middle')
    p1.add_layout(labels_pname1)


    ### Page layout
    page = column( p1 )

curdoc().add_root(page)
