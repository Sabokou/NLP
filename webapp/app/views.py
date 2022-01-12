from sys import _current_frames
from flask import render_template, request, flash, redirect, url_for
from numpy import quantile
from app import app
from app.LearningForest import LearningForest
import pandas as pd
import psycopg2

LF = LearningForest()

#defining global variables
user_answer = ""
correct_answer = ""
selected_lecture = ""
current_question = ""

# Page Functions
@app.route('/')  # Overview - Page
def index():
    dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
    result = pd.read_sql_query(f"""SELECT * FROM Result_Overview;""", dbconn)
    return render_template("includes/table.html", column_names=result.columns.values,
                                   row_data=list(result.values.tolist()),
                                   title='Overview', sub_header="Your Results:", link_column='none',
                                   zip=zip)

@app.route('/upload', methods=['POST', 'GET'])  # Upload - Page
def upload():
    return render_template("/upload.html")

@app.route('/uploader', methods = ['GET', 'POST']) # Success-Page after an Document has been upload
def uploading_file():
   if request.method == 'POST':
        LF.upload_process(request)
        return render_template("/includes/success.html", title='Success',
                                   text="Your Data was successfully transmitted to the Database")


@app.route('/learning', methods=['POST', 'GET'])  # Learning - Page
def learning():
    lectures = LF.dropdown_lecture()
    return render_template("/learning.html", lectures=lectures)

@app.route('/text', methods=['POST', 'GET']) # Detailed Text from Learning-Page
def text():
    select, text = LF.text_generation(request)
    return render_template("includes/text.html", title='Learning', sub_header=select, Text=text)



@app.route('/exercise', methods=['POST', 'GET'])  # Exercise-Page
def exercise():
    lectures = LF.dropdown_lecture()
    return render_template("/exercise.html", lectures=lectures)

@app.route('/exercising', methods=['POST', 'GET'])
def exercising():
    global selected_lecture
    global current_question
    lecture, chapter, current_question = LF.get_question(request.form.get('lectures'))
    selected_lecture = lecture

    return render_template("/exercising.html",
                            question = current_question,
                            chapter = chapter,
                            lecture = lecture)

@app.route('/exercising2', methods=['POST', 'GET'])
def exercising2():
    global selected_lecture
    global current_question

    #for check:
    if request.method == 'POST':
        if request.form['correct'] == 'correct':
            LF.correct_answer(current_question)

    lecture, chapter, current_question = LF.get_question(selected_lecture)
    return render_template("/exercising.html",
                            question = current_question,
                            chapter = chapter,
                            lecture = lecture)

@app.route('/checking', methods=['POST', 'GET'])
def checking():
    global user_answer
    global correct_answer
    global current_question

    feedback, correct_answer, user_answer = LF.check_if_correct(request)

    if feedback == True:
        LF.correct_answer(current_question)
        return render_template("/correct.html")
    else:
        LF.false_answer(current_question)
        return render_template("/false.html")

@app.route('/check', methods=['POST', 'GET'])
def check():
    global user_answer
    global correct_answer
    return render_template("/check.html",
                            user_answer = user_answer,
                            correct_answer = correct_answer)

@app.route('/false', methods=['POST', 'GET'])
def false():
    global current_question
    LF.false_answer(current_question)
    return render_template("/false2.html")