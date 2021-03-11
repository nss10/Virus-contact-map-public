from pymongo import MongoClient, GEOSPHERE,errors
import os
import config as cfg
dbConf=cfg.DB

def add_cases_data_to_collection(countyList):
    countyCollection.drop()
    save_to_db(countyList,countyCollection)

client = MongoClient(dbConf['uri'], dbConf['port'], username=dbConf['un'],password=dbConf['pwd'],authsource=dbConf['dbname'])
db = client[dbConf["dbname"]]
countyCollectionName = dbConf['countyLocationCollection']
countyCollection = db[countyCollectionName]
metaCollection = db['metaDataCollection']

def save_to_db(pvList,collectionName,userDefinedId=False):
    for pv in pvList:
        if(userDefinedId):
            pv['_id'] = str(pv['centerLat'])+str(pv['centerLon'])+pv['duration']['startTimestampMs']+pv['duration']['endTimestampMs']
        try:
            collectionName.insert(pv, check_keys=False)
        except errors.DuplicateKeyError:
            pass
        del pv['_id']

def add_new_records(geo_id, key_name, records):
    countyCollection.update_one({"GEO_ID": geo_id},
                                {"$addToSet": {
                                        key_name: {
                                            "$each": records
                                        }
                                    }
    })


def set_last_updated_date_in_db(key, dateString):
    metaCollection.update_one({},{"$set":{key: dateString}},True)

def get_last_updated_date_in_db(key):
    return list(metaCollection.find({},{"_id":0}))[0][key]


if __name__=="__main__":
    set_last_updated_date_in_db("cases", "2021-02-01")
