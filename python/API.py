from flask import Flask, request
from timeline_object import timelineObject
from query import getSpatioTemporalMatch
from response import get_response
import json
app = Flask(__name__)



@app.route("/json", methods=["POST"])
def extract_json_from_input():
    timelineJson = request.get_json()
    radius = 50 # in meters    
    timeSpan=5 # in hours
    tObj = timelineObject(timelineJson)
    placeVisits = tObj.getPlaceVisits()
    matchLocations = getSpatioTemporalMatch(placeVisits, 50,5)
    return json.dumps(get_response(matchLocations))



