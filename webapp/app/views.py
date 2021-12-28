from flask import render_template, request, flash, redirect, url_for
from app import app
from werkzeug.utils import secure_filename
import os
from app.Uploads import Uploads


# Page Functions
@app.route('/')  # Overview
def index():
    return render_template("/index.html")

@app.route('/learning', methods=['POST', 'GET'])  # Learning
def learning():
    return render_template("/learning.html")

@app.route('/exercise', methods=['POST', 'GET'])  # Exercise
def exercise():
    return render_template("/exercise.html")

@app.route('/upload', methods=['POST', 'GET'])  # Upload
def upload():
    return render_template("/upload.html")

@app.route('/uploader', methods = ['GET', 'POST'])
def uploading_file():
   if request.method == 'POST':
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
        Hierarchy_list = Uploads.prepare_hierarchy_transmission(level_one_list, one_two_dict, two_three_dict, three_four_dict)
        Uploads.hierarchy_transmission_to_DB(Hierarchy_list)
        return render_template("/includes/success.html", title='Success',
                                   text=Hierarchy_list)

@app.route('/connection', methods = ['GET', 'POST'])
def test_connection():
    dbconn = psycopg2.connect(database="postgres", user="postgres", port=5432, password="securepwd", host="db")
    myCursor = dbconn.cursor()
    myCursor.execute("CALL add_content('Test_lecture','Test_chapter', 'Test_content')")
    dbconn.commit()
    myCursor.close()
    dbconn.close()
    return render_template("/includes/success.html", title='Success',
                           text="Your Data was successfully added to the database")