
# purpose
# read individual, apply rdp, write to geojson, aggregate all to single with visit counts 

# usage
# python process_all_gpx_to_master.py --dir_gpx=data/gpx --dir_geojson=data/geojson


"""

use_RDP  = True
# rdp thinning 
# eps  0.1 133466 total points, too slow
# eps  1.0  81272 total points 
# eps  3.0  48215 total points, spotty and not connected 
# eps 10.0  22168 total points, spotty and not connected 
#epsilon  =  0.1 # 0.1 is too slow
epsilon  =  1.0 

#dist_min_aggregate_points = 1.0 
dist_min_aggregate_points = 3.0 
#dist_min_aggregate_points = 10.0 


# 10.0 reduced points from 81272 to 20192 
# thin nearby points took  2.05 min



#dist_max_between_points_to_make_line =  1.0 # dont plot lines this far away
#dist_max_between_points_to_make_line = 10.0 # dont plot lines this far away
dist_max_between_points_to_make_line = 100.0 # dont plot lines this far away

process_name = 'process_files'
time_start = time.time()


time_end   = time.time()
process_dt = (time_end-time_start)/60.0
print(process_name+' took %5.2f min' %(process_dt))




time_end   = time.time()
process_dt = (time_end-time_start)/60.0
print(process_name+' took %5.2f min' %(process_dt))

process_name = 'connect adjacent points'
time_start = time.time()

# only connect adjacent points, dont connect points from separate tracks 
features_thin = []

n = 1000
for n in range(1, n_points_all, 1):
    if (n%10000 == 0):
        print('  processing n %s of %s ' %(n, n_points_all)) 
    dist_temp = calc_dist_between_two_coords(lon_all[n], lat_all[n], lon_all[n-1], lat_all[n-1])
    n_temp = max(1, n_time_visited[n])
    if (dist_temp < dist_max_between_points_to_make_line):
        line = geojson.LineString([(lon_all[n], lat_all[n]), (lon_all[n-1], lat_all[n-1])])     
        feature = geojson.Feature(geometry=line, properties={'n_times': int('%.0f'%n_temp)})
        #feature = geojson.Feature(geometry=line, properties={'n_times': int('%.0f'%n_times)})
        features_thin.append(feature)
        del n_temp, line, feature
    

time_end   = time.time()
process_dt = (time_end-time_start)/60.0
print(process_name+' took %5.2f min' %(process_dt))


process_name = 'write master geojson file'
time_start = time.time()


feature_collection_thin = geojson.FeatureCollection(features_thin)
#file_name = 'master_thin.geojson'
file_name = 'master_thin_min_'+str(int(dist_min_aggregate_points))+'_max_'+str(int(dist_max_between_points_to_make_line))+'.geojson'
geojson_write_file = os.path.join(dir_work, file_name)
print('  geojson_write_file is %s ' %(geojson_write_file))
if os.path.isfile(geojson_write_file):
    temp_command = 'rm '+geojson_write_file
    os.system(temp_command)
with open(geojson_write_file, 'w') as file:
    geojson.dump(feature_collection_thin, file)


time_end   = time.time()
process_dt = (time_end-time_start)/60.0
print(process_name+' took %5.2f min' %(process_dt))

"""

""""
import geopandas
#from scipy.signal import medfilt
from utils import calc_dist_from_coords
from utils import rgb2hex
from utils import calc_dist_between_two_coords
from utils import calc_dist_between_one_point_to_all_points
"""




import argparse
import folium
import geojson
import glob
import gpxpy
import matplotlib.cm as cm
import numpy as np
import os
import sys
import time
import webbrowser

from utils import RDP

def create_output_file_name_from_input_file(dir_data, input_file):
    file_type_old = "gpx"
    file_type_new = "geojson"
    file_name_new = os.path.basename(input_file).replace("."+file_type_old, "."+file_type_new)
    output_file = os.path.join(dir_data, file_type_new, file_name_new)
    print(output_file)
    return output_file

