

def getTimeOverlap(original_time,current_time):
    '''
    Computes the difference in time in terms of number of hours and returns a floating point number
    '''
    diff = int(current_time["startTimestampMs"]) - int(original_time["startTimestampMs"])
    return diff/(1000*60*60)


def get_json_from_path(path):
    with open(path) as json_file:
            return json.load(json_file)