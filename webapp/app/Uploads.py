import mammoth
from werkzeug.utils import secure_filename
import os
from app import app
from html.parser import HTMLParser
import psycopg2

uploads_dir = os.path.join(app.root_path, 'Uploaded_Docs')
os.makedirs(uploads_dir, exist_ok=True)
app.config['SECRET_KEY'] = 'mysecretkey'
ALLOWED_EXTENSIONS = {'docx'}

# General Functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

MyList = []

class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        MyList.append([self.get_starttag_text(), data])
        return MyList


class Uploads:

    def __init__(self):
        pass

    @staticmethod
    def initial_upload(request):
        if 'file' not in request.files:
            flash('No file part')
            return render_template("/includes/fail.html", title='Error',
                                   text='No file part')
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
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
    def convert_to_html(path):
        with open(path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file, ignore_empty_paragraphs=False)
            text = result.value
#            messages = result.messages
#            with open('test.html', 'w') as html_file:
#                html_file.write(text)
            return text

    @staticmethod
    def parse_html(text):
        parser = MyHTMLParser()
        parser.feed(text)
        return MyList

    @staticmethod
    def chapter(list):
        chapters = []
        for i in list:
            if i[0] != '<p>':
                chapters.append([i[1], MyList.index(i)])
        return chapters

    @staticmethod
    def level(list):
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
    def hierarchy(list_one, list_two):
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
    def prepare_DB_transmission(level_one_list, chapter_data_dict):
        lecture = level_one_list[0][0]
        Content_List = []
        for i in chapter_data_dict:
            Content_List.append([lecture, i, chapter_data_dict[i]])
        return Content_List

    @staticmethod
    def transmission_to_DB(Content_List):
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        for i in Content_List:
            myCursor.execute(f"CALL add_content('{str(i[0])}', '{str(i[1])}', '{str(i[2])}')")
        dbconn.commit()
        myCursor.close()
        dbconn.close()

    @staticmethod
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
    def hierarchy_transmission_to_DB(Hierarchy_List):
        dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
        myCursor = dbconn.cursor()
        for i in Hierarchy_List:
            myCursor.execute(f"CALL add_hierarchy('{str(i[0])}', '{str(i[1])}', '{str(i[2])}')")
        dbconn.commit()
        myCursor.close()
        dbconn.close()


''' @staticmethod
    def create_hierarchies(self, MyList):
        chapter_list = self.chapter(MyList)
        level_one_list, level_two_list, level_three_list, level_four_list, level_data_list = self.level(MyList)
        one_two_dict = self.hierarchy(level_one_list, level_two_list)
        two_three_dict = self.hierarchy(level_two_list, level_three_list)
        three_four_dict = self.hierarchy(level_three_list, level_four_list)
        chapter_data_dict = self.hierarchy(chapter_list, level_data_list)
        return one_two_dict, two_three_dict, three_four_dict, chapter_data_dict
'''



