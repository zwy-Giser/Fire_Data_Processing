# %% [markdown]
# # Concat data and save to csv
# %%
import pandas as pd
import os
import copy
import geopandas as gpd
import pandas as pd
import os 
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import geoplot

# %%
years = range(2014,2021)
raw_data_root="/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/landsat8_raw_data"
all_data_root="/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/yearly_raw_data"
cliped_data_root="/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/clipped_data"
for data_year in years:
    month_data_root = raw_data_root+"/{}".format(data_year)

    data_aggregate = pd.DataFrame([])
    for root, _, files in os.walk(month_data_root):
        for file in files:
            print(file)
            data = pd.read_csv(os.path.join(root, file),index_col=False)
            print(len(data))
            if data_aggregate.empty:
                data_aggregate = copy.deepcopy(data)
            else:

                data_aggregate = pd.concat([data_aggregate, data], axis=0, ignore_index=True)
                # data_aggregate = data_aggregate.append(data, ignore_index=True)


    data_aggregate.rename(columns={" lon": "lon", " lat": "lat", " date":"date", " time":"time"}, inplace=True)
    print(data_aggregate.info())
    # Keep only relevant columns
    fire_df = data_aggregate.loc[:, ("id", "lon", "lat", "date", "time", "confidence")]
    fire_df.info()

    fire_df.to_csv(os.path.join(all_data_root+"/Landsat_{}_all.csv".format(data_year)))


# %%
# data clip 
    geometry = gpd.points_from_xy(fire_df.loc[:,"lon"], fire_df.loc[:,"lat"])
    fire_points = gpd.GeoDataFrame(
        fire_df[["id","lon","lat","date", "time", "confidence"]], geometry=geometry
    )

    fire_points.head()
    len(fire_points)

    # %%
    study_area = gpd.read_file("/Users/zwy/Library/CloudStorage/Dropbox/work files/Policy impact on fire/county_cities_filtered(interaction).gpkg")
    study_area = study_area.to_crs("EPSG:4326")
    study_area.head()
    fire_clipped = fire_points.clip(study_area)

    # Plot the clipped data
    # The plot below shows the results of the clip function applied to the capital cities
    """ax = geoplot.kdeplot(fire_clipped)
    study_area.boundary.plot(ax=ax, color="green")
    ax.set_title("VIIRS Fire 2017", fontsize=20)
    ax.set_axis_off()
    plt.show()"""

    # %%
    len(fire_clipped)

    # %%
    fire_clipped.to_csv(cliped_data_root+"/Lansat_{}_clipped.csv".format(data_year))

# %%




