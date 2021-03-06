import pandas as pd
import io
import requests
import os
import sys
import json
import logging
from datetime import datetime
from helper import getDiffDaysSinceDataEpoch
from mdb import add_cases_data_to_collection

logging.basicConfig(level=logging.DEBUG, filename='./data-preprocess.log', format='%(asctime)s - [%(levelname)s] - %(message)s')

def formatUsaFactsData(url):
    logging.debug(url)
    try:
        s = requests.get(url).content
        df = pd.read_csv(io.StringIO(s.decode('utf-8')))
        df['CODE'] = df.apply(lambda row: f"{row.StateFIPS:02d}{str(row.countyFIPS)[len(str(row.StateFIPS)):]}", axis=1)
        return df
    except:
        logging.error("Error collected data from "+url)
        return None

def getConfirmed():
    url = "https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv"
    return formatUsaFactsData(url)

def getDeaths():
    url = "https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv"
    return formatUsaFactsData(url)

def getCountyCooords():
    file_url = './data/county_coords.csv'
    if not os.path.exists(file_url):
        logging.error("Missing CountyCoords data. No such file exists - "+file_url)
        return None
    df = pd.read_csv(file_url)
    df['GEO_ID'] = df.apply(lambda row : str(row.GEO_ID)[:-5].zfill(5), axis=1)
    df =df.drop_duplicates(subset=['GEO_ID'])
    df = df.drop(['NAME'],axis=1)
    return df.iloc[:,[1,2,3]]

def getStrainData():
    url = 'https://raw.githubusercontent.com/gagnonlab/ncov-data/master/gagnon_data.csv'
    logging.debug(url)
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df['date'] = [getDiffDaysSinceDataEpoch(datetime.strptime(date,'%Y-%m-%d')) for date in df['date']]
    fips_set = set(df['countyFIPS'].dropna().astype(int))
    county_dict = {}
    for county in fips_set:
        county_dict[county] = json.loads(df[df['countyFIPS'] == county] \
                                .drop(columns=['countyFIPS']) \
                                .rename(columns={'-': 'Other','date':'DE'}) \
                                .to_json(orient="records"))
    return county_dict

def getMobilityData():   
    url = 'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
    logging.debug(url)
    try:
        s = requests.get(url).content
        data = pd.read_csv(io.StringIO(s.decode('utf-8')))
        data['date'] = [getDiffDaysSinceDataEpoch(datetime.strptime(date,'%Y-%m-%d')) for date in data['date']]
        # data = data[data['sub_region_1'] == 'Illinois'] \ #replace prev line with this when broadeing the filter 
        data = data[data['country_region_code'] == 'US']  \
            .dropna(subset=['census_fips_code'], how='all') \
            .drop(columns=['country_region_code', 'country_region', 'sub_region_1', 'sub_region_2','metro_area', 'iso_3166_2_code']) \
            .astype({
                                'date' : 'int64',
                                'retail_and_recreation_percent_change_from_baseline': 'Int64',
                                'grocery_and_pharmacy_percent_change_from_baseline': 'Int64',
                                'parks_percent_change_from_baseline': 'Int64',
                                'transit_stations_percent_change_from_baseline': 'Int64',
                                'workplaces_percent_change_from_baseline': 'Int64',
                                'residential_percent_change_from_baseline': 'Int64'
                        }) \
            .rename(columns=
                        {
                                'date' : 'daysElapsed',
                                'retail_and_recreation_percent_change_from_baseline': 'retail_and_recreation',
                                'grocery_and_pharmacy_percent_change_from_baseline': 'grocery_and_pharmacy',
                                'parks_percent_change_from_baseline': 'parks',
                                'transit_stations_percent_change_from_baseline': 'transit_stations',
                                'workplaces_percent_change_from_baseline': 'workplaces',
                                'residential_percent_change_from_baseline': 'residential'
                        }) 
        fips_set = set(data['census_fips_code'])
        logging.debug(len(fips_set))
        county_dict = {}
        for county in fips_set:
            county_dict[str(int(county)).zfill(5)] = json.loads(data[data['census_fips_code']==county] \
                                                                    .drop(columns=['census_fips_code'])                                                                     
                                                                    .to_json(orient="records"))
        return county_dict
    except : 
        logging.debug("Error collecting google mob data")
        return None

