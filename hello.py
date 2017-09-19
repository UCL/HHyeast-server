from flask import Flask, render_template, redirect, url_for
import glob
import os
import subprocess
import atexit

from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import SelectField, SubmitField
import context_processors as cp

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
cp.setup(app)


bokeh_process1 = subprocess.Popen(
    ['bokeh', 'serve', '--allow-websocket-origin=localhost:5000', 'lolliplotServer.py'], stdout=subprocess.PIPE)
bokeh_process2 = subprocess.Popen(
    ['bokeh', 'serve', '--allow-websocket-origin=localhost:5000', '--port=5007', 'lolliplotServerDetail.py'], stdout=subprocess.PIPE)

@atexit.register
def kill_server():
    bokeh_process1.kill()
    bokeh_process2.kill()


class IndexForm(FlaskForm):
    filelist = glob.glob('/Users/ilektra/HHprY-Project/*.ssw11.hhr')
    filename = SelectField('filename',
                choices = [(os.path.basename(f).split('.')[0], os.path.basename(f).split('.')[0]) for f in filelist])

class DetailForm(FlaskForm):
    button = SubmitField()


@app.route('/', methods=['POST','GET'])
def index():
    form = IndexForm()
    if form.validate_on_submit():
        filename = form.filename.data
        url = url_for('load_name',filename=filename)
        return redirect(url)
    return render_template('index.html',form=form)

@app.route('/<filename>', methods=['POST','GET'])
def load_name(filename):
    filepath = os.path.join('/Users/ilektra/HHprY-Project',filename+'.0.ssw11.hhr')
    bokeh_script = server_document(
        url='http://localhost:5006/lolliplotServer', arguments=dict(filename=filepath))

    form1 = DetailForm()
    if form1.validate_on_submit():
        url = url_for('load_detail', filename=filename, db='pdb')
        return redirect(url)
    form2 = DetailForm()
    if form2.validate_on_submit():
        url = url_for('load_detail', filename=filename, db='pfam')
        return redirect(url)
    form3 = DetailForm()
    if form3.validate_on_submit():
        url = url_for('load_detail', filename=filename, db='yeast')
        return redirect(url)

    html = render_template(
        'plot.html',
        plot_script=bokeh_script,
        name=filename,
        form1=form1,
        form2=form2,
        form3=form3)

    return html

@app.route('/<filename>/<db>')
def load_detail(filename, db):
    filepath = os.path.join('/Users/ilektra/HHprY-Project',filename+'.0.ssw11.hhr')
    bokeh_script = server_document(
        url='http://localhost:5007/lolliplotServerDetail', arguments=dict(filename=filepath, db=db))

    html = render_template(
        'detail.html',
        plot_script=bokeh_script,
        name=filename )

    return html
