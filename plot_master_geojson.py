
# purpose 
# plot master geojson tracks and recent individual tracks 

# usage
# python plot_master_geojson.py --dir_geojson=data/geojson


# imports
import os
import numpy as np
import folium
import geopandas
import argparse
import glob
from datetime import datetime  as dt
from datetime import timedelta as td
import geojson
import webbrowser
import matplotlib.cm as cm
#from scipy.signal import medfilt
import pandas as pd

from utils import calc_dist_from_coords
from utils import RDP
from utils import rgb2hex
from utils import calc_dist_between_two_coords
from utils import calc_dist_between_one_point_to_all_points

#manual_debug = True
manual_debug = False
if (manual_debug):
    dir_work = '/home/craigmatthewsmith/gps_tracks'
    os.chdir(dir_work)
    dir_geojson = 'data/geojson'
else: # parse command line parameters
    dir_work = os.getcwd()
    parser = argparse.ArgumentParser(description = 'process gpx files to geojson')
    parser.add_argument('--dir_geojson', type=str, default='data/geojson', help = 'data of geojson files')
    args = parser.parse_args()    
    dir_geojson = args.dir_geojson 

use_RDP  = True
epsilon  = 1.0 # rdp thinning 
#dist_min_aggregate_points = 1.0 
dist_min_aggregate_points = 3.0 
#dist_min_aggregate_points = 10.0 

#  1.0, reduced points from 75752 to 65536, 2.5 M master.geojson file size 
# 10.0, reduced points from 75752 to 19330, 2.5 M master.geojson file size

dist_max_between_points_to_make_line = 100.0 # dont plot lines this far away

dt_now = dt.now()

trailheads_file = 'trailheads.csv'
# read trailheads file
trailheads_csv = pd.read_csv(trailheads_file,index_col=0)
#trailheads_matrix = stn_read_csv.as_matrix()
trailheads_csv.head()

#th_lon = [-121.95168, -121.96682, -121.97457]
#th_lat = [37.83386, 37.85792, 37.8524]

th_lat = [
    37.8694,
    37.84743,
    37.8628, 
    37.87572,
    37.87586,
    37.88652, 
    37.88754, 
    37.87056, 
    37.8501, 
    37.85977, 
    37.85792,
    37.83386,
    37.8524]

th_lon = [
    -121.9973,
    -121.98593,
    -121.9791,
    -122.02286,
    -122.01466,
    -122.01799,
    -122.01429,
    -122.01017,
    -121.99069,
    -121.98874,
    -121.96682,
    -121.95168,
    -121.97457]

n_th = len(th_lat)


# last updated 2020/05/16
n_recent_days1 = 90
n_recent_days2 =  7 


# find recent geojson files
geojson_file_list_recent1 = []
geojson_file_list_recent2 = []

geojson_file_list_all = glob.glob(os.path.join(dir_geojson, '*.geojson'))
n_files = len(geojson_file_list_all)
print(n_files)     
n = 10
for n in range(0, n_files, 1):
    file_temp = geojson_file_list_all[n]        
    date_temp = os.path.basename(file_temp).split('.')[0]
    if (date_temp.endswith('p')):
        date_temp = date_temp.split('p')[0]
    #print(date_temp)
    dt_temp = dt.strptime(date_temp,'%Y-%m-%d_%H-%M')
    #print(dt_temp)
    days_delta = (dt_now - dt_temp).days
    #print(days_delta)
    if (days_delta <= n_recent_days2):
        geojson_file_list_recent2.append(file_temp)
    if (days_delta > n_recent_days2 and days_delta <= n_recent_days1):
        geojson_file_list_recent1.append(file_temp)

n_files1 = len(geojson_file_list_recent1)
n_files2 = len(geojson_file_list_recent2)
print('found %s recent files' %(n_files1))                              
print('found %s recent files' %(n_files2)) 

features_tracks_recent1 = []
f = 0
for f in range(0, n_files1, 1):
    geojson_file = geojson_file_list_recent1[f]
    print('  processing f %s of %s ' %(f, n_files))
    # read geojson file
    with open(geojson_file, 'r') as file:
        geojson_data = geojson.load(file)    
    #geojson_data
    for feature in geojson_data['features']:
        line = geojson.LineString(feature['geometry']['coordinates'])
        features_tracks_recent1.append(geojson.Feature(geometry=line))        

features_tracks_recent2 = []
f = 0
for f in range(0, n_files2, 1):
    geojson_file = geojson_file_list_recent2[f]
    print('  processing f %s of %s ' %(f, n_files))
    # read geojson file
    with open(geojson_file, 'r') as file:
        geojson_data = geojson.load(file)    
    #geojson_data
    for feature in geojson_data['features']:
        line = geojson.LineString(feature['geometry']['coordinates'])
        features_tracks_recent2.append(geojson.Feature(geometry=line))        

        
geojson_data_track_recent1 = geojson.FeatureCollection(features_tracks_recent1)
geojson_data_track_recent2 = geojson.FeatureCollection(features_tracks_recent2)
    
