import psycopg2
import pandas as pd
from app.Uploads import Uploads


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
        Content_list = Uploads.prepare_DB_transmission(level_one_list, chapter_data_dict)
        Uploads.transmission_to_DB(Content_list)
        Hierarchy_list = Uploads.prepare_hierarchy_transmission(level_one_list, one_two_dict, two_three_dict,
                                                                three_four_dict)
        Uploads.hierarchy_transmission_to_DB(Hierarchy_list)
        Uploads.lecture_transmission_to_DB(level_one_list, text.replace("'", ""))

    @staticmethod
    def text_generation(request): # generates the text of a lecture for the learning-page
        select = request.form.get('lectures')
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        result = pd.read_sql_query(f"""SELECT s_content FROM LECTURE WHERE s_lecture='{select}';""", dbconn)
        row_data = list(result.values.tolist())
        text = row_data[0][0]
        return select, text
