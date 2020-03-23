from pymongo import MongoClient, GEOSPHERE
from timeline_object import timelineObject

def get_activity_segments():
    to = timelineObject('./data/2020_FEBRUARY.json')
    asList = to.getActivitySegments()
    return asList

def get_place_visits():
    to = timelineObject('./data/2020_FEBRUARY.json')
    pvList = to.getPlaceVisits()
    return pvList

client = MongoClient('localhost', 27017)
db = client["testdb"]
collection = db["placesVisited"]

pvList = get_place_visits()

for pv in pvList:
    collection.insert(pv)

collection.create_index([("location", GEOSPHERE)])