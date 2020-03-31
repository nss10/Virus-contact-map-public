import pandas as pd
import numpy as np
import uuid
import random
from datetime import datetime
import time
import json

# Data source: https://data.openaddresses.io/runs/807493/us/ny/city_of_new_york.zip

df = pd.read_csv('./data/city_of_new_york/us/ny/city_of_new_york.csv')

df = df[['LON', 'LAT', 'NUMBER', 'STREET', 'CITY', 'DISTRICT', 'POSTCODE']]
df = df.replace(np.nan, '', regex=True)
df = df.dropna()
df['CITY'] = 'New York'
df['DISTRICT'] = 'NY'
df['COUNTRY'] = 'USA'
df['ADDRESS'] = df.apply(lambda row: f"{row.NUMBER} {row.STREET}\n {row.CITY}, {row.DISTRICT} {int(row.POSTCODE)} \n {row.COUNTRY}", axis=1)
df['NAME'] = df.apply(lambda row: f"{row.NUMBER} {row.STREET}", axis=1)

# How many?
N = 40
L = len(df)
for i in range(0,N):
    """
        generate a random id
        select between 65 to 75 places for the month
        create json
        save as id.json
    """
    res = {}
    res["timelineObjects"] = []
    id = str(uuid.uuid4())
    C = random.randrange(65, 75)
    for j in range(0, C):
        # get a random index from df
        row = df.sample()
        place_visit = {}
        place_visit["placeVisit"] = {}
        place_visit["placeVisit"]["location"] = {}
        place_visit["placeVisit"]["location"]["latitudeE7"]= int(float(row.LAT) * 1e7)
        place_visit["placeVisit"]["location"]["longitudeE7"] = int(float(row.LON) * 1e7)
        place_visit["placeVisit"]["location"]["placeId"] = str(uuid.uuid4())

        addr = str(row.ADDRESS).replace('\nName: ADDRESS, dtype: object', '').split('    ')[1]
        name = str(row.NAME).replace('\nName: NAME, dtype: object', '').split('    ')[1]

        place_visit["placeVisit"]["location"]["address"]= addr
        place_visit["placeVisit"]["location"]["name"]= name
        place_visit["placeVisit"]["location"]["sourceInfo"] = {}
        place_visit["placeVisit"]["location"]["sourceInfo"]["deviceTag"] = ''.join(["{}".format(random.randint(0, 9)) for num in range(0, 10)])
        place_visit["placeVisit"]["location"]["locationConfidence"] = random.uniform(60.0,99.0)
        place_visit["placeVisit"]["duration"] = {}

        # datetime(year, month, day, hour, minute, second, microsecond)
        day = random.randint(1, 31)
        hour = random.randint(0, 22) # don't want to calculate spillover etc.
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        microsecond = random.randint(0, 1000000)

        start = datetime(2020, 3, day, hour, minute, second, microsecond)
        diff = 23 - hour
        end = datetime(2020, 3, day, hour + random.randint(1, diff), minute, second, microsecond) # At least an hour

        place_visit["placeVisit"]["duration"]["startTimestampMs"] = str(int(time.mktime(start.timetuple())))
        place_visit["placeVisit"]["duration"]["endTimestampMs"] = str(int(time.mktime(end.timetuple())))
        place_visit["placeVisit"]["placeConfidence"] = "HIGH_CONFIDENCE"
        place_visit["placeVisit"]["centerLatE7"] = int(float(row.LAT) * 1e7)
        place_visit["placeVisit"]["centerLngE7"] = int(float(row.LON) * 1e7)
        place_visit["placeVisit"]["visitConfidence"] = random.randint(90, 99)
        place_visit["placeVisit"]["editConfirmationStatus"] = "NOT_CONFIRMED"
        res["timelineObjects"].append(place_visit)

        activity_segment = {}
        activity_segment["activitySegment"] = {}

        activity_segment["activitySegment"]["startLocation"] = {}
        row1 = df.sample()
        activity_segment["activitySegment"]["startLocation"]["latitudeE7"] = int(float(row1.LAT) * 1e7)
        activity_segment["activitySegment"]["startLocation"]["longitudeE7"] = int(float(row1.LON) * 1e7)

        activity_segment["activitySegment"]["endLocation"] = {}
        row2 = df.sample()
        activity_segment["activitySegment"]["endLocation"]["latitudeE7"] = int(float(row2.LAT) * 1e7)
        activity_segment["activitySegment"]["endLocation"]["longitudeE7"] = int(float(row2.LON) * 1e7)

        activity_segment["activitySegment"]["duration"] = {}
        activity_segment["activitySegment"]["duration"]["startTimestampMs"] = str(int(time.mktime(start.timetuple())))
        activity_segment["activitySegment"]["duration"]["endTimestampMs"] = str(int(time.mktime(end.timetuple())))
        activity_segment["activitySegment"]["distance"] = random.randint(1000, 50000)
        activity_segment["activitySegment"]["activityType"] = "IN_PASSENGER_VEHICLE"
        activity_segment["activitySegment"]["confidence"] = "HIGH"

        res["timelineObjects"].append(activity_segment)

    # Save json
    with open(f'./generated/{id}_genareted_MARCH_2020.json', 'w') as fp:
        json.dump(res, fp, indent=4)

