from flask import Flask, request,render_template, url_for, redirect
from flask_cors import CORS
from timeline_object import timelineObject
from query import getSpatioTemporalMatch
from response import get_response
from helper import get_json_from_path
import json,uuid
import os
app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

@app.route("/test")
def testMethod():
    return "Server running!"

@app.route(app.config['ROUTE_PROCESS_INPUT'], methods=["get"])
def process_input():
    filePath = app.config['UPLOAD_PATH'] + str(request.args.get('id'))
    radius = app.config['RADIUS_IN_MTRS'] 
    timeSpan=app.config['TIMESPAN_IN_HRS'] 
    timelineJson = get_json_from_path(filePath)
    tObj = timelineObject(timelineJson) # Convert input json into python object
    placeVisits = tObj.getPlaceVisits()
    matchLocations = getSpatioTemporalMatch(placeVisits, radius,timeSpan)
    os.remove(filePath)  # Delete tempFile once processed
    return json.dumps(get_response(matchLocations))

@app.route(app.config['ROUTE_UPLOAD_HANDLER'], methods=['POST'])
def handleFileUpload():
    htmlTag=app.config['FILE_ELEMENT_TAG']
    if htmlTag in request.files:
        jsonFile = request.files[htmlTag]
        if jsonFile.filename != '':    
            filename = str(uuid.uuid4())
            jsonFile.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            return redirect(url_for('process_input',id=filename))
    return app.config['MESSAGE_UPLOAD_ERROR']

