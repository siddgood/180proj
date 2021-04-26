import geopandas as gpd
from shapely.geometry import Point, LineString, MultiPoint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopy


def join_reducer(left, right):
    """
    Take two geodataframes, do a spatial join, and return
    without the index_left and index_right columns
    """
    sjoin = gpd.sjoin(left, right, how='inner')
    for column in ['index_left', 'index_right']:
        try:
            sjoin.drop(column, axis=1, inplace=True)
        except Exception as e:
            # ignore if there are no index columns
            pass
    return sjoin


def sample_roads(geodf, n=100, isLine=False):
    '''
    Sample points and lines(street segments) from a road network
    '''
    m = len(geodf)
    lengths = geodf['LENGTH'].tolist()
    total_length = geodf.sum()['LENGTH']
    lengths_normalized = [l/total_length for l in lengths]

    indices = np.random.choice(range(m), size=n, p=lengths_normalized)
    # indices = np.random.choice(range(m), size=n)

    if isLine:
        lines = []
        for index in indices:
            line = geodf.iloc[index]['geometry']
            lines.append(line)

        # return MultiPoint(lines)
        return gpd.GeoSeries(lines)

    points = []
    for index in indices:
        line = geodf.iloc[index]['geometry']
        offset = np.random.rand() * line.length
        point = line.interpolate(offset)
        points.append(point)

    # return MultiPoint(points)
    return gpd.GeoSeries(points)


def reverse_geocode(geoseries, provider='arcgis'):
    '''
    Function to reverse geocode GeoSeries points
    '''
    return gpd.tools.reverse_geocode(list(geoseries), provider=provider)


def sample_location(geodf, n, buffer=None):
  '''
  Samples from a shapefile that has
  ALL entries as point geometries
  '''
  m = len(geodf)
  indices = np.random.choice(range(m), size=n)
  sample = []

  for index in indices:
    point = geodf.iloc[index]['geometry']
    sample.append(point)

  output = gpd.GeoSeries(sample)
  if buffer:
    output.set_crs('EPSG:4326', inplace=True)
    output = output.to_crs(epsg=3763)
    output = output.buffer(buffer)
    output = output.to_crs(epsg=4326)
  return output
