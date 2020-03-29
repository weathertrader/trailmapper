
# usage
# python process_gpx_files_to_geojson.py --data_input_raw=data_input_raw --data_processed_gpx=data_processed_gpx --data_geojson=data_geojson

import os
import numpy as np
import pandas as pd
import folium
from folium import plugins
import geopandas
import argparse
import glob
import gpxpy
import geojson
import webbrowser
import numpy as np
import matplotlib.cm as cm
from scipy.signal import medfilt
import argparse
import glob

from scipy.signal import medfilt

from utils import rgb2hex
from utils import calc_dist_from_coords
from utils import calc_dist_from_coordsPoint2Line
from utils import RDP

#manual_debug = True
manual_debug = False
if (manual_debug):
    #dir_work = '/home/craigmatthewsmith/gps_tracks'
    #os.chdir(dir_work)
    data_input_raw     = 'data_input_gpx' 
    data_processed_gpx = 'data_processed_gpx' 
    data_geojson       = 'data_geojson'
else: # parse command line parameters
    parser = argparse.ArgumentParser(description = 'process gpx files to geojson')
    parser.add_argument('--data_input_raw',     type=str, default='data_input_raw',     help='input .gpx file')
    parser.add_argument('--data_processed_gpx', type=str, default='data_processed_gpx', help = 'output .geojson file')
    parser.add_argument('--data_geojson',       type=str, default='data_geojson',       help = 'output .geojson file')
    args = parser.parse_args()    
    data_input_raw     = args.data_input_raw
    data_processed_gpx = args.data_processed_gpx
    data_geojson       = args.data_geojson 


ingest_file_list = glob.glob(os.path.join(data_input_raw, '*.gpx'))
n_files = len(ingest_file_list)
print('found %s files to process ' %(n_files))                              

f = 0
#for f in range(0, 4, 1):
for f in range(0, n_files, 1):
    print('  processing %s of %s n_files ' %(f, n_files))                              
    gpx_file_temp = ingest_file_list[f]

    lat_lon_data = []
    elevation_data = []
    dt_data = []
    timestamp_data = []

    # read GPX file
    with open(gpx_file_temp, 'r') as file:
        gpx = gpxpy.parse(file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    lat_lon_data.append([point.latitude, point.longitude])
                    elevation_data.append(point.elevation)
                    timestamp_data.append(point.time.timestamp()) # convert time to timestamps (s)
                    dt_data.append(point.time) # convert time to timestamps (s)

    lat_lon_data   = np.array(lat_lon_data)  # [deg, deg]
    elevation_data = np.array(elevation_data) # [m]
    timestamp_data = np.array(timestamp_data) # [s]

    n_points = len(timestamp_data)
    print('    read %s points ' %(n_points))    
    # calculate trackpoints distance, slope, speed and power
    distance_data = np.zeros([n_points]) # [m]
    slope_data    = np.zeros([n_points]) # [%]
    speed_data    = np.zeros([n_points]) # [m/s]

    for i in np.arange(1, n_points):
        distance_data[i] = calc_dist_from_coords(lat_lon_data[i-1, :], lat_lon_data[i, :])
        delta_elevation = elevation_data[i]-elevation_data[i-1]
        if (distance_data[i] > 0):
            slope_data[i] = delta_elevation/distance_data[i]
        distance_data[i] = np.sqrt(np.power(distance_data[i], 2.0)+np.power(delta_elevation, 2.0)) # recalculate distance to take slope into account
    for i in np.arange(1, timestamp_data.shape[0]):
        if (timestamp_data[i] != timestamp_data[i-1]):
            speed_data[i] = distance_data[i]/(timestamp_data[i]-timestamp_data[i-1])

    # filter speed and slope data (default Strava filters)
    slope_data = medfilt(slope_data, 5)
    speed_data = medfilt(speed_data, 5)

    #n_points = len(slope_data)
    #print('    read %s points ' %(n_points))    
    
    use_RDP = True
    # use Ramer–Douglas–Peucker algorithm to reduce the number of trackpoints
    if use_RDP:
        epsilon = 1 # [m]
        tmp = np.hstack((lat_lon_data, np.arange(0, lat_lon_data.shape[0]).reshape((-1, 1)))) # hack
        tmp_new = RDP(tmp, epsilon) # remove trackpoints less than epsilon meters away from the new track
        index = tmp_new[:, 2].astype(int) # hack
        lat_lon_data = lat_lon_data[index, :]
        elevation_data = elevation_data[index]
        timestamp_data = timestamp_data[index]
        distance_data = distance_data[index]
        slope_data = slope_data[index]
        speed_data = speed_data[index]
    slope_data = abs(slope_data*100) # decimal to %

    n_points = len(slope_data)
    print('    read %s points ' %(n_points))    
    
    # create GeoJSON feature collection
    features = []
    for i in np.arange(1, n_points):
        line = geojson.LineString([(lat_lon_data[i-1, 1], lat_lon_data[i-1, 0]), (lat_lon_data[i, 1], lat_lon_data[i, 0])]) # (lon,lat) to (lon,lat) format
        feature = geojson.Feature(geometry=line, properties={'elevation': float('%.1f'%elevation_data[i]), 'slope': float('%.1f'%slope_data[i]), 'speed': float('%.1f'%speed_data[i])})
        features.append(feature)

    feature_collection = geojson.FeatureCollection(features)

    file_name = os.path.basename(gpx_file_temp.strip('.gpx'))
    # write geojson file
    geojson_write_file = gpx_file_temp.replace(file_name,dt_data[0].strftime('%Y-%m-%d_%H-%M')).replace(data_input_raw,data_geojson).replace('.gpx','.geojson')        
    print('    geojson_write_file is %s ' %(geojson_write_file))
    with open(geojson_write_file, 'w') as file:
        geojson.dump(feature_collection, file)

    # rename and archive gpx file 
    gpx_file_name_archive = gpx_file_temp.replace(file_name,dt_data[0].strftime('%Y-%m-%d_%H-%M')).replace(data_input_raw,data_processed_gpx)        
    print('    gpx_file_name_archive is %s ' %(gpx_file_name_archive))
    if (' ' in gpx_file_temp):
        temp_command = 'mv -f "'+gpx_file_temp+'" '+gpx_file_name_archive
    else:
        temp_command = 'mv -f '+gpx_file_temp+' '+gpx_file_name_archive

    print('    temp_command is %s ' %(temp_command))    
    os.system(temp_command)

