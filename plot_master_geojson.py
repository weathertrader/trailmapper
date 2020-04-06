
# purpose 
# read individual, apply rdp, aggregate all to single with visit counts 

# usage
# python plot_master_geojson.py --dir_gpx_processed=data/gpx_processed


# imports
import os
import numpy as np
import folium
import geopandas
import argparse
import glob
import gpxpy
import geojson
import webbrowser
import matplotlib.cm as cm
#from scipy.signal import medfilt

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
    dir_gpx_original  = 'data/gpx_original' 
    dir_gpx_processed = 'data/gpx_processed' 
    dir_geojson       = 'data/geojson'
else: # parse command line parameters
    parser = argparse.ArgumentParser(description = 'process gpx files to geojson')
    parser.add_argument('--dir_gpx_processed', type=str, default='data/gpx_processed', help = 'data of gpx files')
    args = parser.parse_args()    
    dir_gpx_processed = args.dir_gpx_processed 



ingest_file_list = glob.glob(os.path.join(dir_gpx_processed, '*.gpx'))
n_files = len(ingest_file_list)
print('found %s files to process ' %(n_files))                              



epsilon  = 1.0 # [m]
dist_min = 1.0 # 1.0, 75752 to 65536, 5386531 master.geojson file size 
dist_max = 100.0 # dont plot lines this far away



#geojson_file = os.path.join(dir_work, 'master_thin.geojson')
geojson_file = 'master_thin_min_'+str(int(dist_min))+'_max_'+str(int(dist_max))+'.geojson'

print(os.path.isfile(geojson_file))

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

print(cmin_n_times)
print(cmax_n_times)

# create new GeoJson objects to reduce GeoJSON data sent to Folium map as layer
style_track = lambda x: {'color': '#FC4C02', 'weight': 5} # show some color...

style_n_times = lambda x: {'color': rgb2hex(cmap((x['properties']['n_times']-cmin_n_times)/(cmax_n_times-cmin_n_times))), 'weight': 5} # cmap needs normalized data
tooltip_n_times = folium.features.GeoJsonTooltip(fields=['n_times'], aliases=['n_times'])

# set up Folium map
#fmap = folium.Map(tiles = None, prefer_canvas=True, disable_3d=True)
#fmap = folium.Map(tiles='Stamen Terrain', prefer_canvas=True, disable_3d=True)
fmap = folium.Map(tiles='Stamen Terrain', location=[37.862606, -121.978372], zoom_start=10) 
folium.TileLayer(tiles = 'OpenStreetMap', name='OpenStreetMap', show=False).add_to(fmap)
folium.TileLayer(tiles = 'Stamen Terrain', name='Terrain Map', show=True).add_to(fmap)
cmap = cm.get_cmap('jet') # matplotlib colormap


print('appending features to map ')

folium.GeoJson(geojson_data_track, style_function=style_track, name='track', show=True, smooth_factor=3.0).add_to(fmap)
folium.GeoJson(geojson_data_n_times, style_function=style_n_times, tooltip=tooltip_n_times, name='n_times', show=False, smooth_factor=3.0).add_to(fmap)
        
#fmap

# add layer control widget
folium.LayerControl(collapsed=False).add_to(fmap)

# save map to html file
fmap.fit_bounds(fmap.get_bounds())

#html_file = os.path.join(dir_work, 'heatmap.html')
html_file = 'heatmap_'+str(int(dist_min))+'_max_'+str(int(dist_max))+'.html'

if os.path.isfile(html_file):
    os.system('rm -f '+html_file)
fmap.save(html_file)
# open html file in default browser
webbrowser.open(html_file, new=2, autoraise=True)
