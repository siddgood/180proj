from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from passlib.hash import pbkdf2_sha256
from tempfile import mkdtemp

import gdown
import zipfile
import geopandas as gpd

import os

from custom_geopandas_methods import join_reducer

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
    # returns index page
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

        path = os.getcwd() + "/geo/tmpData/"
        list_of_files = []

        for filename in os.listdir(path):

            if ".zip" not in filename and "__MACOSX" not in filename:

                list_of_files.append(filename)

        fl_counties = gpd.read_file(
            "geo/tmpData/" + list_of_files[0] + "/" + list_of_files[0] + ".shp")  # LINESTRING geometry
        fl_counties = fl_counties.to_crs("EPSG:4326")

        fl_roads = gpd.read_file(
            "geo/tmpData/" + list_of_files[1] + "/" + list_of_files[1] + ".shp")  # LINESTRING geometry
        fl_roads = fl_counties.to_crs("EPSG:4326")

        # return render_template("result.html", filename="static/ouch.jpg")

        return render_template("result.html",
                               table1=[fl_counties.to_html(
                                   classes='data', max_rows=5)],
                               table2=[fl_roads.to_html(
                                   classes='data', max_rows=5)],
                               title1=fl_counties.columns.values,
                               title2=fl_roads.columns.values,
                               files=list_of_files)


@app.route("/filter", methods=["GET", "POST"])
def filter():
    if request.method == "GET":

        return render_template("error.html")

    if request.method == "POST":
        path = os.getcwd() + "/geo/tmpData/"
        list_of_files = []

        for filename in os.listdir(path):

            if ".zip" not in filename and "__MACOSX" not in filename:

                list_of_files.append(filename)

        filePathCounties = "geo/tmpData/" + \
            list_of_files[1] + "/" + list_of_files[1] + ".shp"
        fl_counties = gpd.read_file(filePathCounties)  # POLYGON geometry
        fl_counties = fl_counties.to_crs("EPSG:4326")
        print("counties")
        print(request.form.get("column"))
        print(request.form.get("value"))
        fl_hil = fl_counties[fl_counties[request.form.get("column")]
                             == request.form.get("value")]

        filePathRoads = "geo/tmpData/" + \
            list_of_files[0] + "/" + list_of_files[0] + ".shp"
        fl_roads = gpd.read_file(filePathRoads)  # LINESTRING geometry
        fl_roads = fl_roads.to_crs("EPSG:4326")
        print("here1")
        fl_roads_hil = join_reducer(fl_roads, fl_hil)
        print("here2")
    return render_template("error.html")


def getApp():
    return app


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=5001)
