def get_response_format_per_location(place, locations):
    """
    This is a helper method for the get_response method. 
    :param: - locations
        (List of all locations in the initial format)\n
    :return: - response
        (List of all Json objects in the format required in the response)\n
    """
    nearby=[]
    currentLocList=[]
    for loc in locations:
        if loc["place_location"]["address"] not in currentLocList:
            # Filtering duplicates
            nearby.append(
                {    
                    "id" : str(loc["_id"]),
                    "Address" : loc["place_location"]["address"],
                    "coordinates":{
                        "lat" : loc["place_location"]["lat"],
                        "lon" : loc["place_location"]["lon"]
                    },
                    "Confidence" : loc["visitConfidence"],
                    "timestamp" : loc["duration"],
                    "timeDifference": loc["timeDifference"]
                }
            )
            currentLocList.append(loc["place_location"]["address"])
    return {
        "place":place,
        "nearby" : nearby
    }

def get_response(matchLocations):
    '''
        Parses the locations that are a spatiotemporal match into a format that is suitable for the response
    '''
    response=[]
    for key in matchLocations:
        response.append(get_response_format_per_location(key,matchLocations[key]))
    return response
    