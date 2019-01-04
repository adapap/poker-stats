from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/tournament')
def tournament():
    """
    The root page, or the tournament page, will allow quickly setting up and running a tournament.
    Features include a blind clock with blind configurations and table randomizer.

    GET:
        
    """
    return 'Tournament Page'