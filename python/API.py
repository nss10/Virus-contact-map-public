from flask import Flask
from flask import request
from timeline_object import timelineObject
from query import get_neighbouring_places
from query import getSpatioTemporalMatch
from response import get_response
import json
app = Flask(__name__)



@app.route("/json", methods=["POST"])
def extract_json_from_input():
    response="Success"
    timelineJson = request.get_json()    
    tObj = timelineObject(path_to_json=None, timeline_json=timelineJson)
    placeVisits = tObj.getPlaceVisits()
    matchLocations = getSpatioTemporalMatch(placeVisits, 50)
    return json.dumps(get_response(matchLocations))



