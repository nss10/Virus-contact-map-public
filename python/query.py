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


def getCountyLocations():
  retCollection = list(countyCollection.find({},{ "_id": 0,"GEO_ID" : 1,"NAME":1,"confirmed_cases":1, "deaths":1}))
  case_count_set=set()
  for item in retCollection:
    caseList=[]
    deathList=[]
    for case in item['confirmed_cases']:
      if(case['count']>0):
        caseList.append(case)
        case_count_set.add(case['count'])
    for case in item['deaths']:
      if(case['count']!=0):
        deathList.append(case)
    item['confirmed_cases']=caseList
    item['deaths']=deathList
  colorList = get_quantile(list(case_count_set))
  colorCodes = {}
  for item in colorList:
    colorCodes[item[0]] = item[1]
    
  return {"colorCodes" : colorCodes,"collection" : retCollection}


def getAllInfectedLocations():
  res =  list(perDayCollection.find({},{ "_id": 0}))
  if(len(res) > 0 and res[0]['loggedDate']==str(date.today())):
    print("Returning data from Cache")
    return res
  return updateCacheAndFetch()


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


def get_county_matches(places):
  county_dict={}
  for place in places:
    lat,lon = place['place_location']['lat'],place['place_location']['lon']

    county_fips = getCountyFromPoint(lat,lon)
    if(county_fips not in county_dict):
      county_dict[county_fips] = list(countyCollection.find({"GEO_ID":county_fips},{ "_id": 0,"GEO_ID" : 1,"NAME":1,"confirmed_cases":1, "deaths":1}))
    countyList = list(county_dict.values())
    


def test():
  print(list(countyCollection.find({},{ "_id": 0,"GEO_ID" : 1,"NAME":1,"confirmed_cases":1, "deaths":1})))



if __name__ == "__main__":
  test()

 
 