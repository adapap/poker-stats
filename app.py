from flask import Flask, render_template

from data import *



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
def load_stats():
    return render_template('stats.html')


