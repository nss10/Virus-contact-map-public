from flask import Flask, request
from flask_cors import CORS
import json

from query import getCountyLevelData,getGeometryData,getColorCodes
from helper import replaceKeys

app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

@app.route("/")
def testMethod():
    return "Server running!"

@app.route("/countyCasesData")
def countyLocationData():
    return replaceKeys(app.config['CCD'],json.dumps(getCountyLevelData(), separators=(',', ':')))

@app.route("/geometryData")
def geometryData():
    return json.dumps({"type": "FeatureCollection", "features": getGeometryData()})

@app.route("/colorCodes/<prop>")
def colorCodes(prop):
    colorCodeProperty = prop or app.config['COUNTY_PROPS']['CASES']
    print(colorCodeProperty)
    return json.dumps(getColorCodes(colorCodeProperty))

    
