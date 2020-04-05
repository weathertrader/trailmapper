
# to do 

# 2 hr  from raw_gpx, thinning points implement, refine points across all gpx
#       count number of times each point has been visited 

# 1 hr  understand and implement 
#       calc_dist_between_two_coords(), calc_dist_between_points() and 
#       calc_dist_from_coords_to_line(), calc_distance_between_point_and_line()

# 2 hr  redo rdp algo on individual gpx  

# 1 hr  write geojson, drop speed and slope data

# 1 hr  plot colorbar shows number of visits
#       plot can show heatmap or invididual  
# 2 hr  repo structure, 
#       cli implementation 
#       process all

# 2 hr add RAWS stations 

# update and refine README.md, add installation and run instructions 
# check that environment.yml works 
# create a master geojson with refined points and attributes according to number of routes per point
# add number of points to each geojson point 
# add new routes to existing master route 
# rename to myroutemap

# script names 
# process_gpx_to_geojson_individual - uses rdp to simply each gpx to geojson

# process_all_gpx_to_master - read individual, apply rdp, aggregate all to single with visit counts 

# process_new_tracks_add_to_existing_master - eliminates too close points, retains new points
# plot_geojson, has flags for plot master and for individual 

# cli options  
# python script_name.py --data_geojson=data_geojson
# --master_name=data_master/tracks_master.geosjon
# --data_input_raw=data_input_raw 
# --data_processed_gpx=data_processed_gpx 
# --data_geojson=data_geojson

# remove stopped points 
If the magnitude of the time averaged velocity of an activity stream gets too low at any point, 
subsequent points from that activity are filtered until the activity breaches a specific radius in distance
 from the initial stopped point.

https://github.com/remisalmon/Strava-to-GeoJSON/blob/master/strava_geojson.py
rdp 
https://github.com/fhirschmann/rdp/blob/master/rdp/__init__.py
https://github.com/sebleier/RDP/blob/master/__init__.py


# usage
# python plot_gps_points_from_geojson.py --data_geojson=data_geojson

# imports
import os
import numpy as np
import pandas as pd
import matplotlib.cm as cm
from scipy.signal import medfilt
import argparse
import glob
from scipy.signal import medfilt

import geopandas
import geojson
import folium
from folium import plugins
import webbrowser

from utils import rgb2hex

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




