
# should work from cli
# all args in cli
# environment.yml should work
# functional .gitignore 
# functional README.md 


# ./process_gpx_files_to_geojson.py --data_input_gpx=data_input_gpx --data_processed_gpx=data_processed_gpx' --data_geojson='data_geojson --visualize=False --SI-units=True


# imports
import argparse
import glob
import os
#import gpxpy
#import geojson
#import folium
#import webbrowser

import numpy as np
import matplotlib.cm as cm

from scipy.signal import medfilt

# functions
def rgb2hex(c):
    hexc = '#%02x%02x%02x'%(int(c[0]*255), int(c[1]*255), int(c[2]*255))
    return(hexc)

def calc_dist_from_coords(p1, p2): # distance between p1 and p2 [lat,lon] (in deg)
    lat1 = np.radians(p1[0])
    lat2 = np.radians(p2[0])
    lon1 = np.radians(p1[1])
    lon2 = np.radians(p2[1])

    delta_lat = lat2-lat1
    delta_lon = lon2-lon1

    # Haversine formula
    a = np.power(np.sin(delta_lat/2.0), 2)+np.cos(lat1)*np.cos(lat2)*np.power(np.sin(delta_lon/2.0), 2)
    c = 2.0*np.arctan2(np.sqrt(a), np.sqrt(1.0-a))

    dist = 6371e3*c

    return(dist)

def calc_dist_from_coordsPoint2Line(p0, p1, p2): # distance from p0 to line defined by p1 and p2 [lat,lon] (in deg)
    # Mercator projection
    P0 = np.array([np.radians(p0[1]), np.arcsinh(np.tan(np.radians(p0[0])))])*6371e3
    P1 = np.array([np.radians(p1[1]), np.arcsinh(np.tan(np.radians(p1[0])))])*6371e3
    P2 = np.array([np.radians(p2[1]), np.arcsinh(np.tan(np.radians(p2[0])))])*6371e3

    # distance from point to line
    dist = abs((P2[1]-P1[1])*P0[0]-(P2[0]-P1[0])*P0[1]+P2[0]*P1[1]-P2[1]*P1[0])/np.sqrt(np.power(P2[1]-P1[1], 2)+np.power(P2[0]-P1[0], 2)) # (from https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points)

    return(dist)

def RDP(data, epsilon): # Ramer–Douglas–Peucker algorithm
    if epsilon <= 0:
        return(data)

    dist_max = 0
    index = 0

    for i in np.arange(1, data.shape[0]):
        dist = calc_dist_from_coordsPoint2Line(data[i, :2], data[0, :2], data[-1, :2]) # needs a 2D projection, does not work with cross-track distance

        if dist > dist_max:
            index = i
            dist_max = dist

    if dist_max > epsilon:
        tmp1 = RDP(data[:index+1, :], epsilon)
        tmp2 = RDP(data[index:, :], epsilon)

        data_new = np.vstack((tmp1[:-1], tmp2))
    else:
        data_new = np.vstack((data[0, :], data[-1, :]))

    return(data_new)