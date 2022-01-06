import psycopg2
import pandas as pd
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
    def exec_statement(str): # executes an sql-statement
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        myCursor.execute(str)
        result = myCursor.fetchall()
        dbconn.commit()
        myCursor.close()
        dbconn.close()
        return result

    @staticmethod
    def upload_process(request): #Upload- and Transmission-Process from a docx-document to the content in the Database
        path = Uploads.initial_upload(request)
        text = Uploads.convert_to_html(path)
        MyList = Uploads.parse_html(text)
        chapter_list = Uploads.chapter(MyList)
        level_one_list, level_two_list, level_three_list, level_four_list, level_data_list = Uploads.level(MyList)
        one_two_dict = Uploads.hierarchy(level_one_list, level_two_list)
        two_three_dict = Uploads.hierarchy(level_two_list, level_three_list)
        three_four_dict = Uploads.hierarchy(level_three_list, level_four_list)
        chapter_data_dict = Uploads.hierarchy(chapter_list, level_data_list)
        for i in chapter_data_dict:
            chapter_data_dict[i] = ' '.join(chapter_data_dict[i]).replace("'", "")

        list = []
        list2=[]
        for key, value in chapter_data_dict.items():
            list2.append(qg.generate(str(value)))
            #question_answer_dict, question_answer_list = Uploads.prepare_question_transmission(value)
            question_answer_list=[["Question 1", "Answer 1"], ["Question 2", "Answer 2"]]
            for i in range(len(question_answer_list)):
                new_list=[key]+question_answer_list[i]
                list.append(new_list)

        Content_list = Uploads.prepare_DB_transmission(level_one_list, chapter_data_dict)
        #Uploads.transmission_to_DB(Content_list)
        Hierarchy_list = Uploads.prepare_hierarchy_transmission(level_one_list, one_two_dict, two_three_dict,
                                                                three_four_dict)
        #.hierarchy_transmission_to_DB(Hierarchy_list)
        #Uploads.lecture_transmission_to_DB(level_one_list, text.replace("'", ""))
        #for i in range(len(list)):
        #    Uploads.question_transmission_to_DB(level_one_list[0][0], list[i][0], list[i][1], list[i][2])

        return list2

    @staticmethod
    def text_generation(request): # generates the text of a lecture for the learning-page
        select = request.form.get('lectures')
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        result = pd.read_sql_query(f"""SELECT s_content FROM LECTURE WHERE s_lecture='{select}';""", dbconn)
        row_data = list(result.values.tolist())
        text = row_data[0][0]
        return select, text

    @staticmethod
    def check_if_correct(correct_answer, my_answer): # calculates the similarity between the inserted answer and the correct answer by using TFIDF
        corpus = [my_answer, correct_answer]
        vect = TfidfVectorizer(min_df=1, stop_words="english")
        tfidf = vect.fit_transform(corpus)
        pairwise_similarity = tfidf * tfidf.T
        pairwise_similarity_arr = pairwise_similarity.toarray()
        score = pairwise_similarity_arr[0][1]
        print(score)
        if score > 0.5: # if similarity is greater than 0,5 --> answer is classified as correct
            return True
        else:           # if similarity is less than 0,5 --> answer is classified as false
            return False

    @staticmethod
    def get_question_answer(request): # generates the text of a lecture for the learning-page
        select = request.form.get('lectures')
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        df = pd.read_sql_query(f"""SELECT * FROM QUESTIONS;""", dbconn)
        questions = df.to_dict('records')
        for question in questions:
            if int(pd.read_sql_query(f"""SELECT n_solved FROM question_results WHERE n_question_id={int(question['n_question_id'])};""", dbconn)['n_solved'][0]) == 0:
                return(question)

    @staticmethod
    def get_chapter(id): 
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        chapter = pd.read_sql_query(f"""SELECT s_chapter FROM chapter WHERE n_chapter_id={int(id)};""", dbconn)['s_chapter'][0]
        return chapter

    @staticmethod
    def get_lecture(id): 
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        lecture = pd.read_sql_query(f"""SELECT s_lecture FROM chapter WHERE n_chapter_id={int(id)};""", dbconn)['s_lecture'][0]
        return lecture

