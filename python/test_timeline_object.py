import unittest
from timeline_object import timelineObject

class TestSum(unittest.TestCase):

    def test_get_activity_segments(self):
        self.to = timelineObject('./data/2020_FEBRUARY.json')
        asList = self.to.getActivitySegments()
        self.assertEqual(len(asList), 146, "Should be 146")

    def test_get_place_visits(self):
        self.to = timelineObject('./data/2020_FEBRUARY.json')
        pvList = self.to.getPlaceVisits()
        self.assertEqual(len(pvList), 239, "Should be 239")
        for pv in pvList:
            print(pv)
