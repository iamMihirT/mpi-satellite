import pandas as pd
from dateutil import parser
import spacy
import re
from geopy.geocoders import Nominatim
import geopandas as gpd
from shapely.geometry import Point
import json
import logging
from sentinelhub import SHConfig   
import datetime
import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import time
from geopy.exc import GeocoderUnavailable

from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    DownloadRequest,
    MimeType,
    MosaickingOrder,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    bbox_to_dimensions,
)
from utils import plot_image

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logging.captureWarnings(True)

# Load data from JSON file
with open('C:/Users/Mihir Trivedi/Desktop/final code/data_aug.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

df = pd.DataFrame(data)

def get_bounding_box(place_name):
    geolocator = Nominatim(user_agent="place_boundary")
    location = geolocator.geocode(place_name)
    
    if location:
        # Get latitude and longitude
        lat, lon = location.latitude, location.longitude
        
        # Define a bounding box around the location (adjust the size as needed)
        bounding_box = {
            'min_latitude': lat - 0.16,
            'max_latitude': lat + 0.16,
            'min_longitude': lon - 0.35,
            'max_longitude': lon + 0.35
        }
        
        return bounding_box
    else:
        return None

# Add bounding box to the DataFrame
df['bounding_box'] = df['extracted.location'].apply(get_bounding_box)

# Define SentinelHub configuration
config = SHConfig()
config.sh_client_id = "35c2e8f8-8796-450a-9770-f4e481949986"
config.sh_client_secret = "Y*X?HpB9W4N&#lWKt!1CQL3cj-)r(6M{n}Nuj6QD"
config.save()

config = SHConfig()

if not config.sh_client_id or not config.sh_client_secret:
    print("Warning! To use Process API, please provide the credentials (OAuth client ID and client secret).")

# Set resolution
resolution = 60

# Create a DataFrame for coordinates and sizes
coords_list = []
coords_size_list = []

for index, row in df.iterrows():
    bounding_box_dict = row['bounding_box']

    if bounding_box_dict is not None:
        min_lat = bounding_box_dict['min_latitude']
        max_lat = bounding_box_dict['max_latitude']
        min_lon = bounding_box_dict['min_longitude']
        max_lon = bounding_box_dict['max_longitude']

        coords_wgs84 = (min_lon, min_lat, max_lon, max_lat)
        coords_bbox = BBox(bbox=coords_wgs84, crs=CRS.WGS84)
        coords_size = bbox_to_dimensions(coords_bbox, resolution=resolution)

        coords_list.append((min_lon, min_lat, max_lon, max_lat))
        coords_size_list.append(coords_size)
    else:
        coords_list.append(())
        coords_size_list.append(None)

df_coords = pd.DataFrame({
    'coords': coords_list,
    'coords_size': coords_size_list
})

# Drop rows with empty coordinates
df_coords = df_coords.dropna()

# SentinelHub evalscript for true color imagery
evalscript_true_color = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04"]
            }],
            output: {
                bands: 3
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B04, sample.B03, sample.B02];
    }
"""

# Loop through DataFrame and request true color images
for index, row in df_coords.iterrows():
    coords = row['coords']
    coords_size = row['coords_size']

    if coords:
        min_lon, min_lat, max_lon, max_lat = coords
        coords_bbox = BBox((min_lon, min_lat, max_lon, max_lat), crs=CRS.WGS84)

        # Request true color images
        request_true_color = SentinelHubRequest(
            evalscript=evalscript_true_color,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L1C,
                    time_interval=("2023-01-09", "2023-10-09"),
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
            bbox=coords_bbox,
            size=coords_size,
            config=config,
        )
        true_color_imgs = request_true_color.get_data()

        # Plot and save images
        image = true_color_imgs[0]
        plot_image(image, factor=3.5 / 255, clip_range=(0, 1))

        image_filename = f"true_color_image_{index}.png"
        image_path = os.path.join("C:/Users/Mihir Trivedi/Desktop/final code/img_generated", image_filename)

        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        im = Image.fromarray((image * 255).astype('uint8'))
        im.save(image_path)

        print(f"Image saved to: {image_path}")

# Additional code for handling the returned data
print(f"Returned data is of type = {type(true_color_imgs)} and length {len(true_color_imgs)}.")
print(f"Single element in the list is of type {type(true_color_imgs[-1])} and has shape {true_color_imgs[-1].shape}")
