from pymongo import MongoClient
from helper import getTimeOverlap
# LocalDb
# client = MongoClient('localhost', 27017)
# db = client["testdb"]
# collection = db["placesVisited"]

# RemoteDb
client = MongoClient('173.28.146.185', 27017)
db = client["covid19"]
collection = db["infectedPlaces"]


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