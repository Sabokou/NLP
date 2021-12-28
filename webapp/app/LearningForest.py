import psycopg2
import sqlalchemy


class LearningForest:

    def __init__(self):
        pass

    @staticmethod
    def dropdown_lecture():
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
    def exec_statement(str):
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        myCursor.execute(str)
        result = myCursor.fetchall()
        dbconn.commit()
        myCursor.close()
        dbconn.close()
        return result
