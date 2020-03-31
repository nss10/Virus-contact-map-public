import os
TEST="Hello World from Config file"
RADIUS_IN_MTRS=50
TIMESPAN_IN_HRS=3*24
UPLOAD_PATH= os.getcwd()+"\\tempFiles\\"
MESSAGE_UPLOAD_ERROR = "Upload Error"
FILE_ELEMENT_TAG='jsonFile'
ROUTE_UPLOAD_HANDLER='/handleUpload'
ROUTE_PROCESS_INPUT='/processJson'
DB_LOCAL={
    "uri":'localhost',
     "port":27017,   
    "dbname":"testdb",
    "collection":"placesVisited"
}
DB_REMOTE={
    "uri":'173.28.146.185',
    "port":27017,
    "dbname":"covid19",
    "collection":"infectedPlaces"
}

