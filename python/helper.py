import json
import time
import requests
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon
from datetime import datetime


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

def getDaysSinceTimeLineEpoch(timeInMs):
    diff = datetime(2020, 5, 17) - datetime.fromtimestamp(int(timeInMs)/1000.0)
    return diff.days


def get_json_from_path(path):
    with open(path) as json_file:
        return json.load(json_file)


def get_latest_cases_count(county,daysSinceEpoch):
    firstConfirmedCaseDay = int(county['confirmed_cases'][0]['daysElapsed'])
    return county['confirmed_cases'][daysSinceEpoch-firstConfirmedCaseDay]['count'] if firstConfirmedCaseDay < daysSinceEpoch < int(county['confirmed_cases'][-1]['daysElapsed'])else 0


def get_quantile(arr):
    arr = list(dict.fromkeys(arr))
    if(len(arr)==1):
        return {arr[0] : 5} # If single county returns median color from the list
    labelList = list(range(11))
    x = pd.qcut(arr, len(labelList), labels=labelList)
    return dict((x, y) for x, y in zip(arr, list(x)))


def getCountyFromPoint(lat, lon):
    content = requests.get(
        "https://geo.fcc.gov/api/census/area?lat="+str(lat)+"&lon="+str(lon)+"&format=json")
    jsonObj = json.loads(content.content)
    return jsonObj['results'][0]['county_fips']


def isPointInCounty(lat, lon, county_dict, get_geometry_from_erics, poly_dict={}):
    for county_fips in county_dict:
        if(county_fips not in poly_dict):
            poly_dict[county_fips] = get_geometry_from_erics(county_fips)
        p1 = Point(lon, lat)
        poly = Polygon(poly_dict[county_fips])
        if(p1.within(poly)):
            return True
    return False


def getRiskScore(place):
    diff = int(place['duration']['endTimestampMs']) - int(place['duration']['endTimestampMs'])
    minute = 60*1000
    if(diff >= 30*minute):
        return 1
    elif(diff >=15*minute):
        return 0.7
    else:
        return 0

def replaceKeys(config,source):
    for key in config.keys():
        source = source.replace(key,config[key])
    return source
if __name__ == "__main__":
    print(get_quantile([1,1]))
