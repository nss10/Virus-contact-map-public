
def get_response_format_per_location(locations):
    """
    This is a helper method for the get_response method. 
    :param: - locations
        (List of all locations in the initial format)\n
    :return: - response
        (List of all Json objects in the format required in the response)\n
    """
    response=[]
    
    for loc in locations:
        response.append(
            {    
                "Address" : loc["place_location"]["address"],
                "Confidence" : loc["visitConfidence"],
                "timestamp" : loc["duration"],
                "timeDifference": loc["timeDifference"]
            }
        )
    return response


def get_response(matchLocations):
    '''
        Parses the locations that are a spatiotemporal match into a format that is suitable for the response
    '''
    response={}
    for matchLocation in matchLocations:
        for key in matchLocation:
            if(key in response):
                response[key]+=get_response_format_per_location(matchLocation[key])
            else:
                response[key] = get_response_format_per_location(matchLocation[key])
    return response