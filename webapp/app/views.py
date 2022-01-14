from sys import _current_frames
from flask import render_template, request, flash, redirect, url_for
from numpy import quantile
from app import app
from app.LearningForest import LearningForest
import pandas as pd
import psycopg2

LF = LearningForest()

#defining global variables
selected_lecture = ""


# Page Functions
@app.route('/')  # Overview - Page
def overview():
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

@app.route('/initial_exercising', methods=['POST', 'GET'])
def initial_exercising():
    global selected_lecture

    selected_lecture = request.form.get('lectures')
    lecture, chapter, current_question = LF.get_question(selected_lecture)

    return render_template("/exercising.html",
                            question = current_question,
                            chapter = chapter,
                            lecture = lecture)

@app.route('/further_exercising', methods=['POST', 'GET'])
def further_exercising():
    global selected_lecture

    lecture, chapter, current_question = LF.get_question(selected_lecture)

    return render_template("/exercising.html",
                           question=current_question,
                           chapter=chapter,
                           lecture=lecture)


@app.route('/checking', methods=['POST', 'GET'])
def checking():
    current_score, correct_answer, user_answer, current_question = LF.check_if_correct(request)


    if current_score > 0.5:
        LF.correct_answer(current_question)
        current_chapter, sub_chapter, next_chapter = LF.get_chapter_and_subchapter(current_question, selected_lecture)
        if next_chapter == False:
            result = LF.exercising_done(selected_lecture)
            return render_template("/exercising_done_positive.html",
                                   Text=f"Our algorithm classified your answer as correct! (Score: {current_score})",
                                   Chapter=current_chapter,
                                   Result = result)
        if sub_chapter == []:
            return render_template("/correct.html",
                                   Text=f"Our algorithm classified your answer as correct! (Score: {current_score})",
                                   Chapter=current_chapter,
                                   Subchapter_Text="",
                                   Next=next_chapter)
        return render_template("/correct.html",
                               Text = f"Our algorithm classified your answer as correct! (Score: {current_score})",
                               Chapter = current_chapter,
                               Subchapter_Text = f"You have qualified yourself for the following chapters: {sub_chapter}",
                               Next = next_chapter)
    else:
        return render_template("/check.html",
                            Score = current_score,
                            question = current_question,
                            user_answer = user_answer,
                            correct_answer = correct_answer)


@app.route('/evaluating', methods=['POST', 'GET'])
def evaluating():
    if request.method == 'POST':
        current_question = request.form.get('question')
        if request.form.get('correct') == 'correct':
            LF.correct_answer(current_question)
            current_chapter, sub_chapter, next_chapter = LF.get_chapter_and_subchapter(current_question, selected_lecture)
            if next_chapter == False:
                result = LF.exercising_done(selected_lecture)
                return render_template("/exercising_done_positive.html",
                                       Text="You classified your answer as correct!",
                                       Chapter=current_chapter,
                                       Result=result)
            if sub_chapter == []:
                return render_template("/correct.html",
                                       Text="You classified your answer as correct!",
                                       Chapter=current_chapter,
                                       Subchapter_Text="",
                                       Next=next_chapter)
            return render_template("/correct.html",
                                   Text="You classified your answer as correct!",
                                   Chapter=current_chapter,
                                   Subchapter_Text=f"You have qualified yourself for the following chapters: {sub_chapter}",
                                   Next=next_chapter)
        elif request.form.get('incorrect') == 'incorrect':
            dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
            chapter = pd.read_sql_query(f"""SELECT chapter.s_chapter FROM questions  LEFT JOIN chapter ON questions.n_chapter_id = chapter.n_chapter_id WHERE questions.s_question='{current_question}';""",dbconn)
            chapter = list(chapter.values.tolist())
            chapter = chapter[0][0]
            dbconn.close()
            first_try = LF.check_for_first_try(chapter)
            LF.false_answer(current_question)
            current_chapter, sub_chapter, next_chapter = LF.get_chapter_and_subchapter(current_question, selected_lecture)
            if next_chapter == False:
                result = LF.exercising_done(selected_lecture)
                return render_template("/exercising_done_negative.html",
                                       Text="You classified your answer as false!",
                                       Chapter=current_chapter,
                                       Result=result)

            if first_try == True:
                return render_template("/false.html",
                                       Text= f"This was your first try for chapter {current_chapter}. You have one try left.",
                                       Button_Text = f"Try again chapter {current_chapter}")
            else:
                return render_template("/false.html",
                                       Text = f"This was your second try. You have disqualified yourself from chapter {current_chapter}",
                                       Button_Text=f"Go on to chapter {next_chapter}")


