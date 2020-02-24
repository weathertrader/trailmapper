

###############################################################################
# process_gps_files_to_csv.py
# author: Craig Smith 
# purpose: process gpx files to a single csv 
# revision history:  
#   02/22/2020 - original 
# data required: 
#   gpx files 
# usage:  
#   python /home/craigmatthewsmith/gps_tracks/gps_tracks/process_gps_files_to_csv.py 
# to do: 
#   - 
# notes: 
#   - 
# debugging: 
#   - 
###############################################################################


import os
import glob
import lxml

# set working directory


dir_work = '/home/craigmatthewsmith/gps_tracks/gps_tracks'
os.chdir(dir_work)
dir_data_raw       = os.path.join(dir_work, 'data_raw')
dir_data_processed = os.path.join(dir_work, 'data_processed')


file_list = glob.glob(os.path.join(dir_data_raw, '*.gpx'))
n_files = len(file_list)


lon_list = []
lat_list = []

f = 0
for f in range(0, n_files, 1):
    file_temp = file_list[f]
    file_open = open(file_temp,'r')
    file_lines = file_open.readlines()
    n_lines = len(file_lines)
    n = 9 
    for n in range(0, n_lines ,1): 
        #print(config_lines[n])
        line_strip = file_lines[n].strip()
        #print (line_strip)
        if   ('<trkpt ' in line_strip):
            line_split = line_strip.split('"')
            lon_list.append(float(line_split[1]))
            lat_list.append(float(line_split[3]))
            del line_split
        del line_strip
    file_open.close()
    os.sys('mv -f '+file_temp+' '+dir_data_processed+'/')

n_points = len(lon_list)
n_points


import numpy as np
import pandas as pd

np.array(lon_list, dtype=float)

np.array([0, 1, 2])

temp1 = np.array([np.array(lon_list, dtype=float), np.array(lat_list, dtype=float)])
np.shape(temp1)
np.type(temp1)
type(temp1)


[lon_list, lat_list]

# create a df
points_df = pd.DataFrame(np.array([lon_list, lat_list]).T, index=np.arange(0, n_points, 1), columns=['lat', 'lon'])
points_df.head()
#points_df.index.name = 'index'
# write to csv
points_file_name = os.path.join(dir_work, 'points.csv')
points_df.to_csv(points_file_name) 
 
# read from csv

points_file_name = os.path.join(dir_work, 'points.csv')
if not os.path.isfile(points_file_name):
    print('ERROR - missing file')
    
points1_df = pd.read_csv(points_file_name,index_col=0)
lon_array = np.array(points1_df['lon'])
lat_array = np.array(points1_df['lat'])

stn_read_df_matrix = stn_read_csv.as_matrix()
var_wrf_read   = stn_read_df_matrix
datetime_wrf_temp = stn_read_csv.index # object 
nt_wrf = len(datetime_wrf_temp)
datetime_str = ["%s" % x for x in datetime_wrf_temp] 
datetime_wrf_utc = []
datetime_wrf_lst = []
for n in range(0,nt_wrf,1):
datetime_wrf_utc.append(datetime.datetime.strptime(datetime_str[n],'%Y-%m-%d %H:%M:00'))     
datetime_wrf_lst.append(datetime_wrf_utc[n] - datetime.timedelta(hours=utc_conversion))     



# write to csv
# read from csv spyder
# move read_from_csv to ipynb
# plot 




#<trkpt lat="37.8626060" lon="-121.9783720">
#<ele>200.3</ele>
#<time>2020-02-15T20:50:38Z</time>

 


write_csv

read_csv

above look for csv and append if exists or replace 


