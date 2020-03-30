
# to do 
# process all files 2017/07 to 2019/07/01
# update and refine README.md, add installation and run instructions 
# check that environment.yml works 
# refine  points across all gpx
# create a master geojson with refined points and attributes according to number of routes per point
# rename to myroutemap

# usage
# python plot_gps_points_from_geojson.py --data_geojson=data_geojson

# imports
import os
import numpy as np
import pandas as pd
import argparse
import numpy as np
import matplotlib.cm as cm
from scipy.signal import medfilt
import argparse
import glob
from scipy.signal import medfilt

import gpxpy
import geopandas
import geojson
import folium
from folium import plugins
import webbrowser

from utils import rgb2hex
from utils import calc_dist_from_coords
from utils import calc_dist_from_coordsPoint2Line
from utils import RDP

#manual_debug = True
manual_debug = False
if (manual_debug):
    #dir_work = '/home/craigmatthewsmith/gps_tracks'
    #os.chdir(dir_work)
    data_geojson       = 'data_geojson'
else: # parse command line parameters
    parser = argparse.ArgumentParser(description = 'process gpx files to geojson')
    parser.add_argument('--data_geojson',       type=str, default='data_geojson',       help = 'output .geojson file')
    args = parser.parse_args()    
    data_geojson       = args.data_geojson 


# create new GeoJson objects to reduce GeoJSON data sent to Folium map as layer
f_track     = lambda x: {'color': '#FC4C02', 'weight': 5} # show some color...
f_track_new = lambda x: {'color': '#061283', 'weight': 5} # show some color...

geojson_file_list = sorted(glob.glob(os.path.join(data_geojson, '*.geojson')))
n_files = len(geojson_file_list)
print('found %s files ' %(n_files))                              

cmap = cm.get_cmap('jet') # matplotlib colormap


features_tracks = []
features_tracks_new = []
features_elevation = []
features_speed = []
f = 0
#for f in range(0, 3, 1):
#for f in range(n_files-50, n_files, 1):
for f in range(0, n_files, 1):
    geojson_file = geojson_file_list[f]
    print('  reading f %s of %s ' %(f, n_files))
    
    # read geojson file
    with open(geojson_file, 'r') as file:
        geojson_data = geojson.load(file)

    #geojson_data

    for feature in geojson_data['features']:
        line = geojson.LineString(feature['geometry']['coordinates'])
        if (f < n_files-5):
            features_tracks.append(geojson.Feature(geometry=line))
        else:
            features_tracks_new.append(geojson.Feature(geometry=line))

    cmin_elevation = min(feature['properties']['elevation'] for feature in geojson_data['features'])
    cmax_elevation = max(feature['properties']['elevation'] for feature in geojson_data['features'])
    f_elevation = lambda x: {'color': rgb2hex(cmap((x['properties']['elevation']-cmin_elevation)/(cmax_elevation-cmin_elevation))), 'weight': 5} # cmap needs normalized data
    t_elevation = folium.features.GeoJsonTooltip(fields=['elevation'], aliases=['Elevation (m)'])

    for feature in geojson_data['features']:
        line = geojson.LineString(feature['geometry']['coordinates'])
        elevation = feature['properties']['elevation']
        features_elevation.append(geojson.Feature(geometry=line, properties={'elevation': elevation}))

    cmin_speed = min(feature['properties']['speed'] for feature in geojson_data['features'])
    cmax_speed = max(feature['properties']['speed'] for feature in geojson_data['features'])
    f_speed = lambda x: {'color': rgb2hex(cmap((x['properties']['speed']-cmin_speed)/(cmax_speed-cmin_speed))), 'weight': 5} # cmap needs normalized data
    t_speed = folium.features.GeoJsonTooltip(fields=['speed'], aliases=['Speed '])

    for feature in geojson_data['features']:
        line = geojson.LineString(feature['geometry']['coordinates'])
        speed = feature['properties']['speed']
        features_speed.append(geojson.Feature(geometry=line, properties={'speed': speed}))

print('creating map features to map ')

#fmap = folium.Map(tiles='Stamen Terrain', prefer_canvas=True, disable_3d=True)
fmap = folium.Map(tiles='Stamen Terrain', location=[37.862606, -121.978372], zoom_start=10) 
folium.TileLayer(tiles = 'OpenStreetMap', name='OpenStreetMap', show=False).add_to(fmap)
folium.TileLayer(tiles = 'Stamen Terrain', name='Terrain Map', show=True).add_to(fmap)

print('appending features to map ')

geojson_data_elevation = geojson.FeatureCollection(features_elevation)
folium.GeoJson(geojson_data_elevation, style_function=f_elevation, tooltip=t_elevation, name='Elevation (m)', show=False, smooth_factor=3.0).add_to(fmap)
        
geojson_data_speed = geojson.FeatureCollection(features_speed)
folium.GeoJson(geojson_data_speed, style_function=f_speed, tooltip=t_speed, name='Speed ', show=False, smooth_factor=3.0).add_to(fmap)

geojson_data_track = geojson.FeatureCollection(features_tracks)
folium.GeoJson(geojson_data_track, style_function=f_track, name='Track only', show=True, smooth_factor=3.0).add_to(fmap)

geojson_data_track_new = geojson.FeatureCollection(features_tracks_new)
folium.GeoJson(geojson_data_track_new, style_function=f_track_new, name='Track only', show=True, smooth_factor=3.0).add_to(fmap)


folium.LayerControl(collapsed=False).add_to(fmap)

print('saving map ')

# save map to html file
fmap.fit_bounds(fmap.get_bounds())

#html_file = os.path.join(dir_work, 'index.html')
html_file = 'index.html'
if os.path.isfile(html_file):
    os.system('rm -f '+html_file)
fmap.save(html_file)

print('opening map in browser ')
# open html file in default browser
webbrowser.open(html_file, new=2, autoraise=True)




