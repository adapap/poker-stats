from flask import Flask, render_template

from stats import *



app = Flask(__name__)

@app.route('/')
@app.route('/tournament')
def tournament():
    """
    The root page, or the tournament page, will allow quickly setting up and running a tournament.
    Features include a blind clock with blind configurations and table randomizer.

    GET:
        
    """
    return render_template('index.html')


@app.route('/stats')
def load_stats(most_finals=most_final_tables("2018F"), most_top3=most_top_3("2018F")):

    return render_template('stats.html', most_finals=most_finals, most_top3=most_top3)





