from functools import lru_cache
from datetime import datetime as dt

from mdb import getGeometryDataFromDB, getCountyDataFromDB
from helper import get_quantile
import config as cfg

props = cfg.COUNTY_PROPS
countyLocations = {}
lastFetchedDate = dt(2020,1,22)

@lru_cache
def getGeometryData():
  """
  Fetches the Geometry data for all the counties from DB and returns a copy while caching a copy in the server
  """
  return getGeometryDataFromDB()

def getCountyLevelData():
  """
    County level data is returned from cache, if exists. Else fetched from db and returned
  """
  global countyLocations
  if not isCacheValid():
    countyLocations = fetchAndUpdateCache()
  return countyLocations

def getColorCodes(series_name):
  """
    Given the county properties list and the series name
    would return a dictionary whose key represents a number and value represents a color code on [0-10] scale
  """
  countyList = getCountyLevelData()
  case_count_set=set()
  for item in countyList['collection']:
    for case in item[series_name]:
      case_count_set.add(case['count'])
  return addDiffEncodingOnColorCodes(get_quantile(list(case_count_set)))

def fetchAndUpdateCache() :
  print("updating cache")
  countyCasesData = getCountyDataFromDB(props)
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


''' Methods related to Differential encoding '''

def differentialEncode(propList):
  oldCount=0
  resultList = []
  for prop in propList:
    if(prop['count']>0 and oldCount!=prop['count']):
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
