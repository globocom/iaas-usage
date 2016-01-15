from app import app
from flask import render_template, request
from app.auth.utils import required_login


@app.route('/')
@required_login
def index():
    return render_template('index.html')
