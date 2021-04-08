from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from passlib.hash import pbkdf2_sha256
from tempfile import mkdtemp

import gdown
import zipfile
import geopandas as gpd

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
    return redirect(url_for('upload'))

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "GET":

        return render_template("upload.html")

    if request.method == "POST":

        link_string = request.form.get("link")
        link_string = link_string.replace(' ', '')
        links = link_string.split(",")

        for l in links:
            file_id = l[32:].split('/')[0]

            url = "https://drive.google.com/uc?id=" + file_id
            output = 'geo/tmpData/tmp.zip'
            gdown.download(url, output, quiet=False)

            with zipfile.ZipFile(output, 'r') as zip_ref:
                zip_ref.extractall('geo/tmpData/')

        fl_counties = gpd.read_file("geo/tmpData/cntbnd_sep15/cntbnd_sep15.shp") # LINESTRING geometry
        fl_counties = fl_counties.to_crs("EPSG:4326")

        # return render_template("result.html", filename="static/ouch.jpg")

        return render_template("result.html", tables=[fl_counties.to_html(classes='data', max_rows=5, max_cols=5)], titles=fl_counties.columns.values)

def getApp():
    return app

if __name__ == '__main__':
    #app.debug = True
    app.run(host='0.0.0.0', port=5001)
