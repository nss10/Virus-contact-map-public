from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client["testdb"]
collection = db["placesVisited"]


res = collection.find(
   {
     "location":
       { "$near" :
          {
            "$geometry": { "type": "Point",  "coordinates": [ -89.21, 37.72 ] },
            "$minDistance": 1,
            "$maxDistance": 500
          }
       }
   }
)

for r in res:
    print(r)