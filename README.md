
# My Route Map

Create a interactive map of all of your gps tracks 

Inline-style: 
![alt text](example.png "hover text")

## Table of Contents
1. [Installation](README.md#installation)
1. [Run Instructions](README.md#Run-instructions)
1. [Scripts](README.md#Scripts)
1. [To do](README.md#To-do)
1. [References](README.md#References)

## Installation

Clone the repo and build the image. 

`docker build -t tm_image .`


## Run Instructions

Run the image with an attached volume.

`docker run -it --rm -v $(pwd):/app --name=tm_cont tm_image /bin/bash`

Move your gpx files into the `data/gpx` directory.

Process the gpx file to geojson with  

```
python trailmapper.py --mode process_gps_tracks --dir_data data
```

And plot the tracks with 

```
python trailmapper.py --mode plot_gps_tracks --dir_data data

```

Now navigate to the repository folder and double-click the `heatmap.html` to view the 
tracks in a web browser.  


## To do 

### Map
1. Add RAWS stations
2. Add Trailheads from Maps
2. Fix the master geojson colormap so that saturation occurs at 10 
3. grab tracks via API instead of manually 
4. thin points
5. add junctions 

### Track processing
- redo track simplify algorithm on individual gpx using Shapely default RDP   
- remove stopped data using speed_min 
