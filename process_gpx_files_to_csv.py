
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
import numpy as np
import pandas as pd

# set working directory
dir_work = '/home/craigmatthewsmith/gps_tracks'
os.chdir(dir_work)
dir_data_raw       = os.path.join(dir_work, 'data_raw')
dir_data_processed = os.path.join(dir_work, 'data_processed')

# find files to read
file_list = glob.glob(os.path.join(dir_data_raw, '*.gpx'))
n_files = len(file_list)

print('found %s files ' %(str(n_files).rjust(2,'0')))

lon_list  = []
lat_list  = []
ele_list  = []
time_list = []
f = 0
for f in range(0, n_files, 1):
    print('processing f %s ' %(str(f).rjust(2,'0')))
    file_temp = file_list[f]
    file_open = open(file_temp,'r')
    file_lines = file_open.readlines()
    n_lines = len(file_lines)
    n = 9 
    #for n in range(0, 20 ,1): 
    for n in range(0, n_lines ,1): 
        #print(file_lines[n])
        line_strip = file_lines[n] # .strip()
        #print (line_strip)
        if   ('<trkpt ' in line_strip):
            line_split = line_strip.split('"')
            lon_list.append(float(line_split[1]))
            lat_list.append(float(line_split[3]))
            del line_split
        elif (' <ele>' in line_strip):
            ele_list.append(float(line_strip.split('<')[1].split('>')[1]))
        elif ('    <time>' in line_strip):
            time_list.append(line_strip.split('<')[1].split('>')[1])
        del line_strip
    file_open.close()
    #os.system('mv -f '+file_temp+' '+dir_data_processed+'/')

n_points = len(lon_list)
print('found %s points ' %(n_points))
n_points = len(ele_list)
print('found %s points ' %(n_points))
n_points = len(time_list)
print('found %s points ' %(n_points))

#np.array(lon_list, dtype=float)
#np.array([0, 1, 2])
#temp1 = np.array([np.array(lon_list, dtype=float), np.array(lat_list, dtype=float)])
#np.shape(temp1)
#np.type(temp1)
#type(temp1)
#[lon_list, lat_list]


#var_temp = np.array([lon_list, lat_list, ele_list, time_list]).T
#columns_temp = ['lat', 'lon', 'ele', 'time']

#np.shape(lon_list)
#np.shape(lat_list)
#np.shape(ele_list)
#np.shape(time_list)

# create a df
points_new_df = pd.DataFrame(np.array([lon_list, lat_list, ele_list, time_list]).T, index=np.arange(0, n_points, 1), columns=['lat', 'lon', 'ele', 'time'])
points_new_df.head()

# check for pre-existing file and append
points_file_name = os.path.join(dir_work, 'points.csv')
if os.path.isfile(points_file_name):
    print('appending to existing file')
    points_old_df = pd.read_csv(points_file_name,index_col=0)
    #lon_array = np.array(points1_df['lon'])
    #lat_array = np.array(points1_df['lat'])
    points_old_df = points_old_df.append(points_new_df)
else:
    points_old_df = points_new_df
del points_new_df

# write to csv
points_old_df.to_csv(points_file_name) 
 
# parse dts
#stn_read_df_matrix = stn_read_csv.as_matrix()
#var_wrf_read   = stn_read_df_matrix
#datetime_wrf_temp = stn_read_csv.index # object 
#nt_wrf = len(datetime_wrf_temp)
#datetime_str = ["%s" % x for x in datetime_wrf_temp] 
#datetime_wrf_utc = []
#datetime_wrf_lst = []
#for n in range(0,nt_wrf,1):
#    datetime_wrf_utc.append(datetime.datetime.strptime(datetime_str[n],'%Y-%m-%d %H:%M:00'))     
#    datetime_wrf_lst.append(datetime_wrf_utc[n] - datetime.timedelta(hours=utc_conversion))     


#<trkpt lat="37.8626060" lon="-121.9783720">
#<ele>200.3</ele>
#<time>2020-02-15T20:50:38Z</time>

