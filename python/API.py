from flask import Flask, request,render_template, url_for, redirect
from flask_cors import CORS
from timeline_object import timelineObject
from query import getSpatioTemporalMatch,getAllInfectedLocations
from response import get_response
from helper import get_json_from_path
from mdb import save_to_db,get_place_visits
import json,uuid,os,sys
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

@app.route("/allData")
def intialData():
    return json.dumps(getAllInfectedLocations())


@app.route(app.config['ROUTE_UPLOAD_HANDLER'], methods=['POST'])
def handleFileUpload():
    htmlTag=app.config['FILE_ELEMENT_TAG']
    if htmlTag in request.files:
        jsonFile = request.files[htmlTag]
        if jsonFile.filename != '':    
            filename = str(uuid.uuid4())
            jsonFile.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            return redirect(url_for('process_input',id=filename))
        else:
            return app.config['MESSAGE_UPLOAD_ERROR']
    errorFiles=[]
    shouldUpload=True
    for i in [1,2]:
        tagName = htmlTag+str(i)
        if(tagName in request.files):
            if(not uploadFile(request.files[tagName],errorFiles,shouldUpload)):
                shouldUpload=False
    if(len(errorFiles) > 0):
        return app.config['MESSAGE_UPLOAD_ERROR'] + ":\n " + str(errorFiles)
    else:
        return app.config['MESSAGE_DATA_SAVED']


def uploadFile(file,errorFiles, shouldUpload=True):
    try:
        jsonObj = json.load(file)
        pvList=get_place_visits(jsonObj)
    except:
        e = sys.exc_info()[0]
        print("Exception caught " + str(e) + " while adding "+file.filename)
        errorFiles.append(file.filename)
        return False
    
    if shouldUpload:
        print('Uploading ',len(pvList),' records to db from file: ',file.filename)
        save_to_db(pvList)
        return True
    else:
        print('Not Uploading ',file.filename,' records to db')
        return False

