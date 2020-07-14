import os
TEST="Hello World from Config file"
RADIUS_IN_MTRS=50
TIMESPAN_IN_HRS=3*24
UPLOAD_PATH= os.getcwd()+"\\tempFiles\\"
MESSAGE_UPLOAD_ERROR = "MESSAGE : Upload Error"
MESSAGE_DATA_SAVED = "MESSAGE : Data added to database succesfully"
FILE_ELEMENT_TAG='jsonFile'
ROUTE_UPLOAD_HANDLER='/handleUpload'
ROUTE_PROCESS_INPUT='/processJson'
GET_ALL_INFECTED_DATA='/allData'
GET_COUNTY_CASES_DATA='/countyCasesData'
GET_ERICS_DATA='/ericsData'
BACKEND_REMOTE=False
FLASK_HOME='C:\\Users\\nvas_\\Documents\\VCM\\Virus-Contact-Map\\python\\'
CCD={
    "GEO_ID": "ID",
    "NAME": "N",
    "confirmed_cases": "CC",
    "deaths": "D",
    "daysElapsed": "DE",
    "count": "C"
}


DB_LOCAL={
    "uri":'localhost',
    "port":27017,   
    "dbname":"testdb",
    "un":"",
    "pwd":"",
    "collection":"placesVisited",
    "dailyCollection":"latestCollection",
    "countyLocationCollection" : "countyLocations",
    "ericsCollection" : "ericsCollection"
}
DB_REMOTE={
    "uri":'173.28.146.185',
    "port":25564,
    "dbname":"covid19",
    "un":"admin",
    "pwd":"covid19 sucks",
    "collection":"infectedPlaces",
    "dailyCollection":"latestCollection",
    "countyLocationCollection" : "countyLocations",
    "ericsCollection" : "ericsCollection"
}
DB=DB_REMOTE if BACKEND_REMOTE else DB_LOCAL
