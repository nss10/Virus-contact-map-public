from pymongo import MongoClient, GEOSPHERE
from timeline_object import timelineObject
import os

def get_activity_segments(path):
    to = timelineObject(path)
    asList = to.getActivitySegments()
    return asList

def get_place_visits(path):
    to = timelineObject(path)
    pvList = to.getPlaceVisits()
    return pvList

client = MongoClient('localhost', 27017)
db = client["testdb"]
collection = db["placesVisited"]

paths = []

for dirname, _, filenames in os.walk("./data"):
    for filename in filenames:
        pvList = get_place_visits(os.path.join(dirname, filename))
        for pv in pvList:
            collection.insert(pv)

collection.create_index([("location", GEOSPHERE)])