# %%
import geopandas as gpd
import pandas as pd
import math
import numpy as np

counties = gpd.read_file("/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/county_cities_filtered(interaction).gpkg")
counties = counties.to_crs(epsg='4326')
counties.info()
counties_with_fire = counties.copy()
# %%
years = range(2014,2021)

clipped_data_root="/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/clipped_data"
for data_year in years:

    fire_df = pd.read_csv(clipped_data_root+"/Landsat_{}_clipped.csv".format(data_year))
    fire_df.info()
    #geometry =gpd.GeoSeries.from_wkt(fire_df["geometry"])
    geometry = gpd.points_from_xy(fire_df.loc[:,"lon"], fire_df.loc[:,"lat"])
    fire_points = gpd.GeoDataFrame(
        fire_df[["id", "date", "time", "confidence"]], geometry=geometry
    )

    # 如果使用inner merge，会忽略无数据的行
    counties_with_fire=counties_with_fire.merge(
        counties.sjoin(
    			fire_points
    		).groupby(
    			'AD2004'
    		)['AD2004'].count().rename(
    			"fire_{}".format(data_year)
    		).reset_index(), on='AD2004', how='left'
    	)

    counties_with_fire.loc[:,"fire_{}".format(data_year)].replace(np.nan, 0, inplace=True)
    counties_with_fire.info()

    # %%
# Save the result (.shp)
#counties_with_fire.to_file("/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/counties_with_fire_{}".format(data_year),encoding='gbk')
counties_with_fire.to_file("/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/counties_with_fire_landsat",encoding='gbk')

