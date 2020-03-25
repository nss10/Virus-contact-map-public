
def get_response_format_per_location(locations):
    response=[]
    
    for loc in locations:
        response.append(
            {
            
            "Address" : loc["place_location"]["address"],
            "Confidence" : loc["visitConfidence"],
            "timestamp" : loc["duration"],
            "timeDifference": loc["timeDifference"],
            "temp" :loc["temp"]
            }
        )
    return response

def get_response(matchLocations):
    response={}
    for matchLocation in matchLocations:
        for key in matchLocation:
            if(key in response):
                response[key]+=get_response_format_per_location(matchLocation[key])
            else:
                response[key] = get_response_format_per_location(matchLocation[key])
    return response