from pymongo import MongoClient
from helper import *
import config as cfg
from mdb import save_to_db
import time
from datetime import date
import random
dbConf = cfg.DB

client = MongoClient(dbConf['uri'], dbConf['port'], username=dbConf['un'],password=dbConf['pwd'],authsource=dbConf['dbname'])
db = client[dbConf["dbname"]]
collection = db[dbConf['collection']]
perDayCollection = db[dbConf['dailyCollection']]
countyCollection = db[dbConf['countyLocationCollection']]
ericsCollection = db[dbConf['ericsCollection']]


def getCountyLocations():
  retCollection = list(countyCollection.find({},{ "_id": 0,"GEO_ID" : 1,"NAME":1,"confirmed_cases":1, "deaths":1}))
  case_count_set=set()
  for item in retCollection:
    caseList=[]
    deathList=[]
    oldCount=0
    for case in item['confirmed_cases']:
      if(case['count']>0):
        if(oldCount!=case['count']):
          oldCount=case['count']
          caseList.append(case)
        case_count_set.add(case['count'])
    oldCount=0
    for case in item['deaths']:
      if(oldCount!=case['count']):
        oldCount=case['count']
        deathList.append(case)          
    item['confirmed_cases']=caseList
    item['deaths']=deathList
  colorCodes = addDiffEncodingOnColorCodes(get_quantile(list(case_count_set)))
  return {"colorCodes" : colorCodes,"collection" : retCollection}

def getEricsData():
  return  list(ericsCollection.find({},{ "_id": 0}))
    
def getAllInfectedLocations():
  res =  list(perDayCollection.find({},{ "_id": 0}))
  if(len(res) > 0 and res[0]['loggedDate']==str(date.today())):
    print("Returning data from Cache")
    return res
  return updateCacheAndFetch()


def addDiffEncodingOnColorCodes(colorCodes):
  oldVal=-1
  retVal={}
  for key in sorted(list(map(int, colorCodes.keys()))):
    if(colorCodes[key]!=oldVal):
      oldVal=retVal[key]=colorCodes[key]
  return retVal
      

def updateCacheAndFetch():
  perDayCollection.drop()
  res = collection.find()
  retVal=[]
  for item in res:
    retVal.append({"address": "","location": item["place_location"]["location"]["coordinates"], "start": "", "end": "", "timeDifference": 0, "loggedDate": str(date.today())})
  save_to_db(retVal,perDayCollection) 
  return retVal
def getSpatioTemporalMatch(placesVisited, radius, timeSpan):
  '''
    Returns list of all location objects that fall within the distance range and timespan \n
    from the infected locations(which are collected from db)
  '''
  spatioTemporalMatch = {}
  for place in placesVisited:
    address = place["place_location"]["address"]
    #Find all neighbouring places
    spatioMatchLocations = get_neighbouring_places(
        place["place_location"]["location"], radius)
    #Add a temporal filter
    temporalMatchList = filterTemporalMatches(
        spatioMatchLocations, place["duration"], timeSpan)

    if(len(temporalMatchList) > 0):
      if(address in spatioTemporalMatch):
        # Update the list if this place is already added
        spatioTemporalMatch[address] += temporalMatchList
      else:
        spatioTemporalMatch[address] = temporalMatchList
  return spatioTemporalMatch


def filterTemporalMatches(spatioMatchLocations, infectedTime, timeSpan):
  '''
      if there is atlease one location that matches temporally, 
      we add it in the spatioTemporalMatch list alond with the infected location's address
  '''
  matchList = []
  for matchLocation in spatioMatchLocations:
    overlap = getTimeOverlap(infectedTime, matchLocation["duration"])
    if(0 <= overlap <= timeSpan):
      matchLocation["timeDifference"] = round(overlap, 2)
      matchList.append(matchLocation)
  return matchList


def get_neighbouring_places(location, radius):
  """
  Given a loation and radius, 
  then this method returns a cursor of all the location objects that fall within that radius picked up from the database
  """
  res = collection.find(
      {
          "location":
          {"$near":
           {
               "$geometry": location,
               "$minDistance": 0,
               "$maxDistance": radius
           }
           }
      }
  )

  return res

def get_geometry_from_erics(fips):
  geo_id = "0500000US"+fips
  return list(ericsCollection.find({"properties.GEO_ID":geo_id},{ "_id": 0,"geometry.coordinates":1})[0]['geometry']['coordinates'][0])

def get_county_matches(places):
  county_dict={}
  for place in places:
    lat,lon = place['place_location']['lat'],place['place_location']['lon']
    if(not isPointInCounty(lat,lon,county_dict, get_geometry_from_erics)):
      county_fips = getCountyFromPoint(lat,lon)
      county_dict[county_fips] = list(countyCollection.find({"GEO_ID":county_fips},{ "_id": 0,"GEO_ID" : 1,"NAME":1,"confirmed_cases":1}))
  countyList=[]
  for value in county_dict.values():
    countyList+=value
  lastVistedDate = getDaysSinceTimeLineEpoch(places[-1]['duration']['endTimestampMs'])
  colorCodes = get_quantile([get_latest_cases_count(county,lastVistedDate) for county in countyList])
  return {"colorCodes" : colorCodes,"collection" : countyList}


def filterPlacesStayedLongerThan(places, time):
  placeList = []
  for place in places:
    if int(place['duration']['endTimestampMs']) - int(place['duration']['startTimestampMs']) > time:
      place['risk'] = getRiskScore(place)
      placeList.append(place)
  return placeList


def test():
  countyList = list(countyCollection.find({},{ "_id": 0,"GEO_ID" : 1,"NAME":1,"confirmed_cases":1, "deaths":1}))
  caseCountList = [get_latest_cases_count(county) for county in countyList]
  colorCodes = get_quantile(caseCountList)



if __name__ == "__main__":
  get_geometry_from_erics("01009")

 
 