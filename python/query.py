from pymongo import MongoClient
from datetime import datetime

client = MongoClient('localhost', 27017)
db = client["testdb"]
collection = db["placesVisited"]

start_time = datetime(2020, 2, 5, 0, 0, 0)
end_time = datetime(2020, 2, 14, 5, 0, 0)
res = collection.find(
   {
       "$and": [
           {"location":
               { "$near" :
                  {
                    "$geometry": { "type": "Point",  "coordinates": [ -89.21, 37.72 ] },
                    "$minDistance": 1,
                    "$maxDistance": 500
                  }
               }
           },
           {
               "duration.start": { "$gte":start_time, "$lt": end_time }
           }
       ]
   }
)

for r in res:
    print(r)