from flask import Flask, flash, redirect, render_template, request, session, url_for, send_file
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from passlib.hash import pbkdf2_sha256
from tempfile import mkdtemp

import gdown
import zipfile
import geopandas as gpd

import os

from custom_geopandas_methods import *

import base64
from io import BytesIO, StringIO
import matplotlib.pyplot as plt
import pandas as pd

# configure application
app = Flask(__name__)

# to use sessions
app.secret_key = b"_o'yyUq1.45{s{a"

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
                               table1=fl_counties.to_html(  # tables is currently a list
                                   classes='data', max_rows=5),
                               table2=fl_roads.to_html(
                                   classes='data', max_rows=5),
                               title1=fl_counties.columns.values,
                               title2=fl_roads.columns.values,
                               files=list_of_files)

#pylint: disable-all


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

        fl_hil = fl_counties[fl_counties[request.form.get("column")]
                             == request.form.get("value")]

        filePathRoads = "geo/tmpData/" + \
            list_of_files[0] + "/" + list_of_files[0] + ".shp"
        fl_roads = gpd.read_file(filePathRoads)  # LINESTRING geometry
        fl_roads = fl_roads.to_crs("EPSG:4326")
        fl_roads_hil = join_reducer(fl_roads, fl_hil)
        fig1 = fl_hil.plot(figsize=(14, 12), facecolor="none",
                           edgecolor="black").get_figure()

        plot1 = figToHTML(fig1)

        fig2 = fl_roads_hil.plot(ax=fl_hil.plot(figsize=(14, 12), facecolor="none",
                                                edgecolor="black")).get_figure()

        plot2 = figToHTML(fig2)

        sample_road_points = sample_roads(fl_roads_hil, n=5, isLine=False)
        reverse_geocode(sample_road_points)

        plot3 = fl_hil.plot(
            figsize=(14, 12), facecolor="none", edgecolor="black")

        fl_roads_hil.plot(ax=plot3)
        fig3 = sample_road_points.plot(
            marker='*', color='red', markersize=50, ax=plot3).get_figure()

        plot3 = figToHTML(fig3)
        sample_road_lines = sample_roads(fl_roads_hil, n=5, isLine=True)
        sample_road_lines

        ax = fl_hil.plot(figsize=(14, 12), facecolor="none", edgecolor="black")
        fl_roads_hil.plot(ax=ax)
        sample_road_lines.plot(color='red', ax=ax)

        # resp = make_response(df.to_csv())
        # resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        # resp.headers["Content-Type"] = "text/csv"
        # return resp

        session["df"] = sample_road_lines.to_csv(
            index=False, header=True, sep=";")
        return render_template("filter.html", plot1=plot1, plot2=plot2,
                               road_points_table=reverse_geocode(
                                   sample_road_points).to_html(),
                               plot3=plot3)


@app.route("/download", methods=["POST"])
def download():
    # Get the CSV data as a string from the session
    csv = session["df"] if "df" in session else ""

    # Create a string buffer
    buf_str = StringIO(csv)

    # Create a bytes buffer from the string buffer
    buf_byt = BytesIO(buf_str.read().encode("utf-8"))

    # Return the CSV data as an attachment
    return send_file(buf_byt,
                     mimetype="text/csv",
                     as_attachment=True,
                     attachment_filename="data.csv")


def figToHTML(figure):
    tmpfile = BytesIO()
    figure.savefig(tmpfile, format='png')
    encoded1 = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

    return '<img src=\'data:image/png;base64,{}\'>'.format(encoded1)


def getApp():
    return app


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=5001)
