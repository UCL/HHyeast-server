from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.models import palettes
from bokeh.layouts import widgetbox, column, layout, gridplot
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
db = args.get('db')[0].decode("utf-8")

### Read data
prob_cutoff = 0.5
xmax, nhits, ref_data = dataProcessing.parse_file(filename, prob_cutoff, db)
source = ColumnDataSource( data=dict(ref_data) ) # source holds a COPY of the ref_data dict


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
### Need this callback mechanism in order to update the plots when reading new probThr
myCallback = CustomJS(code="""
    window.dispatchEvent(new Event('resize'));
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


### Slider widget
ncl_slider = Slider(start=0, end=10, value=0, step=1, title="Number of clusters")
### Data-slider interaction
def slider_handler(attrname, old, new):
    global ref_data
    ncl = ncl_slider.value
    if ncl==0:
        source.data = ref_data
    else:
        x2d = np.vstack((ref_data['x1'], ref_data['dx'])).T
        clabels = dataProcessing.cluster_data_pred(x2d, ncl)
        source.data['pcent'] = (clabels+1)*100./float(ncl)
        cmap.low = 0
ncl_slider.on_change("value", slider_handler)


### textInput widget
threshold_text = TextInput(value="0.5", title="Probability threshold:")
### Data-textInput interaction
def text_handler2(attrname, old, new):
    global ref_data, p1, p2, prob_cutoff
    global filename
    prob_cutoff = float(threshold_text.value)
    xmax, nhits, ref_data = dataProcessing.parse_file(filename, prob_cutoff, db)
    cmap.low = prob_cutoff*100
    p1.height = 25*nhits
    p1.y_range.start = nhits/2+1
    source.data = ref_data
    ncl_slider.value = 0
threshold_text.on_change("value", text_handler2)


### Page layout
page = gridplot( [ [widgetbox(ncl_slider, threshold_text), pcl1 ],
                              [p1] ] )
curdoc().add_root(page)
