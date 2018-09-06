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
import os

pal = palettes.brewer['YlOrRd'][8]
pal.reverse()
cmap = LinearColorMapper(palette=pal, low=50, high=100)

try:
    # Retrieving the arguments
    args = curdoc().session_context.request.arguments
    filename = args.get('filename')[0].decode("utf-8")
    prob_cutoff = float(args.get('prob')[0].decode("utf-8"))
    ov_min = int(args.get('ov_min')[0].decode("utf-8"))
    ov_min_r = float(args.get('ov_min_r')[0].decode("utf-8"))

    ### Read data
    xmax = 0
    dbname_l = []
    ref_data_l = []
    source_l = []
    dbs = ['pdb', 'pfam', 'yeast']
    xmax, nhitsALL, hitList = dataProcessing.parse_file(filename, prob_cutoff) # Get all hits
    protein = os.path.basename(filename).split('.')[0].upper()
    # Loop over databases
    for db in dbs:
        nhits, ref_data = dataProcessing.fill_data_dict(nhitsALL, hitList, db, protein, False)
        if nhits!=0:
            dbname_l.append(db.upper())
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
                     ("Number of hits in cluster", "@nhits"),
                     ("Highest probability hit", "@detail"),
                     ("Template HMM", "@x1t-@x2t (@dxt)") ]
    )

    page = column()
    ncl_ref = 10
    plots_l = []
    for dbname, ref_data, source in zip(dbname_l, ref_data_l, source_l):
        title = 'Clustered matches to database '+dbname
        ### Cluster data
        new_data, ncl = dataProcessing.cluster_data(ref_data, ov_min, ov_min_r)
        source.data = new_data

        ### Main figure
        p1 = figure(tools=[hover,'save','xpan','wheel_zoom','reset'], title=title,
                    width=1500, height=25*max(ncl_ref,ncl),
                    x_range=(0,xmax), y_range=(max(ncl_ref,ncl)/2+1,0), x_axis_location="above")
        p1.ygrid.visible=False
        p1.yaxis.visible=False
        p1.y_range.callback = myCallback
        p1.hbar(y="y", height=0.4, left="x1", right="x2", source=source,
                color={'field': 'pcent', 'transform': cmap})
        labels_pname1 = LabelSet(x='x1', y='y', text='name', source=source, text_baseline='middle', text_color='black')
        p1.add_layout(labels_pname1)
        plots_l.append(p1)


    ### Page layout
    page = column( plots_l, sizing_mode='scale_width')

    curdoc().add_root(page)

except Exception as e:
    curdoc().clear()
    mess = PreText( text=str(e) )
    curdoc().add_root( mess )
