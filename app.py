from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from contextlib import closing
from datetime import datetime, timedelta
import sqlite3
import os
from werkzeug.utils import secure_filename
import json

# configuration
DATABASE = '/root/rpparser/db/rpparser.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
UPLOAD_FOLDER = '/root/rpparser/uploads'
ALLOWED_EXTENSIONS = set(['json'])

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@app.route('/', methods=['GET', 'POST'])
def inputfile():
    cur = g.db.execute('select filename,partyid,created,modified,id from file_entries order by created desc')
    entries = [dict(filename=row[0], partyid=row[1], created=row[2], modified=row[3]) for row in cur.fetchall()]

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('inputfile'))
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('inputfile'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current = datetime.now()
            g.db.execute('insert into file_entries (filename,partyid,created,modified) values (?, ?, ?, ?)',
                 [file.filename, request.form['partyid'], current, current])
            g.db.commit()
            message = "File upload finished successfully."
            return redirect(url_for('inputfile',message=message))
                                    
    current = datetime.now().strftime('%Y/%m/%d %H:%M')
    message = request.args.get('message','')
    if not message:
        message = "Current time is " + current
    return render_template('inputfile.html', message=message,entries=entries)

@app.route('/current_config')
def current_config():
    fname = request.args.get('value').replace(' ','_')
    fpath = UPLOAD_FOLDER + '/' + fname
    jsonfile = open(fpath,'r')
    config = json.load(jsonfile)
    group_config = config['groupsSettings']
    
    templist=[]
    for x in group_config:
        array = [len(row['journal']['journalVolumes']) for row in x['groupCopiesSettings']]
        a = max(array + [len(x['replicationSetsSettings'])])
        x['rowspan'] = max(1,a)
        x['copynum'] = len(x['groupCopiesSettings'])
        templist = templist + [x['copynum']]
        # rowspan=0 cause problem on HTML.
        copymax = max(templist)
    
    return render_template('current_config.html', entries=group_config, copymax=copymax)
    # return render_template('test2.html', key=group_config)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('inputfile'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')