def getBasicCountyInfo(county):
    c = {"GEO_ID" : county['properties']['GEO_ID'][-5:],"NAME": county['properties']['NAME']}
    
    #Changed in 2015, but not updated in Erics dataset
    if c['GEO_ID']=="46113":
        c = {"GEO_ID" : '46102',"NAME": 'Oglala Lakota'}
    #Changed by Census, but not updated in Erics dataset
    if c['GEO_ID']=="02270":
        c = {"GEO_ID" : '02158',"NAME": 'Kusilvak'}
    #Changed in 2013, but not updated in Erics dataset
    elif c['GEO_ID']=="51515":
        c['GEO_ID']="51019"
    c['geometry'] = county['geometry']
    return c

def countyData(path):
    output_data = {}
    output_data['counties'] = []

    logging.debug("Gettting number of cases in each county")
    confirmed_df = getConfirmed()
    logging.debug("Gettting number of deaths in each county")
    deaths_df = getDeaths()
    logging.debug("Gettting LatLon for each county")
    coords_df = getCountyCooords()
    logging.debug("Getting Strain data from repo - ")
    strain_data = getStrainData()
    logging.debug("Getting Mobility data from repo - ")
    mobility_data = getMobilityData()

    columns = confirmed_df.columns.tolist()
    date_series = columns[4:-1]
    if not os.path.isfile(path):
        logging.debug("Fetching geolocation data")
        url = "https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_20m.json"
        data = requests.get(url).json()
        with open(path, 'w') as fp:
            json.dump(data, fp, indent=4)

    with open(path, encoding='ISO-8859-1') as f:
        data = json.load(f)
        counties = data['features']
        logging.debug("Combining geolocation data with cases and deaths")
        for county in counties:
            c = getBasicCountyInfo(county)
            if c['GEO_ID'].startswith("72"):
                continue
            c['coords'] = coords_df[coords_df['GEO_ID']==c['GEO_ID']].iloc[[0],[2,1]].values.flatten().tolist() if coords_df is not None else []
            confirmed_series = confirmed_df[confirmed_df['CODE']==c['GEO_ID']].values.tolist() if confirmed_df is not None else []
            if len(confirmed_series)> 0:
                ccases = confirmed_series[0][4:-1] if confirmed_df is not None else []
                c['confirmed_cases'] = [{'daysElapsed':(d+1), 'count':c} for d,c in zip(range(len(date_series)),ccases)]
                deaths_series = deaths_df[deaths_df['CODE']==c['GEO_ID']].values.tolist() if deaths_df is not None else []
                dcases = deaths_series[0][4:-1] if deaths_df is not None else []
                c['deaths'] = [{'daysElapsed':(d+1), 'count':c} for d,c in zip(range(len(date_series)),dcases)]
                c['strain_data'] = strain_data[int(c['GEO_ID'])] if (strain_data and int(c['GEO_ID']) in strain_data) else []
                c['mobility_data'] = mobility_data[c['GEO_ID']] if (mobility_data and c['GEO_ID'] in  mobility_data) else []
            else:
                c['confirmed_cases'] = [{'daysElapsed': (d+1), 'count': 0} for d in range(len(date_series))]
                c['deaths'] = [{'daysElapsed': (d+1), 'count': 0} for d in range(len(date_series))]
            output_data['counties'].append(c)

    logging.debug("Adding collection to database")
    add_cases_data_to_collection(output_data['counties'])
    
    # # Save json
    # with open(f'./generated/{datetime.date(datetime.now())}.json', 'w') as fp:
    #     json.dump(output_data, fp, indent=4)

def main():
    if not os.path.exists('./data'):
        os.makedirs('./data')

    if not os.path.exists('./generated'):
        os.makedirs('./generated')
    countyData("./data/gz_2010_us_050_00_20m.json")
    
if __name__ == "__main__":
    main()