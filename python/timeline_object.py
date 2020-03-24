import json
from datetime import datetime


class timelineObject:
    """
    Utility class that takes a json file path and returns list of activity segments or place visits
    """
    def __init__(self, path_to_json):
        """
        For now takes a path to a json file
        should implement for a JSON object
        :param path_to_json: path to json file
        """
        self.path = path_to_json
        with open(self.path) as self.json_file:
            self.timeline = json.load(self.json_file)

    def _get_scalar(self, coord):
        """
        Converts coordinate in E7 format to double
        :param coord:
        :return:
        """
        return float(int(coord) / 1e7)

    def _get_time(self, ts):
        """
        Converts time stamp in millisecond to UTC format
        :param ts: timestamp
        :return: UTC time as string
        """
        ts = int(ts) / 1000
        return datetime.utcfromtimestamp(ts)

    def get_lat_lon(self, loc):
        """
        Converts E7 to standard lat, lon, and adds GeoJSON field
        for MongoDB as Point type in 2DSphere format
        :param loc:
        :return:
        """
        res = {}
        res['lat'] = self._get_scalar(loc['latitudeE7'])
        res['lon'] = self._get_scalar(loc['longitudeE7'])
        res['location'] = {"type": "Point", "coordinates": [res['lon'], res['lat']]}
        return res

    def get_duration(self, dur):
        res = {}
        res['start'] = self._get_time(dur['startTimestampMs'])
        res['end'] = self._get_time(dur['endTimestampMs'])
        res['startTimestampMs'] = dur['startTimestampMs']
        res['endTimestampMs'] = dur['endTimestampMs']
        return res

    def get_waypoints(self, wp):
        res = {}
        res['waypoints'] = []
        wps = wp['waypoints']
        for w in wps:
            neww = {}
            neww['lat'] =  self._get_scalar(w['latE7'])
            neww['lon'] =  self._get_scalar(w['lngE7'])
            neww['location'] = {"type": "Point", "coordinates": [neww['lon'], neww['lat']]}
            res['waypoints'].append(neww)
        return res

    def get_simplified_path(self, spath):
        res = {}
        res['points'] = []
        for p in spath['points']:
            newp = {}
            newp['lat'] = self._get_scalar(p['latE7'])
            newp['lon'] = self._get_scalar(p['lngE7'])
            newp['location'] = { "type": "Point", "coordinates": [ newp['lon'], newp['lat'] ] }
            newp['time'] = self._get_time(p['timestampMs'])
            newp['timestampMs'] = p['timestampMs']
            newp['accuracyMeters'] = p['accuracyMeters']
            res['points'].append(newp)
        return res

    def get_simplified_location(self, loc):
        res = {}
        res['lat'] = self._get_scalar(loc['latitudeE7'])
        res['lon'] = self._get_scalar(loc['longitudeE7'])
        res['location'] = {"type": "Point", "coordinates": [res['lon'], res['lat']]}
        res['placeId'] = loc['placeId']
        if 'address' in loc:
            res['address'] = loc['address']
        if 'name' in loc:
            res['name'] = loc['name']
        if 'sourceInfo' in loc:
            res['sourceInfo'] = loc['sourceInfo']
        if 'locationConfidence' in loc:
            res['locationConfidence'] = loc['locationConfidence']
        return res

    def getActivitySegments(self):
        """
        Parses and collects activitySegment objects
        :return: a list of activitySegment objets
        """
        activity_segments = []
        for obj in self.timeline['timelineObjects']:
            if 'activitySegment' in obj:
                a = {}
                if 'startLocation' in obj['activitySegment']:
                    a['startLocation'] = self.get_lat_lon(obj['activitySegment']['startLocation'])
                if 'endLocation' in obj['activitySegment']:
                    a['endLocation'] = self.get_lat_lon(obj['activitySegment']['endLocation'])
                if 'duration' in obj['activitySegment']:
                    a['duration'] = self.get_duration(obj['activitySegment']['duration'])
                if 'distance' in obj['activitySegment']:
                    a['distance'] = obj['activitySegment']['distance']
                if 'activityType' in obj['activitySegment']:
                    a['activityType'] = obj['activitySegment']['activityType']
                if 'confidence' in obj['activitySegment']:
                    a['confidence'] = obj['activitySegment']['confidence']
                if 'waypointPath' in obj['activitySegment']:
                    a['waypointPath'] = self.get_waypoints(obj['activitySegment']['waypointPath'])
                if 'simplifiedRawPath' in obj['activitySegment']:
                    a['simplifiedRawPath'] = self.get_simplified_path(obj['activitySegment']['simplifiedRawPath'])
                activity_segments.append(a)
        return activity_segments

    def getPlaceVisits(self):
        """
        Parses and collects only placeVisit objects
        some placeVisit can have childVisits - which seems to be
        a list of placeVisit like objects. For now I am unfolding them
        and bringing them up into the parent list (Need to decide on this later)
        :return: a list of place visit objects in the JSON
        """
        visits = []
        for obj in self.timeline['timelineObjects']:
            if 'placeVisit' in obj:
                v = {}
                if 'location' in obj['placeVisit']:
                    v['place_location'] = self.get_simplified_location(obj['placeVisit']['location'])
                if 'duration' in obj['placeVisit']:
                    v['duration'] = self.get_duration(obj['placeVisit']['duration'])
                if 'placeConfidence' in obj['placeVisit']:
                    v['placeConfidence'] = obj['placeVisit']['placeConfidence']
                if 'centerLatE7' in obj['placeVisit']:
                    v['centerLat'] = self._get_scalar(obj['placeVisit']['centerLatE7'])
                if 'centerLngE7' in obj['placeVisit']:
                    v['centerLon'] = self._get_scalar(obj['placeVisit']['centerLngE7'])
                if 'centerLatE7' in obj['placeVisit'] and 'centerLngE7' in obj['placeVisit']:
                    v['location'] = {"type": "Point", "coordinates": [v['centerLon'], v['centerLat']]}
                if 'visitConfidence' in obj['placeVisit']:
                    v['visitConfidence'] = obj['placeVisit']['visitConfidence']
                if 'editConfirmationStatus' in obj['placeVisit']:
                    v['editConfirmationStatus'] = obj['placeVisit']['editConfirmationStatus']
                if 'childVisits' in obj['placeVisit']:
                    child_list = obj['placeVisit']['childVisits']
                    for child in child_list:
                        c = {}
                        if 'location' in child:
                            c['place_location'] = self.get_simplified_location(child['location'])
                        if 'duration' in child:
                            c['duration'] = self.get_duration(child['duration'])
                        if 'placeConfidence' in child:
                            c['placeConfidence'] = child['placeConfidence']
                        if 'centerLatE7' in child:
                            c['centerLat'] = self._get_scalar(child['centerLatE7'])
                        if 'centerLngE7' in child:
                            c['centerLon'] = self._get_scalar(child['centerLngE7'])
                        if 'centerLatE7' in child and 'centerLngE7' in child:
                            c['location'] = {"type": "Point", "coordinates": [c['centerLon'], c['centerLat']]}
                        if 'visitConfidence' in child:
                            c['visitConfidence'] = child['visitConfidence']
                        if 'editConfirmationStatus' in child:
                            c['editConfirmationStatus'] = child['editConfirmationStatus']
                        visits.append(c)
                visits.append(v)
        return visits
