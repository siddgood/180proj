# README

## Local Deployment

### Set up via terminal:

Launch terminal and navigate to the ```nga_auto_rfi/ ``` directory/folder

```sh
pip install virtualenv # skip step if virtualenv package is already installed

virtualenv venv

source venv/bin/activate

pip3 install -r requirements.txt
```

### To launch and view:

```sh
python3 geo/__init__.py
```
Local deployment should be viewable at http://0.0.0.0:5001/

### Local app usage notes:
  * All shapefiles that are inputted in the app are locally downloaded in the ```geo/tmp/``` folder
    - After using the app, the downloaded files in this folder can be deleted, but **DO NOT** delete the ```tmp.zip``` found in this folder as this file is necessary and pre-existed originally within the folder

### Sample upload files

* [Road network shapefile](https://drive.google.com/file/d/1ohwYyl2wa1AIgoR5b7T6opPkauRHc6Vv/view?usp=sharing)
* [Area of interest (AOI) shapefile](https://drive.google.com/file/d/1ILbsKRob4alKkAqzzZxquXs8q4wx2KoZ/view?usp=sharing)
* [Parameter shapefile](https://drive.google.com/file/d/1z93Xpo2Ikc8FSdgiRuxixqOvzqEckDwD/view?usp=sharing) (optional)

## Heroku Deployment

Latest demo build is live on https://geosampling.herokuapp.com

Optionally, you can download this folder and deploy directly on your own Heroku using the [Heroku CLI](https://devcenter.heroku.com/articles/git).

### To upload your own shapefiles

To upload your own shapefiles, the use must **at least** upload a road network shapefile (w/ LINESTRING geometry) and an AOI shapefile (w/ POLYGON/MULTIPOLYGON geometry). Please refer to the sample shapefiles for reference.

For the application, the user must upload these shapefiles to Google Drive and obtain a public Google Drive link. Uploading of shapefile **must** be done in the following way:

* Create an empty folder that is the same name as your desired .shp filename (i.e. for majrds_oct19.shp, create an empty folder named "majrds_oct19")
* Put the desired shapefile **and** all related files in the empty folder you created
  - Sometimes your desired .shp file depends on other filetypes (.sbx, .shx, etc.) that may have been downloaded orginially from the source, so make sure to include all of these in the empty folder
* Zip/compress up the non-empty folder and upload the zipped folder to Google Drive
* Set the share settings such that "Anyone with link" can view

Complete the above steps for your desired road network shapefile, AOI shapefile, and parameter shapefile.
