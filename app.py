from flask import render_template
from flask import Flask
import json

app = Flask(__name__)

@app.route('/')
def render_home():
    return render_template('index.html')



