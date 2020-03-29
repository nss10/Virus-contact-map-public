from flask import Flask, request,render_template, url_for, redirect
from timeline_object import timelineObject
from query import getSpatioTemporalMatch
from response import get_response
from helper import get_json_from_path
import json,uuid
import os
app = Flask(__name__)



@app.route("/json", methods=["get"])
def extract_json_from_input():
    filePath = os.getcwd()+"\\tempFiles\\"+ str(request.args.get('id'))
    timelineJson = get_json_from_path(filePath)
    radius = 20 # in meters    
    timeSpan=3 * 24 # in hours
    tObj = timelineObject(timelineJson)
    placeVisits = tObj.getPlaceVisits()
    matchLocations = getSpatioTemporalMatch(placeVisits, radius,timeSpan)
    os.remove(filePath)
    return json.dumps(get_response(matchLocations))

@app.route("/handleUpload", methods=['POST'])
def handleFileUpload():
    if 'jsonFile' in request.files:
        jsonFile = request.files['jsonFile']
        if jsonFile.filename != '':    
            filename = str(uuid.uuid4())
            jsonFile.save(os.path.join(os.getcwd() + '\\tempFiles', filename))
            return redirect(url_for('extract_json_from_input',id=filename))
    return "Upload Error!"

