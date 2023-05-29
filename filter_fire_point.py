import numpy as np
import pandas as pd

import rasterio.features
import rasterio.mask

import fiona
import geopandas as gpd
import shapely.geometry


# Open the raster file
with rasterio.open('path/to/raster.tif') as src:
    # Read the raster data as an array
    raster_data = src.read(1)
    # Get the transform information
    transform = src.transform

    # Open the shapefile and read its features into a DataFrame
    with fiona.open('path/to/shapefile.shp') as shp:
        df = pd.DataFrame(shp)

    # Extract the point coordinates from the 'geometry' column in the DataFrame
    df['geometry'] = df['geometry'].apply(shapely.geometry.shape)
    df['x'] = df['geometry'].apply(lambda x: x.coords[0][0])
    df['y'] = df['geometry'].apply(lambda x: x.coords[0][1])

    # Transform the coordinates to pixel values
    df['px'] = ((df['x'] - transform[0]) / transform[1]).astype(int)
    df['py'] = ((df['y'] - transform[3]) / transform[5]).astype(int)

    # Get the values of the pixels at the positions of the points
    pixel_vals = raster_data[df['py'], df['px']]

    # Find the features with points at pixels with value 1
    df_filtered = df[pixel_vals == 1]

    # Convert the DataFrame to a GeoDataFrame
    gdf_filtered = gpd.GeoDataFrame(df_filtered, crs=shp.crs)

    # Save the filtered features to a GeoPackage file
    gdf_filtered.to_file('path/to/filtered_features.gpkg', driver='GPKG')

    # Print the results
    print(f"Found {len(df_filtered)} features located at pixels with value 1.")
    print(gdf_filtered[['x', 'y']].values)