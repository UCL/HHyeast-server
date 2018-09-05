from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.models import palettes
from bokeh.layouts import widgetbox, column, layout, gridplot
from bokeh.models.widgets import TextInput, Button, PreText, Div
from bokeh.models import HoverTool, CustomJS

import numpy as np
import dataProcessing
import nameProcessing as namep

import sys
import os

pal_seq = palettes.brewer['YlOrRd'][8]
pal_seq.reverse()
pal_cat = palettes.brewer['Paired'][5]
cmap = LinearColorMapper(palette=pal_seq, low=50, high=100)

try:
    # Retrieving the arguments
    args = curdoc().session_context.request.arguments
    filename = args.get('filename')[0].decode("utf-8")
    orf = os.path.basename(filename).split('.')[0].upper()
    orf = namep.standard_name(orf)
    db = args.get('db')[0].decode("utf-8")

    ### Read data
    prob_def = 0.5
    prob_cutoff = prob_def
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
                            text_align='center', text_baseline='middle', text_color='black')
    p.add_layout(labels_pname)


    ### probability textInput widget
    threshold_text = TextInput(value=str(prob_def), title="Probability threshold:")
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
        cmap.palette = pal_seq
        p.height = 25*max(nhits,ymax)
        p.y_range.start = nhits/2+1
        source.data = ref_data
        ov_min_text.value = str(om_def)
        ov_min1_text.value = str(om_def1)
    threshold_text.on_change("value", text_handler2)


    ### clustering textInput and button widgets
    om_def = 10
    om_def1 = 0.1
    ov_min = om_def
    ov_min1 = om_def1
    ov_min_text = TextInput(value=str(om_def), title="Hit edges overlap tolerance (number of residues):")
    ov_min1_text = TextInput(value=str(om_def1), title="Hit edges overlap tolerance (length ratio):")
    preview_clust_button = Button(label="Preview clustering", button_type="primary")
    reset_button = Button(label="Reset", button_type="primary")
    ### Multi-textInput interaction
    def reset_values():
        global ref_data
        threshold_text.value = str(prob_def)
        ov_min_text.value = str(om_def)
        ov_min1_text.value = str(om_def1)
        source.data = ref_data
        cmap.low = 50
        cmap.palette = pal_seq
    def read_values():
        global ov_min, ov_min1
        try:
            ov_min = int(ov_min_text.value)
        except ValueError:
            reset_values()
            return
        try:
            ov_min1 = float(ov_min1_text.value)
        except ValueError:
            reset_values()
            return
    def c_update():
        global ref_data, ov_min, ov_min1
        clabels_l, ncl = dataProcessing.cluster_pred(ref_data['x1'], ref_data['x2'], ov_min, ov_min1)
        clabels = np.array(clabels_l)
        source.data['pcent'] = (clabels+1)*100./float(ncl)
        source.data['name'] = [name.split('%')[0]+"% : cluster: "+str(cluster) for name, cluster in zip(source.data['name'],clabels_l)]
        cmap.palette=pal_cat
        cmap.low = 0
    def f_update():
        global orf, prob_cutoff, ov_min, ov_min1
        button = curdoc().get_model_by_name('goto_summary_button')
        button.text = '''<form name="Goto_summary" action="/'''+orf+'''" method="get">
        <input type="hidden" name="prob" id="prob" value="'''+str(prob_cutoff)+'''" />
        <input type="hidden" name="ovm" id="ovm" value="'''+str(ov_min)+'''" />
        <input type="hidden" name="ovm1" id="ovm1" value="'''+str(ov_min1)+'''" />
        <button type="submit">Go to summary view</button>
        </form>'''
    def preview():
        read_values()
        c_update()
        f_update()

    c_controls = [ov_min_text, ov_min1_text]
    for cc in c_controls:
        cc.on_change("value", lambda attr, old, new: read_values())
    preview_clust_button.on_click(preview)
    reset_button.on_click(reset_values)

    ### Page layout
    cl_title = Div( text="<h3>Clustering parameters:</h3>" )
    empty_vert = Div( text="<br><br>" )
    goto_summary_button = Div(text='''<form name="Goto_summary" action="/'''+orf+'''" method="get">
    <input type="hidden" name="prob" id="prob" value="'''+str(prob_def)+'''"/>
    <input type="hidden" name="ovm" id="ovm" value="'''+str(om_def)+'''" />
    <input type="hidden" name="ovm1" id="ovm1" value="'''+str(om_def1)+'''" />
    <button type="submit">Go to summary view</button>
    </form>''', name='goto_summary_button')
    page = layout( [widgetbox(threshold_text),
                    widgetbox(cl_title, ov_min_text, ov_min1_text),
                    widgetbox(empty_vert, preview_clust_button, reset_button),
                    widgetbox(goto_summary_button)],
                   [p],
                   sizing_mode='scale_width' )
    curdoc().add_root(page)

except Exception as e:
    curdoc().clear()
    mess = PreText( text=str(e) )
    curdoc().add_root( mess )
