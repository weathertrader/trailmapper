
# purpose 
# read individual, apply rdp, aggregate all to single with visit counts 

# usage
# python process_all_gpx_to_master.py --dir_gpx_processed=data/gpx_processed

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



use_RDP  = True
epsilon  = 1.0 # [m]
dist_min = 1.0 # 1.0, 75752 to 65536, 5386531 master.geojson file size 
dist_max = 100.0 # dont plot lines this far away




lat_all = []
lon_all = []
ele_all = []

f = 100
#for f in range(0, 20, 1):
#for f in range(0, n_files, 1):
for f in range(0, 50, 1):
    if (f%10 == 0):
        print('  processing f %s of %s ' %(f, n_files)) 

    lat_lon_temp = []
    lat_temp = []
    lon_temp = []
    ele_temp = []

    gpx_file_temp = ingest_file_list[f]
    # read GPX file
    with open(gpx_file_temp, 'r') as file:
        gpx = gpxpy.parse(file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    #lat_lon_temp.append([point.latitude, point.longitude])
                    lon_temp.append([point.longitude])
                    lat_temp.append([point.latitude])
                    ele_temp.append(point.elevation)

    #lat_lon_temp = np.array(lat_lon_temp)  # [deg, deg]
    lon_temp = np.array(lon_temp) 
    lat_temp = np.array(lat_temp) 
    ele_temp = np.array(ele_temp) 

    n_points = len(lon_temp)
    #print('    read %s points ' %(n_points)) 
    n_points_old = n_points

    # use Ramer–Douglas–Peucker algorithm to reduce the number of trackpoints
    if (use_RDP):
        temp_array = np.hstack([lat_temp, lon_temp, np.arange(0, n_points, 1).reshape(-1, 1)])
        temp_array_new = RDP(temp_array, epsilon) # remove trackpoints less than epsilon meters away from the new track
        index = temp_array_new[:,2].astype(int) # hack
        ele_temp = np.squeeze(ele_temp[index])
        lon_temp = np.squeeze(lon_temp[index])
        lat_temp = np.squeeze(lat_temp[index])
        n_points = len(lon_temp)
        #print('    reduced points from %s to %s ' %(n_points_old, n_points))    
    if (f == 0):
        lat_all = lat_temp
        lon_all = lon_temp
        ele_all = ele_temp
    else: 
        lat_all = np.hstack([lat_all, lat_temp])
        lon_all = np.hstack([lon_all, lon_temp])
        ele_all = np.hstack([ele_all, ele_temp])
    del lon_temp, lat_temp, ele_temp        
    n_points_all = len(lat_all)
    #print('  %s total points ' %(n_points_all))    


n_all = np.full([n_points_all], 0, dtype=int)
print('%s total points ' %(n_points_all))    

# count and reduce nearby points
n = 10000
for n in range(0, n_points_all, 1):
    if (n%1000 == 0):
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
        index_close = np.argwhere(dist_temp < dist_min)
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
            n_all  [n] = n_nearby_points
            del lon_avg, lat_avg, ele_avg
        del dist_temp, index_close, n_nearby_points



n_points_all_old = n_points_all
#print(np.shape(lat_all))
mask = ~np.isnan(lat_all)
lon_all = lon_all[mask] 
lat_all = lat_all[mask] 
ele_all = ele_all[mask] 
n_all   =   n_all[mask] 
n_points_all = len(lat_all)
print('reduced points from %s to %s ' %(n_points_all_old, n_points_all))    


# here need to check raw points vs thinned points on a map 
# by default connect every adjancet point unless it is too far away
features_thin = []

n = 1000
for n in range(1, n_points_all, 1):
    if (n%1000 == 0):
        print('  processing n %s of %s ' %(n, n_points_all)) 
    dist_temp = calc_dist_between_two_coords(lon_all[n], lat_all[n], lon_all[n-1], lat_all[n-1])
    n_temp = max(1, n_all[n])
    if (dist_temp < dist_max):
        line = geojson.LineString([(lon_all[n], lat_all[n]), (lon_all[n-1], lat_all[n-1])])     
        feature = geojson.Feature(geometry=line, properties={'n_times': int('%.0f'%n_temp)})
        #feature = geojson.Feature(geometry=line, properties={'n_times': int('%.0f'%n_times)})
        features_thin.append(feature)
        del n_temp, line, feature
    

feature_collection_thin = geojson.FeatureCollection(features_thin)
#file_name = 'master_thin.geojson'
file_name = 'master_thin_min_'+str(int(dist_min))+'_max_'+str(int(dist_max))+'.geojson'
#geojson_write_file = os.path.join(dir_work, file_name)
geojson_write_file = file_name
print('  geojson_write_file is %s ' %(geojson_write_file))
if os.path.isfile(geojson_write_file):
    temp_command = 'rm '+geojson_write_file
    os.system(temp_command)
with open(geojson_write_file, 'w') as file:
    geojson.dump(feature_collection_thin, file)



