import json,time,requests,numpy as np,pandas as pd
from shapely.geometry import Point,Polygon

def getTimeOverlap(infectedTime,userTime):
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
    diff = time.time()- int(infectedTime["startTimestampMs"])
    return diff

def get_json_from_path(path):
    with open(path) as json_file:
            return json.load(json_file)          


def get_quantile(arr):
    low=200
    up=-1
    labelList = ["#FFCC99", "#FFCC33", "#FFCC00","#FF9933","#FF9900","#FF6666","#FF6633","#FF6600","#FF0033","#FF0000","#CC0033" ]
    x = pd.qcut(arr,len(labelList),labels=labelList)
    return list(zip(arr,list(x)))


#Work in Progress
def getCountyFromPoint():
    p1 = Point(24.952242, 60.1696017)
    content = requests.get("https://geo.fcc.gov/api/census/area?lat="+str(24.952242)+"&lon="+str(60.1696017)+"&format=json")
    jsonObj = json.loads(content.content)
    print(jsonObj)

# isPointInCounty()