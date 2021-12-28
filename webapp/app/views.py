from flask import render_template, request, flash, redirect, url_for
from app import app
from werkzeug.utils import secure_filename
import os
from app.Uploads import Uploads
from app.LearningForest import LearningForest

LF = LearningForest()


# Page Functions
@app.route('/')  # Overview
def index():
    return render_template("/index.html")

@app.route('/learning', methods=['POST', 'GET'])  # Learning
def learning():
    lectures = LF.dropdown_lecture()
    return render_template("/learning.html", lectures=lectures)

@app.route('/exercise', methods=['POST', 'GET'])  # Exercise
def exercise():
    lectures = LF.dropdown_lecture()
    return render_template("/exercise.html", lectures=lectures)

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
                                   text="Your Data was successfully transmitted to the Database")