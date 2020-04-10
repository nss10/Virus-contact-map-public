from pymongo import MongoClient, GEOSPHERE,errors
from helper import get_json_from_path
from timeline_object import timelineObject
import os
import config as cfg
dbConf=cfg.DB

def get_activity_segments(path):
    to = timelineObject(jsonObject)
    asList = to.getActivitySegments()
    return asList

def get_place_visits(jsonObject):
    to = timelineObject(jsonObject)
    pvList = to.getPlaceVisits()
    return pvList

client = MongoClient(dbConf['uri'], dbConf['port'])
db = client[dbConf["dbname"]]
collection = db[dbConf['collection']]


paths = []

def save_to_db(pvList,collectionName=collection,userDefinedId=False):    
    for pv in pvList:
        if(userDefinedId and collectionName==collection):
            pv['_id'] = str(pv['centerLat'])+str(pv['centerLon'])+pv['duration']['startTimestampMs']+pv['duration']['endTimestampMs']
        try:
            collectionName.insert(pv)
        except errors.DuplicateKeyError:
            pass
        del pv['_id']
    if(collectionName==collection):
        collection.create_index([("location", GEOSPHERE)])
def process():
    for dirname, _, filenames in os.walk("../json/"):
        for filename in filenames:
            if("test" in dirname):
                continue
            jsonObject = get_json_from_path(os.path.join(dirname, filename))
            pvList = get_place_visits(jsonObject)
            save_to_db(pvList)
