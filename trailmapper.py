
# purpose
# read individual, apply rdp, write to geojson, aggregate all to single with visit counts 

# usage
# python process_all_gpx_to_master.py --dir_gpx=data/gpx --dir_geojson=data/geojson


"""
#manual_debug = True
manual_debug = False
if (manual_debug):
    dir_work = '/home/craigmatthewsmith/gps_tracks'
    os.chdir(dir_work)
    dir_gpx     = 'data/gpx' 
    dir_geojson = 'data/geojson'
else: # parse command line parameters
    dir_work = os.getcwd()
    parser = argparse.ArgumentParser(description = 'process gpx files to geojson')
    parser.add_argument('--dir_gpx',     type=str, default='data/gpx',     help = 'data of gpx files')
    parser.add_argument('--dir_geojson', type=str, default='data/geojson', help = 'data of geojson files')
    args = parser.parse_args()    
    dir_gpx     = args.dir_gpx 
    dir_geojson = args.dir_geojson 

#gpx_file_temp = os.path.join(dir_work, 'data_input_gpx/Afternoon_Run55.gpx')
#print(os.path.isfile(gpx_file_temp))


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

lat_all = []
lon_all = []
ele_all = []
dt_all  = []

f = 100
#for f in range(0, 20, 1):
#for f in range(0, 50, 1):
for f in range(0, n_files, 1):
    if (f%20 == 0):
        print('  processing f %s of %s ' %(f, n_files)) 

    #lat_lon_temp = []

    # rename and archive gpx file 
    gpx_file_name_archive = gpx_file_temp.replace(file_name,dt_temp[0].strftime('%Y-%m-%d_%H-%M'))
    # print('    gpx_file_name_archive is %s ' %(gpx_file_name_archive))
    if not (gpx_file_temp == gpx_file_name_archive):
        if (' ' in gpx_file_temp):
            temp_command = 'mv -f "'+gpx_file_temp+'" '+gpx_file_name_archive
        else:
            temp_command = 'mv -f '+gpx_file_temp+' '+gpx_file_name_archive
        os.system(temp_command)
        
    if (f == 0):
        lat_all = lat_temp
        lon_all = lon_temp
        ele_all = ele_temp
        dt_all  = dt_temp
    else: 
        lat_all = np.hstack([lat_all, lat_temp])
        lon_all = np.hstack([lon_all, lon_temp])
        ele_all = np.hstack([ele_all, ele_temp])
        dt_all  = np.hstack([ dt_all,  dt_temp])
    del lon_temp, lat_temp, ele_temp, dt_temp 
    n_points_all = len(lat_all)
    #print('  %s total points ' %(n_points_all))    

print('eps %5.1f %s total points ' %(epsilon, n_points_all))    
n_time_visited = np.full([n_points_all], 1, dtype=int)

time_end   = time.time()
process_dt = (time_end-time_start)/60.0
print(process_name+' took %5.2f min' %(process_dt))



process_name = 'thin nearby points'
time_start = time.time()

# count and reduce nearby points
n = 10000
for n in range(0, n_points_all, 1):
    if (n%10000 == 0):
        print('  processing n %s of %s ' %(n, n_points_all)) 
    lat_temp = lat_all[n]
    lon_temp = lon_all[n]
    ele_temp = ele_all[n]
    #print(lat_temp, lon_temp, ele_temp)
    #dist_temp = (lat_all-lat_temp)**2.0 + (lon_all-lon_temp)**2
    #print(np.shape(dist_temp))
    #print(np.shape(dist_temp))
    #print(np.min(dist_temp))
    #print(np.max(dist_temp))
    #dist_temp

    if not (np.isnan(lon_temp)):
        dist_temp = calc_dist_between_one_point_to_all_points(lon_temp, lat_temp, lon_all, lat_all)
        index_close = np.argwhere(dist_temp < dist_min_aggregate_points)
        n_nearby_points = len(index_close)
        #print('    found %s nearby points ' %(n_nearby_points)) 
        if (n_nearby_points > 1):
            lon_avg = np.mean(lon_all[index_close])
            lat_avg = np.mean(lat_all[index_close])
            ele_avg = np.mean(ele_all[index_close])
            #print(lat_temp, lon_temp, ele_temp)
            #print(lat_avg, lon_avg, ele_avg)
            #print(index_close)
            #print(lon_all[index_close])
            #print(lat_all[index_close])
            #print(ele_all[index_close])
            lon_all[index_close] = np.nan
            lat_all[index_close] = np.nan
            ele_all[index_close] = np.nan
            lon_all[n] = lon_avg
            lat_all[n] = lat_avg
            ele_all[n] = ele_avg
            n_time_visited[n] = n_nearby_points
            del lon_avg, lat_avg, ele_avg
        del dist_temp, index_close, n_nearby_points

print('n_times visited ranges from %5.0f - %5.0f' % (np.nanmin(n_time_visited), np.nanmax(n_time_visited)))


n_points_all_old = n_points_all
#print(np.shape(lat_all))
mask = ~np.isnan(lat_all)
lon_all = lon_all[mask] 
lat_all = lat_all[mask] 
ele_all = ele_all[mask] 
n_time_visited = n_time_visited[mask] 
n_points_all = len(lat_all)
print('%s dist_min reduced points from %s to %s ' %(dist_min_aggregate_points, n_points_all_old, n_points_all))    

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
#import folium
#import geopandas
import glob
import gpxpy
import geojson
#import webbrowser
#import matplotlib.cm as cm
#from scipy.signal import medfilt

from utils import calc_dist_from_coords
from utils import rgb2hex
from utils import calc_dist_between_two_coords
from utils import calc_dist_between_one_point_to_all_points
"""




import argparse
import os
import glob
import sys
import numpy as np
import time
import geojson
import gpxpy
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

def plot_gps_tracks(dir_data):
    file_type = "geojson"
    file_list = get_list_of_files_to_process(dir_data, file_type)

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

"""
Usage 

Plot all tracks. 
python trailmapper.py --mode process_gps_tracks --dir_data data
python trailmapper.py --mode plot_geojson --dir_data data

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


"""
# debug 
dir_data = "data"
file_type = "gpx"
input_file = file_list[10]
"""