def read_gpx_file(input_file):

    lat_temp = []
    lon_temp = []
    ele_temp = []
    dt_temp  = []

    # read GPX file
    with open(input_file, 'r') as file:
        gpx = gpxpy.parse(file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    # lat_lon_temp.append([point.latitude, point.longitude])
                    lon_temp.append([point.longitude])
                    lat_temp.append([point.latitude])
                    ele_temp.append(point.elevation)
                    dt_temp.append(point.time)  # convert time to timestamps (s)

    n_points = len(lon_temp)
    print('    read %s points ' %(n_points))
    gpx_track_dict = {
        "lon_track": lon_temp,
        "lat_track": lat_temp,
        "ele_track": ele_temp,
        "dt_track": dt_temp,
        "n_points": len(lon_temp),
    }
    return gpx_track_dict


def simplify_track(gpx_track_dict):
    # use Ramer–Douglas–Peucker algorithm to reduce the number of trackpoints

    lon_temp = gpx_track_dict["lon_track"]
    lat_temp = gpx_track_dict["lat_track"]
    ele_temp = gpx_track_dict["ele_track"]
    dt_temp  = gpx_track_dict[ "dt_track"]

    # lat_lon_temp = np.array(lat_lon_temp)  # [deg, deg]
    lon_temp = np.array(lon_temp)
    lat_temp = np.array(lat_temp)
    ele_temp = np.array(ele_temp)
    dt_temp = np.array(dt_temp)

    n_points_old = n_points

    temp_array = np.hstack([lat_temp, lon_temp, np.arange(0, n_points, 1).reshape(-1, 1)])
    temp_array_new = RDP(temp_array, epsilon)  # remove trackpoints less than epsilon meters away from the new track
    index = temp_array_new[:, 2].astype(int)  # hack
    ele_temp = np.squeeze(ele_temp[index])
    lon_temp = np.squeeze(lon_temp[index])
    lat_temp = np.squeeze(lat_temp[index])
    dt_temp = np.squeeze(dt_temp[index])
    n_points = len(lon_temp)
    # print('    reduced points from %s to %s ' %(n_points_old, n_points))
    gpx_track_dict_new = {
        "lon_track": lon_temp,
        "lat_track": lat_temp,
        "ele_track": ele_temp,
        "dt_track": dt_temp,
        "n_points": len(lon_temp),
    }
    return gpx_track_dict_new

def convert_gpx_track_dict_to_geojson(gpx_track_dict):
    # create GeoJSON feature collection
    features = []
    for i in np.arange(1, gpx_track_dict["n_points"]):
        # note csmith - not sure which way this should go
        line = geojson.LineString([(gpx_track_dict["lon_track"][i-1], gpx_track_dict["lat_track"][i-1]), (gpx_track_dict["lon_track"][i], gpx_track_dict["lat_track"][i])])
        # line = geojson.LineString([(lat_temp[i-1], lon_temp[i-1]), (lat_temp[i], lon_temp[i])])
        # line = geojson.LineString([(lat_lon_data[i-1, 1], lat_lon_data[i-1, 0]), (lat_lon_data[i, 1], lat_lon_data[i, 0])]) # (lon,lat) to (lon,lat) format
        # feature = geojson.Feature(geometry=line, properties={'elevation': float('%.1f'%elevation_data[i]), 'slope': float('%.1f'%slope_data[i]), 'speed': float('%.1f'%speed_data[i])})
        feature = geojson.Feature(geometry=line, properties={'date': ('%s' % gpx_track_dict["dt_track"][i])})
        features.append(feature)
    feature_collection = geojson.FeatureCollection(features)
    return feature_collection

def write_geojson_file(geojson_track, output_file):
    # print('    geojson_write_file is %s ' %(geojson_write_file))
    with open(output_file, 'w') as file:
        geojson.dump(geojson_track, file)




def get_list_of_files_to_process(dir_data, file_type):
    dir_data_sub = os.path.join(dir_data, file_type)
    print(dir_data_sub)
    file_list = glob.glob(os.path.join(dir_data_sub, '*.'+file_type))
    n_files = len(file_list)
    print('found %s files to process ' %(n_files))
    return file_list


def process_gps_tracks(dir_data):
    file_type = "gpx"
    file_list = get_list_of_files_to_process(dir_data, file_type)
    n_files = len(file_list)
    for i, input_file in enumerate(file_list):
        print(f"Processing file {i} of {n_files}")
        gpx_track_dict = read_gpx_file(input_file)
        output_file = create_output_file_name_from_input_file(dir_data, input_file)
        simplify_track_flag = False
        if simplify_track_flag:
            gpx_track_dict = simplify_track(gpx_track_dict)
        geojson_track = convert_gpx_track_dict_to_geojson(gpx_track_dict)
        write_geojson_file(geojson_track, output_file)

def plot_gps_tracks(dir_data):
    file_type = "geojson"
    file_list = get_list_of_files_to_process(dir_data, file_type)
    n_files = len(file_list)
    features_tracks = []
    for i, input_file in enumerate(file_list):
        print(f"Processing file {i} of {n_files}")
        with open(input_file, 'r') as file:
            geojson_data = geojson.load(file)
        #geojson_data
        for feature in geojson_data['features']:
            line = geojson.LineString(feature['geometry']['coordinates'])
            features_tracks.append(geojson.Feature(geometry=line))

    geojson_data_features_tracks = geojson.FeatureCollection(features_tracks)

    style_track1   = lambda x: {'color': '#a432a8', 'weight': 5}

    # lat_center, lon_center, zoom_level = 32.862606, -121.978372, 13
    # lat_center, lon_center, zoom_level = 31.0, -123.0, 11
    # lat_center, lon_center, zoom_level = 31.5, -119.0, 13
    # lat_center, lon_center, zoom_level = 32.0, -118.0, 13
    # lat_center, lon_center, zoom_level = 32.5, -116.0, 13
    # lat_center, lon_center, zoom_level = 33.0, -116.5, 13
    lat_center, lon_center, zoom_level = 33.0, -117.0, 11
    fmap = folium.Map(location=[lat_center, lon_center], tiles='Stamen Terrain', zoom_start=zoom_level, control_scale=True)

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
    # folium.GeoJson(geojson_data_n_times, style_function=style_n_times, tooltip=tooltip_n_times, name='n_times', show=True, smooth_factor=3.0).add_to(fmap)
    # add th
    # for n in range(0, n_th, 1):
    #     #folium.Marker([th_lat[n], th_lon[n]]).add_to(fmap)
    #     #folium.Marker([th_lat[n], th_lon[n]], fill_color='#43d9de', radius=8).add_to(fmap)
    #     folium.Marker([th_lat[n], th_lon[n]], fill_color='#43d9de', radius=4).add_to(fmap)
    #     # popup=df_counters['Name'][point], icon=folium.Icon(color='darkblue', icon_color='white', icon='male', angle=0, prefix='fa')).add_to(marker_cluster)

    # add recent tracks
    folium.GeoJson(geojson_data_features_tracks, style_function=style_track1, name='individual', show=True, smooth_factor=3.0).add_to(fmap)
    # folium.GeoJson(geojson_data_track_recent2, style_function=style_track2, name='last 7 days', show=True, smooth_factor=3.0).add_to(fmap)

    # add layer control widget
    folium.LayerControl(collapsed=False).add_to(fmap)

    # save map to html file
    #fmap.fit_bounds(fmap.get_bounds())

    # html_file = os.path.join(dir_work, 'heatmap.html')
    html_file = os.path.join('heatmap.html')
    #html_file = 'heatmap_'+str(int(dist_min))+'_max_'+str(int(dist_max))+'.html'
    # html_file = 'heatmap_'+str(int(dist_min_aggregate_points))+'_max_'+str(int(dist_max_between_points_to_make_line))+'.html'
    if os.path.isfile(html_file):
        os.system('rm -f '+html_file)
    fmap.save(html_file)
    # open html file in default browser
    webbrowser.open(html_file, new=2, autoraise=True)




"""
Usage 

Plot all tracks. 
python trailmapper.py --mode process_gps_tracks --dir_data data
python trailmapper.py --mode plot_gps_tracks --dir_data data

TODO 
get list of input gpx files 
process to geojson files 
get list of geojson files 
plot all geojson and save to html 


"""


supported_modes = ["process_gps_tracks", "plot_gps_tracks"]

if __name__ == "__main__":

    dir_cwd = os.getcwd()
    parser = argparse.ArgumentParser(description='Process input arguments.')
    # parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--dir_data', type=str, default='data', help = 'data directory')
    args = parser.parse_args()
    args = parser.parse_args()
    mode = args.mode
    dir_data = args.dir_data
    print(f"Using mode {mode}")
    print(f"Using dir_data {dir_data}")
    if mode not in supported_modes:
        print(f"ERROR mode {mode} is not supported")
        sys.exit()
    if not os.path.isdir(dir_data):
        print(f"ERROR dir_data {dir_data} does not exist")
        sys.exit()
    if mode == "process_gps_tracks":
        process_gps_tracks(dir_data)
    elif mode == "plot_gps_tracks":
        plot_gps_tracks(dir_data)



"""
# debug 
dir_data = "data"
file_type = "gpx"
input_file = file_list[10]
"""





