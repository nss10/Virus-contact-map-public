BACKEND_REMOTE=False
MAPBOX_TOKEN='pk.eyJ1IjoiemFjaGFyeTgxNiIsImEiOiJjazd6NXN2eWwwMml0M2tvNGo2c3JkcGFpIn0.aB1upejZ61JQjb_z2g1NuA'
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
COUNTY_PROPS={
    "GEO_ID" : "GEO_ID",
    "CASES" : "confirmed_cases",
    "DEATHS" : "deaths",
    "STRAIN" : "strain_data", 
    "MOBILTY" : "mobility_data"
}