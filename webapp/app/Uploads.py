import mammoth
from werkzeug.utils import secure_filename
import os
from app import app
from html.parser import HTMLParser
import psycopg2
from app.qg import QuestionGenerator

qg = QuestionGenerator()

uploads_dir = os.path.join(app.root_path, 'Uploaded_Docs')
os.makedirs(uploads_dir, exist_ok=True)
app.config['SECRET_KEY'] = 'mysecretkey'
ALLOWED_EXTENSIONS = {'docx'}

# General Functions
def allowed_file(filename): #Tests if the file-type has an allowed extension
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

MyList = []

class MyHTMLParser(HTMLParser): # Specified Class of general HTML-Parser
    def handle_data(self, data):
        MyList.append([self.get_starttag_text(), data])
        return MyList


class Uploads:

    def __init__(self):
        pass

    @staticmethod
    def initial_upload(request): # Initially uploads the docx-file into an Upload-Folder within the WebApp
        if 'file' not in request.files:
            flash('No file part')
            return render_template("/includes/fail.html", title='Error',
                                   text='No file part')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return render_template("/includes/fail.html", title='Error',
                                   text='No file was selected')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(uploads_dir, filename)
            file.save(path)
        return path

    @staticmethod
    def convert_to_html(path): # converts a docx-file to an HTML-file
        with open(path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file, ignore_empty_paragraphs=False)
            text = result.value
            return text

    @staticmethod
    def parse_html(text): # parses as an HTML-text in order to identify the different tags
        parser = MyHTMLParser()
        parser.feed(text)
        return MyList

    @staticmethod
    def chapter(list): # creates a List of all chapters
        chapters = []
        for i in list:
            if i[0] != '<p>':
                chapters.append([i[1], MyList.index(i)])
        return chapters

    @staticmethod
    def level(list): # identifies the different tags and levels of text
        level_one_list = []
        level_two_list = []
        level_three_list = []
        level_four_list = []
        level_data_list = []
        for i in list:
            if i[0] == '<h1>':
                level_one_list.append([i[1], MyList.index(i)])
            elif i[0] == '<h2>':
                level_two_list.append([i[1], MyList.index(i)])
            elif i[0] == '<h3>':
                level_three_list.append([i[1], MyList.index(i)])
            elif i[0] == '<h4>':
                level_four_list.append([i[1], MyList.index(i)])
            elif i[0] == '<p>':
                level_data_list.append([i[1], MyList.index(i)])
        return level_one_list, level_two_list, level_three_list, level_four_list, level_data_list

    @staticmethod
    def hierarchy(list_one, list_two): # creates an hierarchy-dictionary with superchapters(key) and subchapters(values)
        added_values = []
        hierarchy_dict = {}
        for j in reversed(list_one):
            emptyList = []
            for i in list_two:
                if i[0] not in added_values and i[1] > j[1]:
                    emptyList.append(i[0])
                    added_values.append(i[0])
            hierarchy_dict[j[0]] = emptyList
        return hierarchy_dict

    @staticmethod
    def prepare_DB_transmission(level_one_list, chapter_data_dict): # prepares the chapter-content for the transmission the the database
        lecture = level_one_list[0][0]
        Content_List = []
        for i in chapter_data_dict:
            chapter_data_dict[i] = ' '.join(chapter_data_dict[i]).replace("'", "")
            Content_List.append([lecture, i, chapter_data_dict[i]])
        return Content_List

    @staticmethod
    def transmission_to_DB(Content_List): #fills the Chapter- and Chapter_Result-Tables in the database
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        for i in reversed(Content_List):
            myCursor.execute(f"CALL add_content('{str(i[0])}', '{str(i[1])}', '{str(i[2])}')")
        dbconn.commit()
        myCursor.close()
        dbconn.close()

    @staticmethod
    # prepares the hierarchy-dictionaries for the transmission to the database
    def prepare_hierarchy_transmission(level_one_list, one_two_dict, two_three_dict, three_four_dict):
        lecture = level_one_list[0][0]
        Hierachy_List = []
        for i in one_two_dict:
            if one_two_dict[i] != []:
                for j in one_two_dict[i]:
                    Hierachy_List.append([lecture, i, j])
        for i in two_three_dict:
            if two_three_dict[i] != []:
                for j in two_three_dict[i]:
                    Hierachy_List.append([lecture, i, j])
        for i in three_four_dict:
            if three_four_dict[i] != []:
                for j in three_four_dict[i]:
                    Hierachy_List.append([lecture, i, j])
        return Hierachy_List


    @staticmethod
    def hierarchy_transmission_to_DB(Hierarchy_List): # fills the hierarchy-table in the database
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        for i in Hierarchy_List:
            myCursor.execute(f"CALL add_hierarchy('{str(i[0])}', '{str(i[1])}', '{str(i[2])}')")
        dbconn.commit()
        myCursor.close()
        dbconn.close()

    @staticmethod
    def lecture_transmission_to_DB(level_one_list, text): # fills the lecture-table in the database
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        lecture = level_one_list[0][0]
        myCursor.execute(f"CALL add_lecture('{lecture}', '{text}')")
        dbconn.commit()
        myCursor.close()
        dbconn.close()

    @staticmethod
    def prepare_question_transmission(text):
        #text = "Computational linguistics is an interdisciplinary field concerned with the computational modelling of natural language, as well as the study of appropriate computational approaches to linguistic questions. In general, computational linguistics draws upon linguistics, computer science, artificial intelligence, mathematics, logic, philosophy, cognitive science, cognitive psychology, psycholinguistics, anthropology and neuroscience, among others."
        question_answer_dict = qg.generate(str(text))
        question_answer_list = []
        for i in range(len(question_answer_dict)):
            inner_list = []
            for j in question_answer_dict[i].keys():
                inner_list.append(question_answer_dict[i][j])
            question_answer_list.append(inner_list)
        return question_answer_dict, question_answer_list

    @staticmethod
    def question_transmission_to_DB(lecture, chapter, question, answer):
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        myCursor.execute(f"CALL add_question('{lecture}','{chapter}','{question}', '{answer}')")
        dbconn.commit()
        myCursor.close()
        dbconn.close()


