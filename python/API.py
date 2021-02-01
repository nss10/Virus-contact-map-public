from flask import Flask, request, url_for, redirect
from flask_cors import CORS
from timeline_object import timelineObject
from query import getCountyLocations,getGeometryData
from response import get_response
from helper import get_json_from_path,replaceKeys
from mdb import save_to_db
import json,uuid,os,sys
app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

@app.route("/test")
def testMethod():
    return "Server running!"


@app.route(app.config['GET_COUNTY_CASES_DATA'])
def countyLocationData():
    return replaceKeys(app.config['CCD'],json.dumps(getCountyLocations(), separators=(',', ':')))


@app.route(app.config['GET_GEOMETRY_DATA'])
def ericsData():
    return json.dumps({"type": "FeatureCollection", "features": getGeometryData()})


    
