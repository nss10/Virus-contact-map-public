from pymongo import MongoClient, GEOSPHERE
from helper import get_json_from_path
from timeline_object import timelineObject
import os
import config as cfg
dbConf=cfg.DB_REMOTE #cfg.DB_LOCAL, cfg.DB_REMOTE

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

def save_to_db(jsonObj):
    pvList = get_place_visits(jsonObj)
    for pv in pvList:
        collection.insert(pv)

def process():
    for dirname, _, filenames in os.walk("../json/"):
        for filename in filenames:
            if("test" in dirname):
                continue
            jsonObject = get_json_from_path(os.path.join(dirname, filename))
            save_to_db(jsonObject)

    collection.create_index([("location", GEOSPHERE)])
# process()