import json,time

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