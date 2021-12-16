from flask import render_template, request, flash, redirect, url_for
from app import app
from werkzeug.utils import secure_filename
import os

uploads_dir = os.path.join(app.root_path, 'Uploads')
os.makedirs(uploads_dir, exist_ok=True)
app.config['SECRET_KEY'] = 'mysecretkey'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

# General Functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



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
           path=os.path.join(uploads_dir, filename)
           file.save(path)
           return render_template("/includes/success.html", title='Success',
                                   text='Your file has been uploaded successfully.')

