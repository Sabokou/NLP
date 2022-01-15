import psycopg2
import pandas as pd
import random
from app.Uploads import Uploads
from sklearn.feature_extraction.text import TfidfVectorizer
from app.qg import QuestionGenerator

qg = QuestionGenerator()



class LearningForest:

    def __init__(self):
        pass

    @staticmethod
    def dropdown_lecture(): # Creates a Dropdown-Menu with the distinct lectures uploaded
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        myCursor.execute("SELECT DISTINCT(s_lecture) FROM CHAPTER ORDER BY s_lecture")
        lectures = []
        lecture_list = myCursor.fetchall()
        for i in lecture_list:
            lectures.append(i[0])
        dbconn.commit()
        myCursor.close()
        dbconn.close()
        return lectures


    @staticmethod
    def upload_process(request): #Upload- and Transmission-Process from a docx-document to the content in the Database
        path = Uploads.initial_upload(request) # Initial Upload from docx-document to a path
        html_text = Uploads.convert_to_html(path) # Conversion from docx to html
        MyList = Uploads.parse_html(html_text) # Parsing of HTML-Text in order to detect specific tags and text
        chapter_list = Uploads.chapter(MyList) # Creation of an overview over the chapter
        level_one_list, level_two_list, level_three_list, level_four_list, level_data_list = Uploads.level(MyList) # Assignment of the levels to the chapters
        # Creation of hierarchies between different chapter-levels
        one_two_dict = Uploads.hierarchy(level_one_list, level_two_list)
        two_three_dict = Uploads.hierarchy(level_two_list, level_three_list)
        three_four_dict = Uploads.hierarchy(level_three_list, level_four_list)
        chapter_data_dict = Uploads.hierarchy(chapter_list, level_data_list) # Assignment of text to chapter
        qa_list = Uploads.prepare_question_transmission(chapter_data_dict) # Generation of Questions and Answers per Chapter
        # Preperation of the Chapter-content for the transmission to the DB
        Content_list = Uploads.prepare_DB_transmission(level_one_list, chapter_data_dict)
        # Transmission of content to DB - procedure: add_content() - table: CHAPTER, CHAPTER_RESULTS
        Uploads.transmission_to_DB(Content_list)
        # Preparation of hierarchies for transmission to DB
        Hierarchy_list = Uploads.prepare_hierarchy_transmission(level_one_list, one_two_dict, two_three_dict, three_four_dict)
        # Transmission of Hierarchies to DB - procedure: add_hierarchy() - table: HIERARCHY
        Uploads.hierarchy_transmission_to_DB(Hierarchy_list)
        # Transmission of the lecture and the HTML-Text to DB - procedure: add_lecture() - table: LECTURE
        Uploads.lecture_transmission_to_DB(level_one_list, html_text)
        # Transmission of the questions and answers to DB - procedure: add_question() - table: QUESTIONS, QUESTION_RESULTS
        Uploads.question_transmission_to_DB(level_one_list, qa_list)


    @staticmethod
    def text_generation(request): # generates the text of a lecture for the learning-page
        select = request.form.get('lectures')
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        result = pd.read_sql_query(f"""SELECT s_content FROM LECTURE WHERE s_lecture='{select}';""", dbconn)
        row_data = list(result.values.tolist())
        text = row_data[0][0]
        dbconn.close()
        return select, text

    @staticmethod
    def reset(select): # Resets the lecture-exercise-process
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        # All questions and chapters are marked as unsolved --> Qualification only for the first Super-Chapter
        myCursor.execute(f"CALL reset('{select}')")
        dbconn.commit()
        myCursor.close()
        dbconn.close()

    @staticmethod
    def get_question(select): # Generation-process to get a random question for a current chapter
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        # Evaluation of the next chapter, the use has to work on
        next_chapter = pd.read_sql_query(f"""SELECT Chapter FROM Valid_Question_Overview WHERE Lecture='{select}' ORDER BY Chapter_id;""", dbconn)
        next_chapter = list(next_chapter.values.tolist())
        next_chapter = next_chapter[0][0]
        # Selection of a random question within the selected chapter
        result = pd.read_sql_query(f"""SELECT Question FROM Valid_Question_Overview WHERE Lecture='{select}' AND Chapter = '{next_chapter}';""", dbconn)
        questions = list(result.values.tolist())
        question = random.choice(questions)
        question = question[0]
        dbconn.close()
        return select, next_chapter, question

    @staticmethod
    def check_if_correct(request):  # calculates the similarity between the inserted answer and the correct answer by using TFIDF
        my_answer = request.form.get('answer')
        question = request.form.get('question')
        # Selection of the correct answer
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        result = pd.read_sql_query(f"""SELECT s_answer FROM questions WHERE s_question='{question}';""", dbconn)
        correct_answers = list(result.values.tolist())
        correct_answer = correct_answers[0][0]

        # Calculation of the similarity-score by using TFIDF
        corpus = [my_answer, correct_answer]
        vect = TfidfVectorizer(min_df=1, stop_words="english")
        tfidf = vect.fit_transform(corpus)
        pairwise_similarity = tfidf * tfidf.T
        pairwise_similarity_arr = pairwise_similarity.toarray()
        score = pairwise_similarity_arr[0][1]
        score = round(score, 2)
        return score, correct_answer, my_answer, question

    @staticmethod
    def get_chapter_and_subchapter(current_question, selected_lecture): # Function to access the current chapter, next chapter and sub-chapter
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        chapter = pd.read_sql_query(f"""SELECT chapter.s_chapter FROM questions  LEFT JOIN chapter ON questions.n_chapter_id = chapter.n_chapter_id WHERE questions.s_question='{current_question}';""", dbconn)
        chapter = list(chapter.values.tolist())
        chapter = chapter[0][0]
        subchapter = pd.read_sql_query(f"""SELECT sub_chapter FROM named_hierarchy_2 WHERE super_chapter = '{chapter}' """, dbconn)
        subchapter = list(subchapter.values.tolist())
        next_chapter = pd.read_sql_query(f"""SELECT Chapter FROM Valid_Question_Overview WHERE Lecture='{selected_lecture}' ORDER BY Chapter_id;""", dbconn)
        next_chapter = list(next_chapter.values.tolist())
        dbconn.close()
        if next_chapter != []:
            next_chapter = next_chapter[0][0]
            return chapter, subchapter, next_chapter
        else:
            return chapter, subchapter, False

    @staticmethod
    def check_final(selected_lecture): # Checks, if the exercise-process is finalized
        # Tries to evaluate the next-chapter
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        next_chapter = pd.read_sql_query(f"""SELECT Chapter FROM Valid_Question_Overview WHERE Lecture='{selected_lecture}' ORDER BY Chapter_id;""",dbconn)
        next_chapter = list(next_chapter.values.tolist())
        dbconn.close()
        # If there is no next-chapter --> Exercise-process is finalizes --> else: Not finalized
        if next_chapter == []:
            return True
        else:
            return False

    @staticmethod
    def correct_answer(question): # calls stored_procedure correct_answer()
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        # Question and chapter gets marked as solved --> Qualification for Sub-Chapters, if available
        myCursor.execute(f"CALL correct_answer('{question}')")
        dbconn.commit()
        myCursor.close()
        dbconn.close()
        return True

    @staticmethod
    def false_answer(question): # calls stored procedure wrong_answer()
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        # Question-Answer gets marked as false --> if it was the second try, user is also disqualificated from the chapter
        myCursor.execute(f"CALL wrong_answer('{question}')")
        dbconn.commit()
        myCursor.close()
        dbconn.close()
        return True

    @staticmethod
    def check_for_first_try(current_chapter): # checks, is it was the first try of the user
        # tries to calculate a question within the chapter, which has been answered wrongly before
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        question = pd.read_sql_query(f"""SELECT Question_id FROM Wrong_Chapter_Question_Overview WHERE Chapter='{current_chapter}';""",dbconn)
        question = list(question.values.tolist())
        dbconn.close()
        # If there is no question --> first try --> else: second try
        if question == []:
            return True
        else:
            return False




    @staticmethod
    def exercising_done(selected_lecture): # calculates the completeness-rate of a lecture, if the exercising-process is finalized
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        result = pd.read_sql_query(f"""SELECT completed FROM Result_Overview WHERE lecture='{selected_lecture}';""", dbconn)
        result = list(result.values.tolist())
        result = result[0][0]*100
        return result

