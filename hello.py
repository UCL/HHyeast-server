from flask import Flask, render_template, redirect, url_for
import glob
import os
import subprocess
import atexit

from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import SelectField

from bokeh.embed import server_document
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.models import palettes
from bokeh.models import ColumnDataSource, LabelSet, Label
from bokeh.models import HoverTool, CustomJS
from bokeh.models.widgets import Slider, Panel, Tabs, TextInput
from bokeh.layouts import widgetbox, column, layout


app = Flask(__name__)
app.config['SECRET_KEY']='la'
csrf = CSRFProtect(app)


bokeh_process = subprocess.Popen(
    ['bokeh', 'serve', '--allow-websocket-origin=localhost:5000', 'lolliplotServer.py'], stdout=subprocess.PIPE)

@atexit.register
def kill_server():
    bokeh_process.kill()


class MyForm(FlaskForm):
    filelist = glob.glob('/Users/ilektra/HHprY-Project/*.ssw11.hhr')
    filename = SelectField('filename',
                choices = [(os.path.basename(f).split('.')[0], os.path.basename(f).split('.')[0]) for f in filelist])


@app.route('/', methods=['POST','GET'])
def index():
    form = MyForm()
    if form.validate_on_submit():
        filename = form.filename.data
        url = url_for('load_name',filename=filename)
        return redirect(url)
    return render_template('index.html',form=form)

@app.route('/<filename>')
def load_name(filename):
    filepath = os.path.join('/Users/ilektra/HHprY-Project',filename+'.0.ssw11.hhr')
    bokeh_script = server_document(
        url='http://localhost:5006/lolliplotServer', arguments=dict(filename=filepath))

    html = render_template(
        'plot.html',
        plot_script=bokeh_script,
        name=filename )

    return html

