from mdb import save_to_db,add_feature_data_to_collection
import requests, config as cfg
dbConf=cfg.DB

#Work in Progress
def getCountyFromPoint(lat,lon):
    content = requests.get("https://geo.fcc.gov/api/census/area?lat="+str(lat)+"&lon="+str(lon)+"&format=json")
    jsonObj = json.loads(content.content)
    return jsonObj['results'][0]['county_fips']
    

def populateErics():
    req = requests.get('https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_20m.json')
    add_feature_data_to_collection(req.json()['features'])

if __name__ == "__main__":
    populateErics()