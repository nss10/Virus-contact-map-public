from flask import Flask
from flask import request
app = Flask(__name__)

def extract_info_from_place(place):
    place_info={}
    # if("placeVisit" in place):
        # print(place["placeVisit"])
    place_info["lat"] = place["placeVisit"]["location"]["latitudeE7"]/10000000
    place_info["lon"] = place["placeVisit"]["location"]["longitudeE7"]/10000000
    place_info["start_time"] = place["placeVisit"]["duration"]["startTimestampMs"]
    place_info["end_time"] = place["placeVisit"]["duration"]["endTimestampMs"]

    return place_info
    
@app.route("/json", methods=["POST"])
def extract_json_from_input():
    req = request.get_json()    
    placesVisited = [extract_info_from_place(place) for place in req["timelineObjects"] if "placeVisit" in place ]
    return str(placesVisited)

