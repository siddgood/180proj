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
