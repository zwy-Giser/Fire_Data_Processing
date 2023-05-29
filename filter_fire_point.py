import numpy as np
import pandas as pd

import rasterio.features
import rasterio.mask

import geopandas as gpd
from shapely.geometry import Point


# Open the raster file
with rasterio.open('path/to/raster.tif') as src:
    # Read the raster data as an array
    raster_data = src.read(1)
    # Get the transform information
    transform = src.transform

    # Read the point coordinates from the CSV file into a DataFrame
    coords_df = pd.read_csv('path/to/coords.csv')

    # Create a Point GeoDataFrame from the coordinates
    geometry = [Point(xy) for xy in zip(coords_df['lon'], coords_df['lat'])]
    gdf = gpd.GeoDataFrame(coords_df, crs='EPSG:4326', geometry=geometry)
    # Transform the GeoDataFrame to the same CRS as the raster data
    gdf = gdf.to_crs(src.crs)

    # Transform the point coordinates to pixel values
    gdf['px'] = ((gdf['geometry'].x - transform[0]) / transform[1]).astype(int)
    gdf['py'] = ((gdf['geometry'].y - transform[3]) / transform[5]).astype(int)

    # Get the values of the pixels at the positions of the points
    pixel_vals = raster_data[gdf['py'], gdf['px']]

    # Find the points with pixel values of 1
    gdf_filtered = gdf[pixel_vals == 1]

    # Save the filtered points to a GeoPackage file
    gdf_filtered.to_file('path/to/filtered_points.gpkg', driver='GPKG')

    # Print the results
    print(f"Found {len(gdf_filtered)} points located at pixels with value 1.")
    print(gdf_filtered[['lon', 'lat']].values)