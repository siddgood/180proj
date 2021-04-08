#!/usr/bin/env python
# coding: utf-8

# In[1]:


import geopandas as gpd
from shapely.geometry import Point, LineString, MultiPoint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopy


# In[2]:


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


# In[3]:


# Function to generate random points and lines on roads

# Source: https://github.com/gboeing/osmnx/issues/639

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


# In[4]:


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


# In[5]:


def reverse_geocode(geoseries, provider='arcgis'):
  '''
  Function to reverse geocode GeoSeries points
  '''
  return gpd.tools.reverse_geocode(list(geoseries), provider=provider)


# In[6]:


def geoseries_to_geodf(geoseries):
  '''
  Converts a simple GeoSeries to a GeoPandas dataframe with a geometry column
  '''
  output_gdf = gpd.GeoDataFrame(geoseries)
  output_gdf.rename(columns={0:'geometry'}).set_geometry('geometry')
  return output_gdf


# # Sample Points and Lines

# ## Road Network x County (Boundary)

# In[7]:


fl_roads = gpd.read_file("./data/majrds_oct19/majrds_oct19.shp") # LINESTRING geometry
fl_roads = fl_roads.to_crs("EPSG:4326")


# In[8]:


fl_counties = gpd.read_file("./data/cntbnd_sep15/cntbnd_sep15.shp") # POLYGON geometry
fl_counties = fl_counties.to_crs("EPSG:4326")


# In[9]:


fl_hil = fl_counties[fl_counties['TIGERNAME'] == 'Hillsborough'] 


# In[10]:


fl_roads_hil = join_reducer(fl_roads, fl_hil) # road network MUST be left parameter when joining


# In[11]:


ax = fl_hil.plot(figsize=(14,12), facecolor="none", edgecolor="black")
fl_roads_hil.plot(ax=ax)


# In[12]:


sample_road_points = sample_roads(fl_roads_hil, n=5)


# In[13]:


reverse_geocode(sample_road_points)


# In[14]:


ax = fl_hil.plot(figsize=(14,12), facecolor="none", edgecolor="black")
fl_roads_hil.plot(ax=ax)
sample_road_points.plot(marker='*', color='red', markersize=50, ax=ax)


# In[15]:


sample_road_lines = sample_roads(fl_roads_hil, n=5, isLine=True)
sample_road_lines


# In[16]:


ax = fl_hil.plot(figsize=(14,12), facecolor="none", edgecolor="black")
fl_roads_hil.plot(ax=ax)
sample_road_lines.plot(color='red', ax=ax)


# ## Road Network x County x Civic Centers

# In[17]:


fl_civic = gpd.read_file("./data/gc_civiccenter_jan19/gc_civiccenter_jan19.shp")
fl_civic = fl_civic.to_crs("EPSG:4326")


# In[18]:


fl_civic.head()


# In[19]:


# Plotting multiple layers
fig, ax = plt.subplots(figsize=(14, 12))
fl_counties.plot(ax=ax, facecolor="none", edgecolor='black', column='NAME')
fl_civic.plot(ax=ax, color='blue')


# In[20]:


# https://gis.stackexchange.com/questions/367496/plot-a-circle-with-a-given-radius-around-points-on-map-using-python


# In[21]:


fl_civic_hil = join_reducer(fl_civic, fl_hil)


# In[22]:


fig, ax = plt.subplots(figsize=(14, 12))
fl_counties.plot(ax=ax, facecolor="none", edgecolor='black', column='NAME')
fl_civic_hil.plot(ax=ax, color='blue')


# In[23]:


ax = fl_hil.plot(figsize=(14,12), facecolor="none", edgecolor="black")
fl_civic_hil.plot(marker='*', color='red', markersize=50, ax=ax)


# In[24]:


sample_civic_region = sample_location(fl_civic_hil, n=2, buffer=8046.72) # buffer in meters (1 mi = 1609.34 m)


# In[25]:


ax = fl_hil.plot(figsize=(20,18), facecolor="none", edgecolor="black")
fl_roads_hil.plot(ax=ax)
sample_civic_region.plot(marker='*', color='red', ax=ax)


# In[26]:


sample_civic_df = gpd.GeoDataFrame(sample_civic_region)
sample_civic_df = sample_civic_df.rename(columns={0:'geometry'}).set_geometry('geometry')


# In[27]:


fl_roads_hil_sample_civic = join_reducer(fl_roads_hil, sample_civic_df)


# In[28]:


ax = fl_hil.plot(figsize=(20,18), facecolor="none", edgecolor="black")
fl_roads_hil_sample_civic.plot(ax=ax)
sample_civic_region.plot(marker='*', color='red', ax=ax)


# In[29]:


fl_roads_hil_sample_civic.plot(figsize=(14,12))


# In[30]:


# sample_civic_points = sample_roads(fl_roads_hil_sample_civic, n=5)


# In[31]:


# ax = fl_roads_hil_sample_civic.plot(figsize=(14, 12))
# sample_civic_points.plot(marker='*', color='red', markersize=, ax=ax)


# In[32]:


lines = fl_roads_hil.geometry.unary_union
intersection = lines.intersection(sample_civic_df.geometry[0])
output = gpd.GeoDataFrame({'geometry':intersection})


# In[33]:


length_arr = []
for i in range(len(output)):
  len_i = output['geometry'][i].length
  length_arr.append(len_i)

output['LENGTH'] = length_arr


# In[36]:


output_points = sample_roads(output, n=3, isLine=True)
ax = output.plot(figsize=(14, 12))
output_points.plot(marker='*', color='red', markersize=60, ax=ax)


# In[37]:


intersection_2 = lines.intersection(sample_civic_df.geometry[1])
output_2 = gpd.GeoDataFrame({'geometry':intersection_2})


# In[38]:


length_arr = []
for i in range(len(output_2)):
  len_i = output_2['geometry'][i].length
  length_arr.append(len_i)

output_2['LENGTH'] = length_arr


# In[39]:


output_lines_2 = sample_roads(output_2, n=3, isLine=True)
ax = output_2.plot(figsize=(14, 12))
output_lines_2.plot(marker='*', color='red', markersize=60, ax=ax)

