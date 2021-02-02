from pymongo import MongoClient, GEOSPHERE,errors
from helper import get_json_from_path
from timeline_object import timelineObject
import os
import config as cfg
dbConf=cfg.DB

def add_cases_data_to_collection(countyList):
    countyCollection.drop()
    save_to_db(countyList,countyCollection)

client = MongoClient(dbConf['uri'], dbConf['port'], username=dbConf['un'],password=dbConf['pwd'],authsource=dbConf['dbname'])
db = client[dbConf["dbname"]]
countyCollection = db[dbConf['countyLocationCollection']]


def save_to_db(pvList,collectionName,userDefinedId=False):

    for pv in pvList:
        if(userDefinedId):
            pv['_id'] = str(pv['centerLat'])+str(pv['centerLon'])+pv['duration']['startTimestampMs']+pv['duration']['endTimestampMs']
        try:
            collectionName.insert(pv)
        except errors.DuplicateKeyError:
            pass
        del pv['_id']
