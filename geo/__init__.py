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

# global_variables = {}

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

        road_ntwrk = gpd.read_file(
            "geo/tmpData/" + list_of_files[0] + "/" + list_of_files[0] + ".shp")  # LINESTRING geometry
        road_ntwrk = road_ntwrk.to_crs("EPSG:4326")
        road_ntwrk_nogeom = road_ntwrk.drop(columns=road_ntwrk.columns[-1], axis=1, inplace=False)

        AOI = gpd.read_file(
            "geo/tmpData/" + list_of_files[1] + "/" + list_of_files[1] + ".shp")  # LINESTRING geometry
        AOI = AOI.to_crs("EPSG:4326")
        AOI_nogeom = AOI.drop(columns=AOI.columns[-1], axis=1, inplace=False)

        # global_variables["AOI"] = AOI
        # global_variables["road_ntwrk"] = road_ntwrk
        session['AOI'] = AOI
        session['road_ntwrk'] = road_ntwrk

        return render_template("upload_result.html",
                               table1=road_ntwrk_nogeom.to_html(  # tables is currently a list
                                   classes='data', max_rows=100),
                               table2=AOI_nogeom.to_html(
                                   classes='data', max_rows=100),
                               title1=road_ntwrk_nogeom.columns.values,
                               title2=AOI_nogeom.columns.values,
                               files=list_of_files)


@app.route("/filter", methods=["GET", "POST"])
def filter():
    if request.method == "GET":

        return render_template("error.html")

    if request.method == "POST":
        # road_ntwrk = global_variables['road_ntwrk']
        # AOI = global_variables['AOI']
        road_ntwrk = session['road_ntwrk']
        AOI = session['AOI']
        user_column = request.form.get("column")
        user_value = request.form.get("value")
        AOI_userfilter = AOI[AOI[user_column] == user_value]
        session["AOI_userfilter"] = AOI_userfilter

        road_x_aoi = join_reducer(road_ntwrk, AOI_userfilter)
        # global_variables["road_x_aoi"] = road_x_aoi
        session['road_x_aoi'] = road_x_aoi

        fig1 = AOI_userfilter.plot(figsize=(14, 12), facecolor="none", edgecolor="black").get_figure()

        fig1_HTML = figToHTML(fig1)

        fig2 = road_x_aoi.plot(ax=AOI_userfilter.plot(figsize=(14, 12), facecolor="none", edgecolor="black")).get_figure()

        fig2_HTML = figToHTML(fig2)

        return render_template("filter.html", plot1=fig1_HTML, plot2=fig2_HTML, user_column=user_column, user_value=user_value)

@app.route("/sample", methods=["GET", "POST"])
def sample():
    if request.method == "GET":
        return render_template("error.html")

    if request.method == "POST":
        road_x_aoi = session['road_x_aoi']
        user_output_type = request.form.get("output_type")
        user_sample_size = int(request.form.get("sample_size"))

        if user_output_type == 'line':
            isLine = True
        else:
            isLine = False

        sample_output = sample_roads(road_x_aoi, n=user_sample_size, isLine=isLine)
        sample_output_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(sample_output))

        if not isLine:
            reverse_sample_output = reverse_geocode(sample_output)
            session['sample_output_csv'] = reverse_sample_output.to_csv(index=False, header=True, sep=",")
        else:
            session['sample_output_csv'] = sample_output_gdf.to_csv(index=False, header=True, sep=",")

        ax = road_x_aoi.plot(figsize=(14, 12))
        if not isLine:
            fig1 = sample_output.plot(marker='*', color='red', markersize=50, ax=ax).get_figure()
            fig1_HTML = figToHTML(fig1)
            return render_template("sample.html", plot1=fig1_HTML, sample_output=sample_output_gdf.to_html(classes='data'),
                                    reverse_sample_output=reverse_sample_output.to_html(classes='data'))
        else:
            fig1 = sample_output.plot(color='red', ax=ax).get_figure()
            fig1_HTML = figToHTML(fig1)
            return render_template("sample.html", plot1=fig1_HTML, sample_output=sample_output_gdf.to_html(classes='data'))


@app.route("/download", methods=["POST"])
def download():
    # Get the CSV data as a string from the session
    sample_ouput_csv = session["sample_output_csv"] if "sample_output_csv" in session else ""

    # Create a string buffer
    buf_str = StringIO(sample_ouput_csv)

    # Create a bytes buffer from the string buffer
    buf_byt = BytesIO(buf_str.read().encode("utf-8"))

    # Return the CSV data as an attachment
    return send_file(buf_byt,
                     mimetype="text/csv",
                     as_attachment=True,
                     attachment_filename="sample_output_data.csv")

@app.route("/param_filter", methods=["GET", "POST"])
def param_filter():
    if request.method == "GET":
        return render_template("error.html")
    if request.method == "POST":
        link_string = request.form.get("link")
        file_id = link_string[32:].split('/')[0]

        url = "https://drive.google.com/uc?id=" + file_id
        output = 'geo/tmpData/tmp.zip'
        gdown.download(url, output, quiet=False)

        with zipfile.ZipFile(output, 'r') as zip_ref:
            zip_ref.extractall('geo/tmpData/')

        path = os.getcwd() + "/geo/tmpData/"
        filename = os.listdir(path)[-1]

        param_shapefile = gpd.read_file(
            "geo/tmpData/" + filename + "/" + filename + ".shp")  # LINESTRING geometry
        param_shapefile = param_shapefile.to_crs("EPSG:4326")

        AOI_userfilter = session['AOI_userfilter']
        road_x_aoi = session['road_x_aoi']
        param_x_AOIuser = join_reducer(param_shapefile, AOI_userfilter)

        ax = AOI_userfilter.plot(figsize=(14,12), facecolor="none", edgecolor="black")
        param_x_AOIuser_fig = param_x_AOIuser.plot(marker='*', color='red', markersize=50, ax=ax).get_figure()
        road_x_param_x_AOIuser_fig = road_x_aoi.plot(ax=ax).get_figure()


        return render_template("param_filter.html",
                                plot1=figToHTML(road_x_param_x_AOIuser_fig))

@app.route("/sample_param", methods=["GET", "POST"])
def sample_param():
    if request.method == "GET":
        return render_template("error.html")
    if request.method == "POST":
        return


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
