from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.models import palettes
from bokeh.layouts import widgetbox, column, layout, gridplot
from bokeh.models.widgets import Slider, Panel, Tabs, TextInput, PreText
from bokeh.models import HoverTool, CustomJS

import numpy as np
import dataProcessing

import sys

pal_seq = palettes.brewer['YlOrRd'][8]
pal_seq.reverse()
pal_cat = palettes.brewer['Paired'][5]
cmap = LinearColorMapper(palette=pal_seq, low=50, high=100)

try:
    # Retrieving the arguments
    args = curdoc().session_context.request.arguments
    filename = args.get('filename')[0]
    db = args.get('db')[0].decode("utf-8")

    ### Read data
    prob_cutoff = 0.5
    xmax, nhits, ref_data = dataProcessing.parse_file(filename, prob_cutoff, db)
    source = ColumnDataSource( data=dict(ref_data) ) # source holds a COPY of the ref_data dict


    ### Tooltip
    hover = HoverTool(
        tooltips = [ ("Hit", "@detail"),
                     ("Query HMM", "@x1-@x2"),
                     ("Template HMM", "@x1t-@x2t (@dxt)") ]
        )

    ### Main figure
    ymax = 10
    p = figure(tools=[hover,'save','pan','wheel_zoom','undo','redo','reset'], width=1500, height=25*max(nhits,ymax),
               x_range=(0,xmax), y_range=(max(nhits,ymax)/2+1,0), x_axis_location="above")
    p.ygrid.visible=False
    p.yaxis.visible=False
    ### Need this callback mechanism in order to update the plots when reading new probThr
    myCallback = CustomJS(code="""
        window.dispatchEvent(new Event('resize'));
    """)
    p.y_range.callback = myCallback
    ###
    p.hbar(y="y", height=0.4, left="x1", right="x2", source=source,
           color={'field': 'pcent', 'transform': cmap})
    labels_pname = LabelSet(x='xm', y='y', text='name', source=source,
                            text_align='center', text_baseline='middle', text_font_size='1vmin')
    p.add_layout(labels_pname)

    ### clustering textInput widgets
    om_def = 10
    om_def1 = 0.1
    ov_min_text = TextInput(value=str(om_def), title="Cluster edges overlap range (residues):")
    ov_min1_text = TextInput(value=str(om_def1), title="Cluster edges overlap range (ratio):")
    ### Multi-textInput interaction
    def reset_values():
        global ref_data
        threshold_text.value = str(p_def)
        ov_min_text.value = str(om_def)
        ov_min1_text.value = str(om_def1)
        source.data = ref_data
    def c_update():
        global ref_data
        try:
            ov_min = float(ov_min_text.value)
        except ValueError:
            reset_values()
            return
        try:
            ov_min1 = float(ov_min1_text.value)
        except ValueError:
            reset_values()
            return
        clabels_l, ncl = dataProcessing.cluster_pred(ref_data['x1'], ref_data['x2'], ov_min, ov_min1)
        clabels = np.array(clabels_l)
        source.data['pcent'] = (clabels+1)*100./float(ncl)
        source.data['name'] = clabels_l
        cmap.palette=pal_cat
        cmap.low = 0
    c_controls = [ov_min_text, ov_min1_text]
    for cc in c_controls:
        cc.on_change("value", lambda attr, old, new: c_update())

    ### probability textInput widget
    p_def = 0.5
    threshold_text = TextInput(value=str(p_def), title="Probability threshold:")
    ### Data-textInput interaction
    def text_handler2(attrname, old, new):
        global ref_data, p, prob_cutoff
        global filename
        try:
            prob_cutoff = float(threshold_text.value)
        except ValueError:
            reset_values()
            return
        xmax, nhits, ref_data = dataProcessing.parse_file(filename, prob_cutoff, db)
        cmap.low = prob_cutoff*100
        p.height = 25*max(nhits,ymax)
        p.y_range.start = nhits/2+1
        source.data = ref_data
        ov_min_text.value = str(om_def)
        ov_min1_text.value = str(om_def1)
    threshold_text.on_change("value", text_handler2)


    ### Page layout
    page = gridplot( [widgetbox(ov_min_text, ov_min1_text, threshold_text)], [p] )
    curdoc().add_root(page)

except Exception as e:
    curdoc().clear()
    mess = PreText( text=str(e) )
    curdoc().add_root( mess )