#geojson_file = os.path.join(dir_work, 'master_thin.geojson')
geojson_file = 'master_thin_min_'+str(int(dist_min_aggregate_points))+'_max_'+str(int(dist_max_between_points_to_make_line))+'.geojson'

# print(os.path.isfile(geojson_file))

# read geojson file
with open(geojson_file, 'r') as file:
    geojson_data = geojson.load(file)

features_tracks  = []
features_n_times = []

for feature in geojson_data['features']:
    line = geojson.LineString(feature['geometry']['coordinates'])
    n_times = feature['properties']['n_times']
    features_tracks.append(geojson.Feature(geometry=line))
    features_n_times.append(geojson.Feature(geometry=line, properties={'n_times': n_times}))
    
geojson_data_track = geojson.FeatureCollection(features_tracks)
geojson_data_n_times = geojson.FeatureCollection(features_n_times)
    
cmin_n_times = min(feature['properties']['n_times'] for feature in geojson_data['features'])
cmax_n_times = max(feature['properties']['n_times'] for feature in geojson_data['features'])
cmax_n_times = 20

print ('min and max times is %s - %s' %(cmin_n_times, cmax_n_times))

# '#FC4C02'
# create new GeoJson objects to reduce GeoJSON data sent to Folium map as layer
style_track1   = lambda x: {'color': '#a432a8', 'weight': 5}  
style_track2   = lambda x: {'color': '#11f52f', 'weight': 5} # #4e32a8 
#style_track2   = lambda x: {'color': '#11f52f', 'weight': 5}  
# cmap needs normalized data
#style_n_times = lambda x: {'color': rgb2hex(cmap((x['properties']['n_times']-cmin_n_times)/(cmax_n_times-cmin_n_times))), 'weight': 5} 
style_n_times = lambda x: {'color': rgb2hex(cmap((min(cmax_n_times,x['properties']['n_times'])   -cmin_n_times)/(cmax_n_times-cmin_n_times))), 'weight': 5} 
tooltip_n_times = folium.features.GeoJsonTooltip(fields=['n_times'], aliases=['n_times'])


#fmap = folium.Map(location = [53.545612, -113.490067], zoom_start= 10.5)
#fmap = folium.Map(location=[37.862606, -121.978372], tiles='Stamen Terrain', zoom_start=11, control_scale=True)
fmap = folium.Map(location=[37.862606, -121.978372], tiles='Stamen Terrain', zoom_start=13, control_scale=True)

# set up Folium map
#fmap = folium.Map(tiles = None, prefer_canvas=True, disable_3d=True)
#fmap = folium.Map(tiles='Stamen Terrain', prefer_canvas=True, disable_3d=True)
#fmap = folium.Map(tiles='Stamen Terrain', name='Terrain Map', location=[34.862606, -121.978372], zoom_start=10) 
# folium.TileLayer(tiles = 'Stamen Terrain', name='Terrain Map', show=True).add_to(fmap)
folium.TileLayer(tiles = 'CartoDB dark_matter', name='CartoDB', show=False).add_to(fmap)
folium.TileLayer(tiles = 'OpenStreetMap', name='OpenStreetMap', show=False).add_to(fmap)
cmap = cm.get_cmap('jet') # matplotlib colormap
print('appending features to map ')

# add heatmap
#folium.GeoJson(geojson_data_track,   style_function=style_track, name='track', show=True, smooth_factor=3.0).add_to(fmap)
folium.GeoJson(geojson_data_n_times, style_function=style_n_times, tooltip=tooltip_n_times, name='n_times', show=True, smooth_factor=3.0).add_to(fmap)
# add th
for n in range(0, n_th, 1):
    #folium.Marker([th_lat[n], th_lon[n]]).add_to(fmap)
    #folium.Marker([th_lat[n], th_lon[n]], fill_color='#43d9de', radius=8).add_to(fmap)
    folium.Marker([th_lat[n], th_lon[n]], fill_color='#43d9de', radius=4).add_to(fmap)
    # popup=df_counters['Name'][point], icon=folium.Icon(color='darkblue', icon_color='white', icon='male', angle=0, prefix='fa')).add_to(marker_cluster)

# add recent tracks        
folium.GeoJson(geojson_data_track_recent1, style_function=style_track1, name='7-90d', show=True, smooth_factor=3.0).add_to(fmap)
folium.GeoJson(geojson_data_track_recent2, style_function=style_track2, name='last 7 days', show=True, smooth_factor=3.0).add_to(fmap)

# add layer control widget
folium.LayerControl(collapsed=False).add_to(fmap)

# save map to html file
#fmap.fit_bounds(fmap.get_bounds())

#html_file = os.path.join(dir_work, 'heatmap.html')
#html_file = 'heatmap_'+str(int(dist_min))+'_max_'+str(int(dist_max))+'.html'
html_file = 'heatmap_'+str(int(dist_min_aggregate_points))+'_max_'+str(int(dist_max_between_points_to_make_line))+'.html'
if os.path.isfile(html_file):
    os.system('rm -f '+html_file)
fmap.save(html_file)
# open html file in default browser
webbrowser.open(html_file, new=2, autoraise=True)
