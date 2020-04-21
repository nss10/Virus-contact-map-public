import pandas as pd
import io
import requests
import os
import json
from datetime import datetime
from mdb import add_timeline_data_to_collection

"""
Data for following states are missing in usa facts (all state id 72 - PUERTO RICO - which is fine!)
0500000US72013, 0500000US72019, 0500000US72025, 0500000US72031, 0500000US72045, 0500000US72054, 0500000US72061, 
0500000US72069, 0500000US72083, 0500000US72093, 0500000US72105, 0500000US72115, 0500000US72129, 0500000US72135, 
0500000US72145, 0500000US46113, 0500000US72027, 0500000US72035, 0500000US72041, 0500000US72043, 0500000US72053, 
0500000US72055, 0500000US72059, 0500000US72067, 0500000US72073, 0500000US72005, 0500000US72079, 0500000US72081, 
0500000US72089, 0500000US72095, 0500000US72101, 0500000US72103, 0500000US72109, 0500000US72117, 0500000US72119, 
0500000US72125, 0500000US72131, 0500000US72137, 0500000US72143, 0500000US72075, 0500000US72147, 0500000US72151, 
0500000US72153, 0500000US72149, 0500000US51515, 0500000US72017, 0500000US72021, 0500000US72029, 0500000US72039, 
0500000US72051, 0500000US72063, 0500000US72077, 0500000US72085, 0500000US72099, 0500000US72111, 0500000US72123, 
0500000US72139, 0500000US72001, 0500000US72007, 0500000US72011, 0500000US72023, 0500000US72033, 0500000US72037, 
0500000US72047, 0500000US72049, 0500000US72057, 0500000US72065, 0500000US72087, 0500000US72091, 0500000US72097, 
0500000US72107, 0500000US72113, 0500000US72121, 0500000US72127, 0500000US72133, 0500000US72141, 0500000US72071, 
0500000US72003, 0500000US72009, 0500000US72015
"""

def getConfirmed():
    url = "https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv"
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df['CODE'] = df.apply(lambda row: f"0500000US{row.stateFIPS:02d}{str(row.countyFIPS)[len(str(row.stateFIPS)):]}", axis=1)
    return df

def getDeaths():
    url = "https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv"
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df['CODE'] = df.apply(lambda row: f"0500000US{row.stateFIPS:02d}{str(row.countyFIPS)[len(str(row.stateFIPS)):]}", axis=1)
    return df

def countyData(path):
    output_data = {}
    output_data['counties'] = []

    confirmed_df = getConfirmed()
    deaths_df = getDeaths()

    columns = confirmed_df.columns.tolist()
    date_series = columns[4:-2]
    if not os.path.isfile(path):
        url = "https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_20m.json"
        data = requests.get(url).json()
        with open(path, 'w') as fp:
            json.dump(data, fp, indent=4)

    with open(path, encoding='ISO-8859-1') as f:
        data = json.load(f)
        counties = data['features']
        for county in counties:
            c = county['properties']
            c['geometry'] = county['geometry']

            confirmed_series = confirmed_df[confirmed_df['CODE']==c['GEO_ID']].values.tolist()
            if len(confirmed_series)> 0:
                ccases = confirmed_series[0][4:-2]
                c['confirmed_cases'] = [{'daysElapsed':(d+1), 'count':c} for d,c in zip(range(len(date_series)),ccases)]
                deaths_series = deaths_df[deaths_df['CODE']==c['GEO_ID']].values.tolist()
                dcases = deaths_series[0][4:-2]
                c['deaths'] = [{'daysElapsed':(d+1), 'count':c} for d,c in zip(range(len(date_series)),dcases)]
            else:
                print(f'{c["GEO_ID"]}    {confirmed_series}')
                c['confirmed_cases'] = [{'daysElapsed': (d+1), 'count': 0} for d in range(len(date_series))]
                c['deaths'] = [{'daysElapsed': (d+1), 'count': 0} for d in range(len(date_series))]
            c['GEO_ID'] = c['GEO_ID'][-5:]
            output_data['counties'].append(c)
            # Modify here to insert each c into mongodb
    add_timeline_data_to_collection(output_data['counties'])
    # Save json
    with open(f'./generated/{datetime.now()}.json', 'w') as fp:
        json.dump(output_data, fp, indent=4)




def main():
    if not os.path.exists('./data'):
        os.makedirs('./data')

    if not os.path.exists('./generated'):
        os.makedirs('./generated')
    countyData("./data/gz_2010_us_050_00_20m.json")

if __name__ == "__main__":
    main()