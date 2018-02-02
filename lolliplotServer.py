from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.models import palettes
from bokeh.layouts import widgetbox, column, layout
from bokeh.models.widgets import Slider, Panel, Tabs, TextInput, PreText
from bokeh.models import HoverTool, CustomJS

import numpy as np
import dataProcessing

import sys

pal = palettes.viridis(10)
cmap = LinearColorMapper(palette=pal, low=50, high=100)

try:
    # Retrieving the arguments
    args = curdoc().session_context.request.arguments
    filename = args.get('filename')[0].decode("utf-8")

    ### Read data
    prob_cutoff = 0.5
    xmax = 0
    dbname_l = []
    nhits_l = []
    ref_data_l = []
    source_l = []
    dbs = ['pdb', 'pfam', 'yeast']
    xmax, nhitsALL, hitList = dataProcessing.parse_file(filename, prob_cutoff) # Get all hits
    # Loop over databases
    for db in dbs:
        nhits, ref_data = dataProcessing.fill_data_dict(nhitsALL, hitList, db)
        if nhits!=0:
            dbname_l.append(db.upper())
            nhits_l.append(nhits)
            ref_data_l.append(dict(ref_data))
            source_l.append(ColumnDataSource( data=ref_data.copy() )) # source holds a COPY of the ref_data dict

    ### Stuff common to all plots:
    ### Need this callback mechanism in order to update the plots when reading new probThr
    myCallback = CustomJS(code="""
        window.dispatchEvent(new Event('resize'));
    """)
    # Tooltip
    hover = HoverTool(
        tooltips = [ ("Cluster limits", "@x1-@x2"),
                     ("Highest probability hit", "@detail"),
                     ("Template HMM", "@x1t-@x2t (@dxt)") ]
    )

    page = column()
    ncl_ref = 10
    plots_l = []
    for dbname, nhits, ref_data, source in zip(dbname_l, nhits_l, ref_data_l, source_l):
        #print(nhits1, file=sys.stderr)
        title = 'Matches to database '+dbname
        ncl = ncl_ref
        if nhits>=ncl:
            x2d = np.vstack((ref_data['x1'], ref_data['dx'])).T
            ncl = min(len(np.unique(x2d,axis=0)), ncl)
            title = title+', clustered in '+str(ncl)
            ### Cluster data
            new_data = dataProcessing.cluster_data(x2d, ref_data, ncl)
            source.data = new_data
        else:
            title = title+', not clustered'

        ### Main figure
        p1 = figure(tools=[hover,'save','xpan','wheel_zoom','reset'], title=title, width=1500, height=25*ncl_ref,
                    x_range=(0,xmax), y_range=(min(ncl_ref,nhits)/2+1,0), x_axis_location="above")
        p1.ygrid.visible=False
        p1.yaxis.visible=False
        p1.y_range.callback = myCallback
        p1.hbar(y="y", height=0.4, left="x1", right="x2", source=source,
                color={'field': 'pcent', 'transform': cmap})
        labels_pname1 = LabelSet(x='x1', y='y', text='name', source=source, text_baseline='middle')
        p1.add_layout(labels_pname1)
        plots_l.append(p1)


    ### Page layout
    page = column( plots_l )

    curdoc().add_root(page)

except Exception as e:
    curdoc().clear()
    mess = PreText( text=str(e) )
    curdoc().add_root( mess )
