
# My Route Map

Create a interactive map of all of your gps tracks 

Inline-style: 
![alt text](example.png "hover text")

## Table of Contents
1. [Installation](README.md#installation)
1. [Run Instructions](README.md#Run-instructions)
1. [Scripts](README.md#Scripts)
1. [To do](README.md#To-do)

## Installation

Clone the repo and enter the dictory.  

Create the python environment and change to it

`conda env create -f environment.yml`

`conda activate env_gis`

## Run Instructions

Move the example.gpx file into the directory that contains files to process.

`mv example.gpx data/gpx/.`

Process the `gpx` file to geojson

`python process_all_gpx_to_master.py --dir_gpx=data/gpx --dir_geojson=data/geojson`

Plot the resulting data in a web browser 

`python plot_gps_points_from_geojson.py --data_geojson=data/geojson`

## Scripts 


read individual gpx , apply rdp, write to geojson, aggregate all to single with visit counts 
```
process_all_gpx_to_master.py
process_all_gpx_to_master.ipynb
```

```
plot_gps_points_from_geojson.ipynb

```

plots individual geojson file
this functinality should move to plot_master and this script should be deprecated


`plot_master_geojson.ipynb`
reads a master geojson file and plots in a folium html map


```
plot_gps_points_from_geojson.py
plot_master_geojson.py
```

## To do 

Show recent tracks on master map in different color
Add trailheads 
Add RAWS stations
Center map in html page and adjust zoom 



