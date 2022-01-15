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
    result = pd.read_sql_query(f"""SELECT * FROM Result_Overview;""", dbconn) # generates an Overview over the completeness-Score per Lecture
    result["completed"] = result["completed"].apply(lambda x: str(x*100)+"%")
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
        LF.upload_process(request) # Upload-Procedure for a docx-document into the database - details in LearningForest.py
        return render_template("/includes/success.html", title='Success',
                                   text="Your Data was succesfully transmitted to the Database.")


@app.route('/learning', methods=['POST', 'GET'])  # Learning - Page
def learning():
    lectures = LF.dropdown_lecture() # Generation of a Dropdown-Menu of the lectures
    return render_template("/learning.html", lectures=lectures)

@app.route('/text', methods=['POST', 'GET']) # Detailed Text from Learning-Page
def text():
    select, text = LF.text_generation(request) # Generates the Text for a specific lecture
    return render_template("includes/text.html", title='Learning', sub_header=select, Text=text)



@app.route('/exercise', methods=['POST', 'GET'])  # Exercise-Page
def exercise():
    lectures = LF.dropdown_lecture() # Dropdown-Menu of Lectures
    return render_template("/exercise.html", lectures=lectures)

@app.route('/initial_exercising', methods=['POST', 'GET'])
def initial_exercising(): # Initial exercising procedure
    global selected_lecture

    selected_lecture = request.form.get('lectures') # takes the lecture, which have been selected on the previous page and sets it as a global variable


    if request.form.get('Start_over') == "Start_over": # If button Start-Over is pushed, the results for the lecture will be reseted
        LF.reset(selected_lecture)  # Otherwise, the Reset-Step will be skipped and you will continue exercising at the same position as before

    Final = LF.check_final(selected_lecture) # Checks, if the exercise-process for a lecture is already finalized
    if Final == True: # If it is finalized, the closing page with result for the lecture will be rendered. Otherwise, normal exercise-process begins.
        result = LF.exercising_done(selected_lecture)
        return render_template("/exercising_done.html",
                               Text="You are already done with the exercises!",
                               color = "green",
                               Result=result)

    lecture, chapter, current_question = LF.get_question(selected_lecture) # question gets generated for current lecture and chapter

    return render_template("/exercising.html",
                            question = current_question,
                            chapter = chapter,
                            lecture = lecture)

@app.route('/further_exercising', methods=['POST', 'GET'])
def further_exercising(): # further exercising process
    global selected_lecture # Accesses the global variable selected_lecture

    lecture, chapter, current_question = LF.get_question(selected_lecture) # generates new questions for current lecture and chapter

    return render_template("/exercising.html",
                           question=current_question,
                           chapter=chapter,
                           lecture=lecture)


@app.route('/checking', methods=['POST', 'GET'])
def checking(): # checking-process is triggered by exercise.html (initial_exercising() and further_exercising())
    global selected_lecture

    if request.form.get('Skip_question')=="Skip_question": # If the Button "Skip Question" is pushed, a new question will be generated
        lecture, chapter, current_question = LF.get_question(selected_lecture)
        return render_template("/exercising.html",
                               question=current_question,
                               chapter=chapter,
                               lecture=lecture)

    elif request.form.get('Start') == "Start": # If the "Submit"-Button is pushed, similarity-score between user-Answer and correct Answer will be calculated
        current_score, correct_answer, user_answer, current_question = LF.check_if_correct(request)

        if current_score > 0.5: # If Score bigger than 0.5 --> Answer was correct
            LF.correct_answer(current_question) # Answer and corresponding chapter will be marked as solved in the databases --> user qualified himself for subchapters, if exist
            current_chapter, sub_chapter, next_chapter = LF.get_chapter_and_subchapter(current_question, selected_lecture) # Sub-chapter and next-chapter get identificated
            if next_chapter == False: # If there is no following chapter, then the exercise-process is finalized
                result = LF.exercising_done(selected_lecture) # Results are calculated and rendered within the closing page
                return render_template("/exercising_done.html",
                                       Text=f"Our algorithm classified your answer as correct! (Score: {current_score})",
                                       color="green",
                                       Chapter_Text=f"You have solved chapter '{current_chapter}'",
                                       Result = result)
            if sub_chapter == []: # If there are no Sub-chapters, correct.html with following text will be rendered
                return render_template("/correct.html",
                                       Text=f"Our algorithm classified your answer as correct! (Score: {current_score})",
                                       Chapter=current_chapter,
                                       Subchapter_Text="",
                                       Next=next_chapter)
            # If there are Sub-chapters, correct.html with following text will be rendered
            Subchapter_string = ', '.join([x[0] for x in sub_chapter])
            return render_template("/correct.html",
                                   Text = f"Our algorithm classified your answer as correct! (Score: {current_score})",
                                   Chapter = current_chapter,
                                   Subchapter_Text = f"You have qualified yourself for the following chapters: {Subchapter_string}",
                                   Next = next_chapter)
        else: # If the score was under 0.5 --> answer is incorrect --> check.html will be rendered
            return render_template("/check.html",
                                Score = current_score,
                                question = current_question,
                                user_answer = user_answer,
                                correct_answer = correct_answer)


