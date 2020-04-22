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
BACKEND_REMOTE=True
DB_LOCAL={
    "uri":'localhost',
     "port":27017,   
    "dbname":"testdb",
    "collection":"placesVisited",
    "dailyCollection":"latestCollection",
    "countyLocationCollection" : "countyLocations"
}
DB_REMOTE={
    "uri":'173.28.146.185',
    "port":25564,
    "dbname":"covid19",
    "un":"admin",
    "pwd":"covid19 sucks",
    "collection":"infectedPlaces",
    "dailyCollection":"latestCollection",
    "countyLocationCollection" : "countyLocations"
}
DB=DB_REMOTE if BACKEND_REMOTE else DB_LOCAL
