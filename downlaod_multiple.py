import requests
import time

satlite = "landsat8" # viirs
for year in range(2017, 2021):
    for month in range(1, 13):
        url = "http://satsee.radi.ac.cn:8080/fireproductdownload.aspx?id={sat}_m{year}{month}.csv&satellite={sat2}".format(sat = satlite, year = year, month = month, sat2 = satlite)
        trycnt = 3  # max try cnt
        while trycnt > 0:
            try:
                filename = "{sat}_m{year}{month}.csv".format(sat = satlite, year = year, month = month)

                response = requests.get(url)

                with open("./data/"+filename, "wb") as file:
                    file.write(response.content)

                print(f"File '{filename}' downloaded successfully.")
                trycnt = 0 # success
            except Exception as ex:
               if trycnt <= 0: print("Failed to retrieve: " + url + "\n" + str(ex))  # done retrying
               else: trycnt -= 1  # retry
               time.sleep(0.5)  # wait 1/2 second then retry
         # go to next URL