@app.route('/evaluating', methods=['POST', 'GET'])
def evaluating(): # evaluating()-function is triggered by check.html --> user can decide, if his answer was indeed wrong or if it was correct
    if request.method == 'POST':
        current_question = request.form.get('question')
        if request.form.get('correct') == 'correct': # if the user classifies his answer as correct
            LF.correct_answer(current_question) # correct-answer-procedure gets triggered --> take a view at the "correct"-part of checking()-function
            current_chapter, sub_chapter, next_chapter = LF.get_chapter_and_subchapter(current_question, selected_lecture)
            if next_chapter == False: # No next chapter --> Exercise-process finalized
                result = LF.exercising_done(selected_lecture)
                return render_template("/exercising_done.html",
                                       Text="You classified your answer as correct!",
                                       color="green",
                                       Chapter_Text=f"You have solved chapter '{current_chapter}'",
                                       Result=result)
            if sub_chapter == []: # No sub-chapters
                return render_template("/correct.html",
                                       Text="You classified your answer as correct!",
                                       Chapter=current_chapter,
                                       Subchapter_Text="",
                                       Next=next_chapter)
            Subchapter_string = ', '.join([x[0] for x in sub_chapter]) # Sub-chapters
            return render_template("/correct.html",
                                   Text="You classified your answer as correct!",
                                   Chapter=current_chapter,
                                   Subchapter_Text=f"You have qualified yourself for the following chapters: {Subchapter_string}",
                                   Next=next_chapter)
        elif request.form.get('incorrect') == 'incorrect': # If the user classifies his response as "incorrect"
            dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
            chapter = pd.read_sql_query(f"""SELECT chapter.s_chapter FROM questions  LEFT JOIN chapter ON questions.n_chapter_id = chapter.n_chapter_id WHERE questions.s_question='{current_question}';""",dbconn)
            chapter = list(chapter.values.tolist())
            chapter = chapter[0][0]
            dbconn.close()
            first_try = LF.check_for_first_try(chapter) # checks, if it was the users first try in this chapter
            LF.false_answer(current_question) # triggers the wrong-answer procedure --> question gets marked as "wrong" (1. Try) --> user disqualifies himself from chapter, if its his second try
            current_chapter, sub_chapter, next_chapter = LF.get_chapter_and_subchapter(current_question, selected_lecture)
            if next_chapter == False: # If there is no next-chapter left, exercise-process is finalized
                result = LF.exercising_done(selected_lecture)
                return render_template("/exercising_done.html",
                                       Text="You classified your answer as false!",
                                       color="red",
                                       Chapter_Text=f"You have been disqualified from chapter '{current_chapter}'",
                                       Result=result)

            if first_try == True: # If it is his first try, he will get a second try
                return render_template("/false.html",
                                       Text= f"This was your first try for chapter '{current_chapter}'. You have one try left.",
                                       Button_Text = f"Try again chapter '{current_chapter}'")
            else: # If it is his second try, he gets disqualificated from the chapter and has to go on to the next-chapter, if available
                return render_template("/false.html",
                                       Text = f"This was your second try. You have disqualified yourself from chapter '{current_chapter}'",
                                       Button_Text=f"Go on to chapter '{next_chapter}'")


