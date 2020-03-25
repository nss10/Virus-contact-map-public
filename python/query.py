from pymongo import MongoClient
from helper import getTimeOverlap

client = MongoClient('localhost', 27017)
db = client["testdb"]
collection = db["placesVisited"]

def getSpatioTemporalMatch(placesVisited,radius):
  spatioTemporalMatch = []
  i=0
  for place in placesVisited:
    spatioMatchLocations = get_neighbouring_places(place["place_location"]["location"], radius)
    placeId = place["place_location"]["address"]
    matchList =[]
    for matchLocation in spatioMatchLocations:
      overlap = (getTimeOverlap(place["duration"], matchLocation["duration"]))
      if(0 <= overlap <= 5):
        matchLocation["timeDifference"] = round(overlap,2)
        matchLocation["temp"] = i
        i+=1
        matchList.append(matchLocation)
    if(len(matchList)>0):
      spatioTemporalMatch.append({placeId:matchList}) 
    
  return spatioTemporalMatch


def get_neighbouring_places(location,radius):
  res = collection.find(
    {
      "location":
        { "$near" :
            {
              "$geometry": location,
              "$minDistance": 0,
              "$maxDistance": radius
            }
        }
    }
  )

  return res