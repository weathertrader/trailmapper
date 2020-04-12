
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

`mv example.gpx data_input_raw/.`

Process the `gpx` file to geojson

`python process_gpx_files_to_geojson.py --data_input_raw=data_input_raw --data_processed_gpx=data_processed_gpx --data_geojson=data_geojson`

Plot the resulting data in a web browser 

`python plot_gps_points_from_geojson.py --data_geojson=data_geojson`

## Scripts 

Ipython notebooks are 

```
plot_gps_points_from_geojson.ipynb
```

plots individual geojson file
this functinality should move to plot_master and this script should be deprecated

```
process_gps_points_to_geojson.ipynb
```
process each gpx individually to geojson and rename gpx and archive
this functionality should move process_all_gpx_to_master and this script should be deprecated


`process_all_gpx_to_master.ipynb` 
process all gpx to a single master
should this write individual geojson
does not update existing master only can write over 

`plot_master_geojson.ipynb`
reads a master geojson file and plots in a folium html map


Python scripts are 
```
Apr  5 07:04 process_gpx_files_to_geojson.py
Apr  5 07:28 plot_gps_points_from_geojson.py
Apr  5 15:11 utils.py
Apr  5 15:49 plot_master_geojson.py
Apr 11 20:08 process_all_gpx_to_master.py
```

## To do 

Show recent tracks on master map 
Add trailheads 
Add RAWS stations
Center html 



