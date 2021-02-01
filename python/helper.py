import json
import time
import requests
import pandas as pd
from datetime import datetime

def getDaysSinceTimeLineEpoch(timeInMs):
    diff = datetime(2020, 5, 17) - datetime.fromtimestamp(int(timeInMs)/1000.0)
    return diff.days


def getDiffDaysSinceDataEpoch(newDate):
    diff = newDate - datetime(2020, 1, 22)
    return diff.days


def get_json_from_path(path):
    with open(path) as json_file:
        return json.load(json_file)


def get_latest_cases_count(county, daysSinceEpoch):
    firstConfirmedCaseDay = int(county['confirmed_cases'][0]['daysElapsed'])
    return county['confirmed_cases'][daysSinceEpoch-firstConfirmedCaseDay]['count'] if firstConfirmedCaseDay < daysSinceEpoch < int(county['confirmed_cases'][-1]['daysElapsed'])else 0


def get_quantile(arr):
    arr = list(dict.fromkeys(arr))
    if(len(arr) == 1):
        # If single county returns median color from the list
        return {arr[0]: 5}
    labelList = list(range(11))
    x = pd.qcut(arr, len(labelList), labels=labelList)
    return dict((x, y) for x, y in zip(arr, list(x)))


def replaceKeys(config, source):
    for key in config.keys():
        source = source.replace(key, config[key])
    return source