import numpy as np
import pandas as pd

import rasterio.features
import rasterio.mask

import geopandas as gpd
from shapely.geometry import Point

# Open the raster file
with rasterio.open("/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/no_repro_binary_landuse/binary_landuse_oriproj.tif") as src:
    years = range(2017,2022)

    clipped_data_root="/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/clipped_data"
    for data_year in years:

        # Read the raster data as an array
        raster_data = src.read(1)
        # Get the transform information
        transform = src.transform
        print((transform))
        # Read the point coordinates from the CSV file into a DataFrame
        coords_df = pd.read_csv(clipped_data_root+"/VIIRS_{}_clipped.csv".format(data_year))
        print(coords_df.info())
        coords_df.drop("geometry",axis=1,inplace=True)
        # Create a Point GeoDataFrame from the coordinates
        geometry = gpd.points_from_xy(coords_df.loc[:,"lon"], coords_df.loc[:,"lat"])
        #geometry = [Point(xy) for xy in zip(coords_df['lon'], coords_df['lat'])]
        gdf = gpd.GeoDataFrame(coords_df, crs='EPSG:4326', geometry=geometry)
        # Transform the GeoDataFrame to the same CRS as the raster data
        gdf = gdf.to_crs(src.crs)

        # Transform the point coordinates to pixel values
        
        gdf['px'] = ((gdf['geometry'].x - transform[2]) / transform[0]).astype(int)
        gdf['py'] = ((gdf['geometry'].y - transform[5]) / transform[4]).astype(int)

        # Get the values of the pixels at the positions of the points
        pixel_vals = raster_data[gdf['py'], gdf['px']].copy()
        # Find the points with pixel values of 1
        gdf_filtered = gdf[pixel_vals == 2]
        # Save the filtered points to a GeoPackage file
        #gdf_filtered[["id","lon","lat","date","time","brightness","confidence"]].to_csv(clipped_data_root+"/VIIRS_{}_clipped_incity.csv".format(data_year),)
        gdf_filtered.to_csv(clipped_data_root+"/VIIRS_{}_clipped_incity.csv".format(data_year),)
        # Print the results
        print(f"Found {len(gdf_filtered)} points located at pixels with value 1.")
        print(gdf_filtered[['lon', 'lat']].values)