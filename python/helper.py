

def getTimeOverlap(original_time,current_time):
    diff = int(current_time["startTimestampMs"]) - int(original_time["startTimestampMs"])
    return diff/(1000*60*60)
