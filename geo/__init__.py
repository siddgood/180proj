from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from passlib.hash import pbkdf2_sha256
from tempfile import mkdtemp

import gdown
import zipfile

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    #returns index page
    return redirect(url_for('search'))

@app.route("/search", methods=["GET", "POST"])
def search():
    """Get stock quote."""

    if request.method == "GET":

        return render_template("search.html")

    if request.method == "POST":

        name = request.form.get("link")


        file_id = name[32:].split('/')[0]

        url = "https://drive.google.com/uc?id=" + file_id
        output = 'sidd/test.zip'
        gdown.download(url, output, quiet=False)

        with zipfile.ZipFile(output, 'r') as zip_ref:
            zip_ref.extractall('sidd/')

        return render_template("result.html", offensive_text_compared={}, filename="static/ugh.jpg")

def getApp():
    return app

if __name__ == '__main__':
    #app.debug = True
    app.run(host='0.0.0.0', port=5001)
