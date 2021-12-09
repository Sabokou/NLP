from flask import render_template
from app import app


@app.route('/')  # Overview
def index():
    return render_template("/index.html")

@app.route('/learning', methods=['POST', 'GET'])  # Learning
def learning():
    return render_template("/learning.html")

@app.route('/exercise', methods=['POST', 'GET'])  # Exercise
def exercise():
    return render_template("/exercise.html")

