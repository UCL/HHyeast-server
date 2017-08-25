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


pal = palettes.viridis(10)
cmap = LinearColorMapper(palette=pal, low=50, high=100)

# Retrieving the arguments
args = curdoc().session_context.request.arguments
filename = args.get('filename')[0]

### Read data
prob_cutoff = 0.5
xmax, nhits, ref_data = dataProcessing.parse_file(filename, prob_cutoff)
source = ColumnDataSource( data=dict(ref_data) ) # source holds a COPY of the ref_data dict
### Cluster data
x2d = np.vstack((ref_data['x1'], ref_data['dx'])).T
ncl = 10
x1, dx, y, pcentcl, name, detail, clabels = dataProcessing.cluster_data(x2d, ref_data['pcent'], ncl)
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


### Tooltip
hover1 = HoverTool(
    tooltips = [ ("match No", "$index"),
                 ("description", "@detail") ]
    )

### Main figure
p1 = figure(tools=[hover1,'save','pan','wheel_zoom'], title='Database BLA, hits clustered in 10.', width=1500, height=25*ncl,
            x_range=(0,xmax), y_range=(ncl/2+1,0), x_axis_location="above")
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


### Page layout
page = column( p1 )
curdoc().add_root(page)
