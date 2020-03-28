
# should work from cli
# all args in cli
# environment.yml should work
# functional .gitignore 
# functional README.md 
# myroutemap

# ./process_gpx_files_to_geojson.py --data_input_gpx=data_input_gpx --data_processed_gpx=data_processed_gpx' --data_geojson='data_geojson --visualize=False --SI-units=True

# imports
#import gpxpy
#import geojson
#import folium
#import webbrowser

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

data_input_gpx = 'data_input_gpx' 
data_processed_gpx = 'data_processed_gpx' 
data_geojson = 'data_geojson'

# command line parameters
parser = argparse.ArgumentParser(description = 'Extract track, elevation, and, speed from Strava GPX files, export to GeoJSON files and visualize in browser', epilog = 'Report issues to https://github.com/remisalmon/Strava-to-GeoJSON')
parser.add_argument('--data_input_gpx',     type=str, default='data_input_gpx', help='input .gpx file')
parser.add_argument('--data_processed_gpx', type=str, default='data_processed_gpx', help = 'output .geojson file')
parser.add_argument('--data_geojson',       type=str, default='data_geojson', help = 'output .geojson file')

args = parser.parse_args()

main(args)







def gpx2geojson(gpx_file_temp, data_input_gpx, data_processed_gpx, data_geojson, use_SI=False, use_RDP=False):
     
    # initialize lists
    lat_lon_data   = []
    elevation_data = []
    timestamp_data = []
    dt_data        = []

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
    dt_data = np.array(dt_data) 
    
    n_points = len(timestamp_data)
    print('  read %s points ' %(n_points))    
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

    # use Ramer–Douglas–Peucker algorithm to reduce the number of trackpoints
    if (use_RDP):
        epsilon = 1 # [m]
        tmp = np.hstack((lat_lon_data, np.arange(0, n_points).reshape((-1, 1)))) # hack
        tmp_new = RDP(tmp, epsilon) # remove trackpoints less than epsilon meters away from the new track
        index = tmp_new[:, 2].astype(int) # hack
        lat_lon_data   = lat_lon_data  [index,:]
        elevation_data = elevation_data[index]
        timestamp_data = timestamp_data[index]
        distance_data  = distance_data [index]
        slope_data     = slope_data    [index]
        speed_data     = speed_data    [index]


    n_points = len(slope_data)
    print('  read %s points ' %(n_points))    

    # convert units
    if use_SI:
        speed_data = speed_data*3.6 # m/s to km/h
    else:
        speed_data = speed_data*2.236936 # m/s to mph

    slope_data = abs(slope_data*100) # decimal to %

    # create GeoJSON feature collection
    features = []
    for i in np.arange(1, n_points):
        #print('    processing %s of %s points ' %(i, n_points))    
        #print('    %s, %s, %s, %s ' %(lat_lon_data[i-1, 1], lat_lon_data[i-1, 0], lat_lon_data[i, 1], lat_lon_data[i, 0]))    
        try:
            line = geojson.LineString([(lat_lon_data[i-1, 1], lat_lon_data[i-1, 0]), (lat_lon_data[i, 1], lat_lon_data[i, 0])]) # (lon,lat) to (lon,lat) format
            feature = geojson.Feature(geometry=line, properties = {'elevation': float('%.1f'%elevation_data[i]), 'slope': float('%.1f'%slope_data[i]), 'speed': float('%.1f'%speed_data[i])})
            features.append(feature)
        except:
            print('    ERROR %s of %s points ' %(i, n_points))    
            
    feature_collection = geojson.FeatureCollection(features)

    file_name = os.path.basename(gpx_file_temp.strip('.gpx'))

    # write geojson file
    geojson_write_file = gpx_file_temp.replace(file_name, dt_data[0].strftime('%Y-%m-%d_%H-%M')).replace(data_input_gpx,data_geojson).replace('.gpx','.geojson')        
    print('  geojson_write_file is %s ' %(geojson_write_file))
    with open(geojson_write_file, 'w') as file:
        geojson.dump(feature_collection, file)
        
    # rename and archive gpx file 
    gpx_file_name_archive = gpx_file_temp.replace(file_name, dt_data[0].strftime('%Y-%m-%d_%H-%M')).replace(data_input_gpx,data_processed_gpx)        
    print('  gpx_file_name_archive is %s ' %(gpx_file_name_archive))
    temp_command = 'mv -f '+gpx_file_temp+' '+gpx_file_name_archive
    print('  temp_command is %s ' %(temp_command))    
    return


def main(args): # main script
    # parse arguments
    data_input_gpx     = args.data_input_gpx
    data_processed_gpx = args.data_processed_gpx
    data_geojson       = args.data_geojson
    visualize          = args.visualize # bool
    SI = True
    
    #geojson_filename = args.geojsonfile # str
    #visualize = args.visualize # bool
    #SI = args.SI # bool

    print('data_input_gpx is %s ' %(data_input_gpx))
    gpx_files_to_process = glob.glob(os.path.join(data_input_gpx, '*gpx'))
    n_gpx_files_to_process = len(gpx_files_to_process)
    if (n_gpx_files_to_process == 0):
        print('ERROR - no gpx files to process ')
        quit()
    else: 
        print('found %s gpx files to process' %(n_gpx_files_to_process))
        

    #if not geojson_filename[-8:] == '.geojson' and not geojson_filename == '':
    #    print('ERROR: --output is not a GeoJSON file')
    #    quit()
 
    # get GPX and GeoJSON filenames
    #gpx_file = glob.glob(gpx_filename)[0] # read only 1 file
    #if not gpx_file:
    #    print('ERROR: no GPX file found')
    #    quit()

    #geojson_file = geojson_filename if geojson_filename else gpx_file[:-4]+'.geojson' # use GPX filename if not specified

    # write GeoJSON file
    f = 0
    gpx_file_temp = gpx_files_to_process[f]
    for f, gpx_file_temp in enumerate(gpx_files_to_process):
        print('  processing f %s of %s, %s ' %(f, n_gpx_files_to_process, gpx_file_temp))
        gpx2geojson(gpx_file_temp, data_input_gpx, data_processed_gpx, data_geojson, use_SI=SI, use_RDP=visualize)

    # visualize GeoJSON file with Folium
    #if visualize:
    #    geojson2folium(geojson_file, use_SI = SI)




