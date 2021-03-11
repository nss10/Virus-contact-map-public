from pymongo import MongoClient
from helper import get_quantile
from functools import lru_cache
import config as cfg
import time
from datetime import date
import random
import pandas as pd
import io,os, requests
from datetime import datetime as dt
dbConf = cfg.DB
props = cfg.COUNTY_PROPS
client = MongoClient(dbConf['uri'], dbConf['port'], username=dbConf['un'],password=dbConf['pwd'],authsource=dbConf['dbname'])
db = client[dbConf["dbname"]]
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
       "properties.coords":"$coords",
       "geometry": 1
       }}
  ]))

# Try to refactor this
def getCountyLocations():
  global countyLocations
  if not isCacheValid():
    countyLocations = fetchAndUpdateCache()
  return countyLocations


def getColorCodes(series_name):
  """
    Given the county properties list and the series name
    would return a dictionary whose key represents a number and value represents a color code on [0-10] scale
  """
  countyList = getCountyLocations()
  case_count_set=set()
  for item in countyList['collection']:
    for case in item[series_name]:
      case_count_set.add(case['count'])
  return addDiffEncodingOnColorCodes(get_quantile(list(case_count_set)))

def fetchAndUpdateCache() :
  print("updating cache")
  countyCasesData = list(countyCollection.find({},{ "_id": 0,props['GEO_ID'] : 1,props['CASES']:1, props['DEATHS']:1, props['STRAIN']:1}))
  for item in countyCasesData:
    item[props['CASES']] = differentialEncode(item[props['CASES']])
    item[props['DEATHS']] = differentialEncode(item[props['DEATHS']])
  revalidateCache()
  return {"lastAvailableDay":countyCasesData[0][props['CASES']][-1]['daysElapsed'], "collection" : countyCasesData}


def isCacheValid():
  """
  Responsible for verifying whether server cache is valid
  """
  global lastFetchedDate
  return lastFetchedDate==dt.date(dt.now())

def revalidateCache():
  """
  Responsible for verifying whether server cache is valid
  """
  global lastFetchedDate
  lastFetchedDate=dt.date(dt.now())

# Methods related to Differential encoding
def differentialEncode(propList):
  oldCount=0
  resultList = []
  for prop in propList:
    if(prop['count']>0):
      if(oldCount!=prop['count']):
        oldCount=prop['count']
        resultList.append(prop)
  return resultList

def addDiffEncodingOnColorCodes(colorCodes):
  oldVal=-1
  retVal={}
  for key in sorted(list(map(int, colorCodes.keys()))):
    if(colorCodes[key]!=oldVal):
      oldVal=retVal[key]=colorCodes[key]
  return retVal
