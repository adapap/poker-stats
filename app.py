from flask import Flask, render_template

from stats import *


info = Stats()
app = Flask(__name__)
CURRENT_SEASON = "2018F"

@app.route('/')
@app.route('/tournament')
def tournament():
    """
    The root page, or the tournament page, will allow quickly setting up and running a tournament.
    Features include a blind clock with blind configurations and table randomizer.

    GET:
        
    """
    return render_template('index.html')

@app.route('/profiles')
def load_profile_search(name=None, season=None):

    return render_template("profiles.html")



@app.route('/profiles/<name>')
@app.route('/profiles/<name>/')
def load_profile(name=None, season=CURRENT_SEASON, tournaments=None, best_finish=None, tourn_finish=None, no_finaltables=None):
    names = get_all_names(CURRENT_SEASON)

    if name not in names:
        name = None
    else:
        tourn_finish = get_best_placement(name, CURRENT_SEASON)[0]
        best_finish = get_best_placement(name, CURRENT_SEASON)[1]
        no_finaltables = get_final_tables(name, CURRENT_SEASON)
        tournaments = tournaments_no(name, CURRENT_SEASON)

    return render_template('profilepage.html', name=name, tournaments=tournaments, best_finish=best_finish, tourn_finish=tourn_finish,
                           season=season, no_finaltables=no_finaltables)




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







