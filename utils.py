
# imports
import numpy as np
from scipy.signal import medfilt

# functions
def rgb2hex(c):
    hexc = '#%02x%02x%02x'%(int(c[0]*255), int(c[1]*255), int(c[2]*255))
    return(hexc)

def calc_dist_between_two_coords(lon0, lat0, lon1, lat1):
    lat0_rad = np.radians(lat0)
    lat1_rad = np.radians(lat1)
    lon0_rad = np.radians(lon0)
    lon1_rad = np.radians(lon1)

    delta_lat = lat1_rad - lat0_rad
    delta_lon = lon1_rad - lon0_rad

    # apply haversine formula
    a = (np.sin(delta_lat/2.0))**2.0 + np.cos(lat0)*np.cos(lat1)*((np.sin(delta_lon/2.0))**2.0)
    c = 2.0*np.arctan2(np.sqrt(a), np.sqrt(1.0-a))

    # note csmith - here need to change '*c', can move to front or should be ^^3*c
    #dist = 6371.0e3*c
    r = 6371.0*1000.0
    dist = r*c
    
    return(dist)


def calc_dist_from_coords(p1, p2): # distance between p1 and p2 [lat,lon] (in deg)
    lat1 = np.radians(p1[0])
    lat2 = np.radians(p2[0])
    lon1 = np.radians(p1[1])
    lon2 = np.radians(p2[1])

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Haversine formula
    a = np.power(np.sin(delta_lat/2.0), 2)+np.cos(lat1)*np.cos(lat2)*np.power(np.sin(delta_lon/2.0), 2)
    c = 2.0*np.arctan2(np.sqrt(a), np.sqrt(1.0-a))

    #dist = 6371e3.0*c
    dist = 6371e3*c
    
    return(dist)

def calc_dist_from_coords_to_line(lon_point, lat_point, lon_line_start, lat_line_start, lon_line_end, lat_line_end): 
    # assume mercator projection
    # note csmith - may have lon and lat reversed here, trying these substitutions 
    
    #p0[0]
    #lon_point
    #p0[1]
    #lat_point
    #
    #p1[0]
    #lon_line_start
    #p1[1]
    #lat_line_start
    #
    #p2[0]
    #lon_line_end
    #p2[1]
    #lat_line_end

    r = 6371.0*1000.0
    
    # Mercator projection
    P0 = r*np.array([np.radians(lat_point),      np.arcsinh(np.tan(np.radians(lon_point)))])
    P1 = r*np.array([np.radians(lat_line_start), np.arcsinh(np.tan(np.radians(lon_line_start)))])
    P2 = r*np.array([np.radians(lon_line_end),   np.arcsinh(np.tan(np.radians(lon_line_end)))])

    # distance from point to line
    # (from https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points)
    dist = abs((P2[1]-P1[1]) * P0[0] - (P2[0]-P1[0]) * P0[1]+P2[0]*P1[1]-P2[1]*P1[0]) / np.sqrt(np.power(P2[1]-P1[1],2) + np.power(P2[0]-P1[0],2)) 

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
    if (epsilon <= 0):
        return(data)

    dist_max = 0
    index = 0

    for i in np.arange(1, data.shape[0]):
        dist = calc_dist_from_coordsPoint2Line(data[i,:2], data[0,:2], data[-1,:2]) # needs a 2D projection
        
        if (dist > dist_max):
            index = i
            dist_max = dist

    if (dist_max > epsilon):
        tmp1 = RDP(data[:index+1,:], epsilon)
        tmp2 = RDP(data[index:  ,:], epsilon)
        data_new = np.vstack((tmp1[:-1], tmp2))
    else:
        data_new = np.vstack((data[0,:], data[-1,:]))

    return(data_new)

