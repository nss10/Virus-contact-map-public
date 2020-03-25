from pymongo import MongoClient
from helper import getTimeOverlap

client = MongoClient('localhost', 27017)
db = client["testdb"]
collection = db["placesVisited"]



def getSpatioTemporalMatch(placesVisited,radius,timeSpan):
  '''
    Returns list of all location objects that fall within the distance range and timespan \n
    from the infected locations(which are collected from db)
  '''
  spatioTemporalMatch = []
  i=0
  for place in placesVisited:
    
    spatioMatchLocations = get_neighbouring_places(place["place_location"]["location"], radius)
    
    matchList =[]
    for matchLocation in spatioMatchLocations:
      overlap = (getTimeOverlap(place["duration"], matchLocation["duration"]))
      if(0 <= overlap <= timeSpan):
        matchLocation["timeDifference"] = round(overlap,2)
        matchList.append(matchLocation)
    
    '''
      if there is atlease one location that matches temporally, 
      we add it in the spatioTemporalMatch list alond with the infected location's address
     '''
    if(len(matchList)>0):
      spatioTemporalMatch.append({place["place_location"]["address"]:matchList}) 

  return spatioTemporalMatch


def get_neighbouring_places(location,radius):
  """
  Given a loation and radius, 
  then this method returns a cursor of all the location objects that fall within that radius picked up from the database
  """
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