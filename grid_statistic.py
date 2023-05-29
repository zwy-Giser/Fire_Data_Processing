# %%
import geopandas as gpd
import pandas as pd
import math
import numpy as np

counties = gpd.read_file("/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/county_cities_filtered(interaction).gpkg")
counties = counties.to_crs(epsg='4326')
counties.info()


# %%
bounds = counties.bounds
lon1 = bounds.minx.min()
lon2 = bounds.maxx.max()
lat1 = bounds.miny.min()
lat2 = bounds.maxy.max()

latStart = min(lat1, lat2);
lonStart = min(lon1, lon2);

#定义栅格大小(单位m)
accuracy = 5000;

#计算栅格的经纬度增加量大小▲Lon和▲Lat
deltaLon = accuracy * 360 / (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360));
deltaLat = accuracy * 360 / (2 * math.pi * 6371004);

# %%
from shapely.geometry import Point,Polygon,shape

#定义空的geopandas表
grid = gpd.GeoDataFrame()

#定义空的list，后面循环一次就往里面加东西
LONCOL = []
LATCOL = []
geometry = []
HBLON1 = []
HBLAT1 = []

#计算总共要生成多少个栅格
#lon方向是lonsnum个栅格
lonsnum = int((lon2-lon1)/deltaLon)+1
#lat方向是latsnum个栅格
latsnum = int((lat2-lat1)/deltaLat)+1

for i in range(lonsnum):
    for j in range(latsnum):

        HBLON = i*deltaLon + (lonStart - deltaLon / 2)
        HBLAT = j*deltaLat + (latStart - deltaLat / 2)
        #把生成的数据都加入到前面定义的空list里面
        LONCOL.append(i)
        LATCOL.append(j)
        HBLON1.append(HBLON)
        HBLAT1.append(HBLAT)
        
        #生成栅格的Polygon形状
        #这里我们用周围的栅格推算三个顶点的位置，否则生成的栅格因为小数点取值的问题会出现小缝，无法完美覆盖
        HBLON_1 = (i+1)*deltaLon + (lonStart - deltaLon / 2)
        HBLAT_1 = (j+1)*deltaLat + (latStart - deltaLat / 2)
        geometry.append(Polygon([
        (HBLON-deltaLon/2,HBLAT-deltaLat/2),
        (HBLON_1-deltaLon/2,HBLAT-deltaLat/2),
        (HBLON_1-deltaLon/2,HBLAT_1-deltaLat/2),
        (HBLON-deltaLon/2,HBLAT_1-deltaLat/2)]))
        
#为geopandas文件的每一列赋值为刚刚的list
grid['grid_id'] = range(len(LONCOL))
grid['LONCOL'] = LONCOL
grid['LATCOL'] = LATCOL
grid['HBLON'] = HBLON1
grid['HBLAT'] = HBLAT1
grid['geometry'] = geometry
grid.info()
grid_with_fire = grid.copy()
# %%
years = range(2021,2022)

clipped_data_root="/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/clipped_data"
for data_year in years:
    fire_df = pd.read_csv(clipped_data_root+"/VIIRS_{}_clipped_incity.csv".format(data_year))
    fire_df.info()
    #geometry =gpd.GeoSeries.from_wkt(fire_df["geometry"])
    geometry = gpd.points_from_xy(fire_df.loc[:,"lon"], fire_df.loc[:,"lat"])
    fire_points = gpd.GeoDataFrame(
        fire_df[["id", "date", "time", "brightness", "confidence"]], geometry=geometry
    )

    # %%
    grid_with_fire=grid_with_fire.merge(
    		grid.sjoin(
    			fire_points
    		).groupby(
    			'grid_id'
    		)['grid_id'].count().rename(
    			"fire_{}".format(data_year)
    		).reset_index(), on='grid_id', how='left'
    	)

    grid_with_fire.loc[:,"fire_{}".format(data_year)].replace(np.nan, 0, inplace=True)
    grid_with_fire.info()
    grid_with_fire = grid_with_fire[grid_with_fire.intersects(counties.unary_union)]
    # %%
    # draw the map, only use for single year
    """grid_with_fire = grid_with_fire[grid_with_fire.intersects(counties.unary_union)]
    grid_with_fire.plot(column='fire', cmap='OrRd', legend=True, figsize=(20,20))"""

# %%
grid_with_fire.to_file("/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/grid_with_fire_{}_incity.shp".format(data_year))
#grid_with_fire.to_file("/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/grid_with_fire_viirs_incity.shp")



