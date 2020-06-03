from flask import Flask, request,render_template, url_for, redirect,flash,render_template
from flask_cors import CORS
from timeline_object import timelineObject
from query import getSpatioTemporalMatch,getAllInfectedLocations,updateCacheAndFetch,getCountyLocations,get_county_matches,getEricsData,filterPlacesStayedLongerThan
from response import get_response
from helper import get_json_from_path,replaceKeys
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
    timelineJson = get_json_from_path(filePath)
    os.remove(filePath)  # Delete tempFile once processed
    tObj = timelineObject(timelineJson) # Convert input json into python object
    placeVisits = tObj.getPlaceVisits()
    placeVisits = filterPlacesStayedLongerThan(placeVisits, 10*60*1000) #10 minutes
    if(request.args.get('uploadOption') == "countyLevel"):
        countyMatches = get_county_matches(placeVisits)
        return json.dumps({"uploadOption": "countyLevel","placesVisited" : placeVisits, "counties" : countyMatches})
    elif(request.args.get('uploadOption') == "infectedPlaces"):
        radius = int(request.args.get('radius')) 
        timeSpan=int(request.args.get('time'))  
        matchLocations = getSpatioTemporalMatch(placeVisits, radius,timeSpan)
        return json.dumps({"uploadOption": "infectedPlaces", "infectedPlaces":  get_response(matchLocations)})


@app.route(app.config['GET_ALL_INFECTED_DATA'])
def intialData():
    return json.dumps(getAllInfectedLocations())


@app.route(app.config['GET_COUNTY_CASES_DATA'])
def countyLocationData():
    countyCasesData =  json.dumps(getCountyLocations(), separators=(',', ':'))
    return replaceKeys(app.config['CCD'],countyCasesData)


@app.route(app.config['GET_ERICS_DATA'])
def ericsData():
    return json.dumps({"type": "FeatureCollection", "features": getEricsData()})


@app.route(app.config['ROUTE_UPLOAD_HANDLER'], methods=['POST'])
def handleFileUpload():
    htmlTag = app.config['FILE_ELEMENT_TAG']
    if htmlTag in request.files:
        jsonFile = request.files[htmlTag]
        if jsonFile.filename != '':
            filename = str(uuid.uuid4())
            jsonFile.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            return redirect(url_for('process_input', id=filename, uploadOption=request.form['uploadOption'], radius=int(request.form['radius']), time=int(request.form['time'])))
        else:
            return app.config['MESSAGE_UPLOAD_ERROR']
    errorFiles = []
    uploadList = []
    shouldUpload = True
    for i in [1, 2]:
        tagName = htmlTag+str(i)
        if(tagName in request.files):
            shouldUpload = shouldUpload and uploadFile(
                request.files[tagName], errorFiles, uploadList)

    if shouldUpload:
        save_to_db(uploadList,userDefinedId=True)

    if(len(errorFiles) > 0):
        return app.config['MESSAGE_UPLOAD_ERROR'] + ":\n " + str(errorFiles)
    else:
        updateCacheAndFetch()
        return app.config['MESSAGE_DATA_SAVED']


def uploadFile(file,errorFiles, uploadList):
    try:
        jsonObj = json.load(file)
        uploadList+=get_place_visits(jsonObj)
        return True
    except:
        e = sys.exc_info()[0]
        print("Exception caught " + str(e) + " while adding "+file.filename)
        errorFiles.append(file.filename)
        return False
    
