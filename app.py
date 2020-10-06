from flask import Flask, render_template, url_for, request, redirect, abort
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException, default_exceptions, Aborter
#from flask_wtf import FlaskForm
#from flask_wtf.file import FileField
#from wtforms import SubmitField

import locationParse


class FileTypeException(HTTPException):
    code = 400
    description = 'Error: File Type Incorrect!'

default_exceptions[400] = FileTypeException
abort = Aborter()

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'TestFiles'
app.config['UPLOAD_EXTENSIONS'] = ['.gpx'] # can add other file types in the list

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files["gpx_file"] # the file name is listed as gpx_file in index.html
        fileName = secure_filename(uploaded_file.filename)
        if fileName != "":
            # next 3 lines validate the file type
            file_ext = os.path.splitext(fileName)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], fileName))   # uploaded_file.filename) # saves the file to the directory.
            #uploaded_file.save(uploaded_file.filename) # saves the file to the directory.
            #TODO figure out how to read the data and then 
            locationParse.main('TestFiles/' + uploaded_file.filename) # run the parsing which will generate an output.
        return redirect(url_for("index"))

    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def page_forbidden(e):
    return render_template("403.html"), 403



if __name__ == "__main__":
    app.run(debug=True)