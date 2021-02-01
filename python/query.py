from pymongo import MongoClient
from helper import *
from functools import lru_cache
import config as cfg
from mdb import save_to_db
import time
from datetime import date
import random
import pandas as pd
import io,os, requests
from datetime import datetime as dt
dbConf = cfg.DB

client = MongoClient(dbConf['uri'], dbConf['port'], username=dbConf['un'],password=dbConf['pwd'],authsource=dbConf['dbname'])
db = client[dbConf["dbname"]]
collection = db[dbConf['collection']]
countyCollection = db[dbConf['countyLocationCollection']]
countyLocations = {}
ericsData = {}
lastFetchedDate = dt(2020,1,22)

@lru_cache
def getGeometryData():

  return list(countyCollection.aggregate([
      {"$project": {
       "_id": 0,
       "properties.GEO_ID":"$GEO_ID",
       "properties.NAME":"$NAME",
       "geometry": 1
       }}
  ]))

# Try to refactor this
def getCountyLocations():
  global countyLocations
  if not isCacheValid():
    countyLocations = fetchAndUpdateCache()
  return countyLocations
    

def fetchAndUpdateCache() :
  print("updating cache")
  countyCasesData = list(countyCollection.find({},{ "_id": 0,"GEO_ID" : 1,"NAME":0,"confirmed_cases":1, "deaths":1}))
  case_count_set=set()
  for item in countyCasesData:
    item['confirmed_cases'] = differentialEncode(item['confirmed_cases'])
    item['deaths'] = differentialEncode(item['deaths'])
    for case in item['confirmed_cases']:
      case_count_set.add(case['count'])
  colorCodes = get_quantile(list(case_count_set))
  colorCodesDiffEncoded = addDiffEncodingOnColorCodes(colorCodes)
  validateCache()
  return {"lastAvailableDay":countyCasesData[0]['confirmed_cases'][-1]['daysElapsed'], "colorCodes" : colorCodesDiffEncoded,"collection" : countyCasesData}
  


# Methods resonsible for validating and 
def isCacheValid():
  global lastFetchedDate
  return lastFetchedDate==dt.date(dt.now())

def validateCache():
  global lastFetchedDate
  lastFetchedDate=dt.date(dt.now())

# Methods related to Differential encoding

def differentialEncode(propList):
  oldCount=0
  resultList = []
  for case in propList:
    if(case['count']>0):
      if(oldCount!=case['count']):
        oldCount=case['count']
        resultList.append(case)
  return resultList

def addDiffEncodingOnColorCodes(colorCodes):
  oldVal=-1
  retVal={}
  for key in sorted(list(map(int, colorCodes.keys()))):
    if(colorCodes[key]!=oldVal):
      oldVal=retVal[key]=colorCodes[key]
  return retVal
