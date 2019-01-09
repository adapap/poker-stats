# Dependencies
import logging
import os
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_scss import Scss
from werkzeug.utils import secure_filename

# Local
from stats import *
from randomizer import *

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

# Pug - HTML Template Engine
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')
# Sass - CSS Preprocessor
Scss(app, static_dir='static/css', asset_dir='static/Scss')

info = Stats()
CURRENT_SEASON = "2018F"
# Format: SB, BB, Ante, Time (min.)
DEFAULT_BLINDS = [
    [10, 20, 0, 0.2],
    [25, 50, 1, 0.35]

]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in 'csv'

@app.route('/')
@app.route('/tournament')
def tournament():
    """
    The root page, or the tournament page, will allow quickly setting up and running a tournament.
    Features include a blind clock with blind configurations and table randomizer.

    GET:
        Incomplete.
    """
    return render_template('index.html')

@app.route('/profiles')
def load_profile_search(name=None, season=None):

    return render_template("profiles.html")



@app.route('/profiles/<name>/')
def load_profile(name=None, season=CURRENT_SEASON, tournaments=None, best_finish=None, tourn_finish=None, no_finaltables=None, results=None):
    names = get_all_names(CURRENT_SEASON)

    if name not in names:
        name = None
    else:
        tourn_finish = get_best_placement(name, CURRENT_SEASON)[0]
        best_finish = get_best_placement(name, CURRENT_SEASON)[1]
        no_finaltables = get_final_tables(name, CURRENT_SEASON)
        tournaments = tournaments_no(name, CURRENT_SEASON)
        results = get_results(name, CURRENT_SEASON)

    return render_template('profilepage.html', name=name, tournaments=tournaments, best_finish=best_finish, tourn_finish=tourn_finish,
                           season=season, no_finaltables=no_finaltables, results=results)




@app.route('/search')
@app.route('/search/<name>')
def search(name=None, response=None, name_list=None):
    if not name:
        response = "Please enter a valid name."
        return render_template('search.html', name=name, response=response)
    if len(name) < 3:
        response = "Make sure your search is at least 3 characters."
    else:
        name_list = get_names(name, CURRENT_SEASON)
        if len(name_list) > 0:
            response = "successful"
        else:
            response = "No results found."

    return render_template('search.html', name=name, response=response, name_list=name_list)


@app.route('/stats')
def load_stats(most_finals=most_final_tables(CURRENT_SEASON), most_top3=most_top_3(CURRENT_SEASON),
               best_sum=sum_of_placements(CURRENT_SEASON),
               most_consecutive=most_consecutive_finals(CURRENT_SEASON)):

    return render_template('stats.html', most_finals=most_finals, most_top3=most_top3,
                           best_sum=best_sum, most_consecutive=most_consecutive)


@app.route('/clock')
def clock():
    """
    The clock starts at a default value and has a given blind structure.
    The structure must include SB, BB, ante, and duration values (min).

    GET:
        Loads the tournament clock with the default blind structure.
    """
    
    return render_template('clock.pug', blinds=DEFAULT_BLINDS)


@app.route('/randomizer', methods=['GET', 'POST'])
def randomizer():

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded.')
            return redirect(request.url)
        file = request.files['file']
        if not file.filename:
            flash('No file uploaded')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            names = concatenate(file)

            return redirect(url_for('upload_page',
                                    filename=filename))

    return render_template('randomizer.html')


@app.route('/upload')
def upload_page():
    return render_template('upload.html')