from flask import render_template, request, flash, redirect, url_for
from app import app
from app.LearningForest import LearningForest
import pandas as pd
import psycopg2

LF = LearningForest()


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
    if request.method == 'POST':
        if request.form['btn_start'] == 'start':
            question = LF.get_question_answer(request)
            chapter = LF.get_chapter(question['n_chapter_id'])
            lecture = LF.get_lecture(question['n_chapter_id'])
            return render_template("/exercising.html",
                                    question = question,
                                    chapter = chapter,
                                    lecture = lecture)


@app.route('/checking', methods=['POST', 'GET'])
def checking():
    return render_template("/checking.html")

