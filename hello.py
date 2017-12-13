from flask import Flask, render_template, redirect, url_for, abort, request, jsonify
import glob
import os
import sys
import subprocess
import atexit

from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField
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
app.url_map.strict_slashes = False
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


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q').upper()
    filelist = sorted(glob.glob(os.path.expanduser('~/data/*.ssw11.hhr')))
    orflist = [os.path.basename(f).split('.')[0].upper() for f in filelist]
    filteredlist = [orf for orf in orflist if search in orf]
    return jsonify(matching_results=filteredlist)

class IndexForm(FlaskForm):
    filename = StringField('autocomplete')


@app.route('/', methods=['POST','GET'])
def index():
    form = IndexForm()
    if form.validate_on_submit():
        filename = form.filename.data
        url = url_for('load_name',filename=filename)
        return redirect(url)
    return render_template('index.html',form=form)

@app.errorhandler(406)
def wrong_case_url(e):
    url = ''
    input_list = e.description.split(' ')
    if len(input_list)==1:
        url = url_for('load_name', filename=input_list[0].upper())
    elif len(input_list)==2:
        url = url_for('load_detail', filename=input_list[0].upper(), db=input_list[1].lower())
    return redirect(url)

@app.route('/<filename>', methods=['POST','GET'])
def load_name(filename):
    if filename!=filename.upper():
        abort(406, filename)

    filepath = os.path.join(os.path.expanduser('~/data'),filename+'.0.ssw11.hhr')
    if os.path.isfile(filepath):
        bokeh_script = server_document(
            url='http://localhost:5006/lolliplotServer', arguments=dict(filename=filepath))

        return render_template(
               'plot.html',
               plot_script=bokeh_script,
               name=filename)
    else:
        return render_template(
            'error.html',
            msg="Data for "+filename+" does not exist. Please choose a different ORF.")

@app.route('/<filename>/<db>')
def load_detail(filename, db):
    if filename!=filename.upper() or db!=db.lower():
        abort(406, filename+" "+db)

    filepath = os.path.join(os.path.expanduser('~/data'),filename+'.0.ssw11.hhr')
    if db in ['pdb', 'pfam', 'yeast']:

        if os.path.isfile(filepath):
           bokeh_script = server_document(
               url='http://localhost:5007/lolliplotServerDetail', arguments=dict(filename=filepath, db=db))
           return render_template(
                  'detail.html',
                  plot_script=bokeh_script,
                  name=filename,
                  db=db )
        else:
           return render_template(
                  'error.html',
       	          msg="Data for "+filename+" does not exist. Please choose a different ORF.")

    else:
        return render_template(
       	       'error.html',
               msg="Data for database "+db+" does not exist. Please choose between pdb, pfam or yeast.")
               
