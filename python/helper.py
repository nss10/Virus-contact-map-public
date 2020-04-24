import json
import time
import requests
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon 

def getTimeOverlap(infectedTime, userTime):
    '''
    Computes the difference in time in terms of number of hours and returns a floating point number
    '''
    if(userTime["endTimestampMs"] < infectedTime["startTimestampMs"]):
        #  infected person visited after user left : No Chance of overlap
        return -1

    elif(infectedTime["endTimestampMs"] < userTime["startTimestampMs"]):
        # user visited after infected person left : Returns the time gap between visits
        diff = int(userTime["startTimestampMs"]) - int(infectedTime["startTimestampMs"])
        return diff

    else:
        # both are at the same place with some time overlap
        return 0


def getTimeSince(infectedTime):
    diff = time.time() - int(infectedTime["startTimestampMs"])
    return diff

def get_json_from_path(path):
    with open(path) as json_file:
        return json.load(json_file)


def get_latest_cases_count(county):
    return county[0]['confirmed_cases'][-1]['count']


def get_quantile(arr):
    low = 200
    up = -1
    arr=list(dict.fromkeys(arr))
    labelList = ["rgba(254,196,233,0.4)", "rgba(245,179,212,0.4)", "rgba(237,162,192,0.4)", "rgba(229,146,172,0.4)", "rgba(220,128,149,0.4)",
                 "rgba(211,110,127,0.4)", "rgba(200,89,100,0.4)", "rgba(190,69,76,0.4)", "rgba(182,55,58,0.4)", "rgba(177,43,44,0.4)", "rgba(169,28,25,0.4)"]
    x = pd.qcut(arr, len(labelList), labels=labelList)
    return dict((x,y) for x,y in zip(arr, list(x)))


def getCountyFromPoint(lat,lon):
    content = requests.get("https://geo.fcc.gov/api/census/area?lat="+str(lat)+"&lon="+str(lon)+"&format=json")
    jsonObj = json.loads(content.content)
    return jsonObj['results'][0]['county_fips']

def isPointInCounty(lat,lon, county_dict, get_geometry_from_erics, poly_dict={}):
    for county_fips in county_dict:
        if(county_fips not in poly_dict):
            poly_dict[county_fips] = get_geometry_from_erics(county_fips)
        p1 = Point(lon,lat)
        poly = Polygon(poly_dict[county_fips])
        if(p1.within(poly)):
            return True
    return False


if __name__ == "__main__":
    print(isPointInCounty())