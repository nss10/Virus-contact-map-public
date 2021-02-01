import pandas as pd
import io
import requests
import os
import sys
import json
from datetime import datetime
from helper import getDiffDaysSinceDataEpoch
from mdb import add_cases_data_to_collection


def getConfirmed():
    url = "https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv"
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df['CODE'] = df.apply(lambda row: f"{row.stateFIPS:02d}{str(row.countyFIPS)[len(str(row.stateFIPS)):]}", axis=1)
    return df

def getDeaths():
    url = "https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv"
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df['CODE'] = df.apply(lambda row: f"{row.stateFIPS:02d}{str(row.countyFIPS)[len(str(row.stateFIPS)):]}", axis=1)
    return df

def countyData(path):
    output_data = {}
    output_data['counties'] = []

    print("Gettting number of cases in each county")
    confirmed_df = getConfirmed()

    print("Gettting number of deaths in each county")
    deaths_df = getDeaths()
    
    
    columns = confirmed_df.columns.tolist()
    date_series = columns[4:-2]
    if not os.path.isfile(path):
        print("Fetching geolocation data")
        url = "https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_20m.json"
        data = requests.get(url).json()
        with open(path, 'w') as fp:
            json.dump(data, fp, indent=4)

    with open(path, encoding='ISO-8859-1') as f:
        data = json.load(f)
        counties = data['features']
        print("Combining geolocation data with cases and deaths")
        for county in counties:
            c = {"GEO_ID" : county['properties']['GEO_ID'][-5:],"NAME": county['properties']['NAME']}
            #Changed in 2015, but not updated in Erics dataset
            if c['GEO_ID']=="46113":
                c = {"GEO_ID" : '46102',"NAME": 'Oglala Lakota'}
            c['geometry'] = county['geometry']

            confirmed_series = confirmed_df[confirmed_df['CODE']==c['GEO_ID']].values.tolist()
            
            if len(confirmed_series)> 0:
                ccases = confirmed_series[0][4:-2]
                c['confirmed_cases'] = [{'daysElapsed':(d+1), 'count':c} for d,c in zip(range(len(date_series)),ccases)]
                deaths_series = deaths_df[deaths_df['CODE']==c['GEO_ID']].values.tolist()
                dcases = deaths_series[0][4:-2]
                c['deaths'] = [{'daysElapsed':(d+1), 'count':c} for d,c in zip(range(len(date_series)),dcases)]
            else:
                c['confirmed_cases'] = [{'daysElapsed': (d+1), 'count': 0} for d in range(len(date_series))]
                c['deaths'] = [{'daysElapsed': (d+1), 'count': 0} for d in range(len(date_series))]
            output_data['counties'].append(c)

    print("Adding collection to database")
    add_cases_data_to_collection(output_data['counties'])
    
    # Save json
    with open(f'./generated/{datetime.date(datetime.now())}.json', 'w') as fp:
        json.dump(output_data, fp, indent=4)

def main():
    if not os.path.exists('./data'):
        os.makedirs('./data')

    if not os.path.exists('./generated'):
        os.makedirs('./generated')
    countyData("./data/gz_2010_us_050_00_20m.json")

if __name__ == "__main__":
    main()
    
   