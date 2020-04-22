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


def get_quantile(arr):
    low = 200
    up = -1
    labelList = ["rgba(254,196,233,0.4)", "rgba(245,179,212,0.4)", "rgba(237,162,192,0.4)", "rgba(229,146,172,0.4)", "rgba(220,128,149,0.4)",
                 "rgba(211,110,127,0.4)", "rgba(200,89,100,0.4)", "rgba(190,69,76,0.4)", "rgba(182,55,58,0.4)", "rgba(177,43,44,0.4)", "rgba(169,28,25,0.4)"]
    x = pd.qcut(arr, len(labelList), labels=labelList)
    return list(zip(arr, list(x)))
