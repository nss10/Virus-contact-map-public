import os

UPLOAD_PATH= os.getcwd()+"\\tempFiles\\"
GET_COUNTY_CASES_DATA='/countyCasesData'
GET_GEOMETRY_DATA='/geometryData'
BACKEND_REMOTE=False
CCD={
    "GEO_ID": "ID",
    "NAME": "N",
    "confirmed_cases": "CC",
    "deaths": "D",
    "daysElapsed": "DE",
    "count": "C",
    "isPredicted":"IP",
    "strain_data":"SD"
}


DB_LOCAL={
    "uri":'localhost',
    "port":27017,   
    "dbname":"testdb",
    "un":"",
    "pwd":"",
    "countyLocationCollection" : "countyLocations"
}
DB_REMOTE={
    "uri":'<remote_server_url>',
    "port":25564,
    "dbname":"covid19",
    "un":"<db_un>",
    "pwd":"<db_pwd>",
    "countyLocationCollection" : "countyLocations"    
}
DB=DB_REMOTE if BACKEND_REMOTE else DB_LOCAL

COUNTY_PROPS={
    "GEO_ID" : "GEO_ID",
    "CASES" : "confirmed_cases",
    "DEATHS" : "deaths",
    "STRAIN" : "strain_data", 
    "MOBILTY" : "mobility_data"
}