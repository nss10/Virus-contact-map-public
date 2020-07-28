import pandas as pd
import io
import requests
import os
import json
from datetime import datetime
from helper import getDiffDaysSinceDataEpoch
from mdb import add_cases_data_to_collection


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

    pred_conf, pred_death =  getFutureData()
    
    lastDate = datetime.strptime(confirmed_df.columns[-2],'%m/%d/%y')
    for dateIndex in range(1,len(pred_conf.columns)):
        firstFutureDate = datetime.strptime(pred_conf.columns[dateIndex],'%Y-%m-%d')
        if(lastDate< firstFutureDate):
            pred_conf = pred_conf.drop(columns=pred_conf.columns[1:dateIndex])
            pred_DaysElapsed = getDiffDaysSinceDataEpoch(firstFutureDate)
            break
    
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
            pred_conf_series = pred_conf[pred_conf['fips']==int(c['GEO_ID'][-5:])].values.tolist()
            
            if len(confirmed_series)> 0:
                ccases = confirmed_series[0][4:-2]
                if(len(pred_conf_series)>0):
                    pred_ccases = pred_conf_series[0][1:]
                else:
                    pred_ccases  = [ccases[-1]]*(len(pred_conf.columns)-1)
                c['confirmed_cases'] = [{'daysElapsed':(d+1), 'count':c} for d,c in zip(range(len(date_series)),ccases)]
                c['confirmed_cases'] += [{'daysElapsed':(pred_DaysElapsed+i), 'count':c, 'isPredicted' : True} for i,c in enumerate(pred_ccases)]
                deaths_series = deaths_df[deaths_df['CODE']==c['GEO_ID']].values.tolist()
                pred_death_series = pred_death[pred_death['fips']==int(c['GEO_ID'][-5:])].values.tolist()
                dcases = deaths_series[0][4:-2]
                if(len(pred_death_series)>0):
                    pred_dcases = pred_death_series[0][1:]
                else:
                    pred_dcases  = [dcases[-1]]*(len(pred_death.columns)-1)
                c['deaths'] = [{'daysElapsed':(d+1), 'count':c} for d,c in zip(range(len(date_series)),dcases)]
            else:
                c['confirmed_cases'] = [{'daysElapsed': (d+1), 'count': 0} for d in range(len(date_series))]
                c['deaths'] = [{'daysElapsed': (d+1), 'count': 0} for d in range(len(date_series))]
                c['deaths'] += [{'daysElapsed':(pred_DaysElapsed+i), 'count':c, 'isPredicted' : True} for i,c in enumerate(pred_dcases)]
            c['GEO_ID'] = c['GEO_ID'][-5:]
            output_data['counties'].append(c)
            # Modify here to insert each c into mongodb
    add_cases_data_to_collection(output_data['counties'])
    # Save json
    with open(f'./generated/{datetime.date(datetime.now())}.json', 'w') as fp:
        json.dump(output_data, fp, indent=4)


def getFutureData():
  token= os.environ.get('GIT_AUTH_TOKEN')
  headers = {'Authorization': 'token %s' % token}
  url='https://raw.githubusercontent.com/Wjerry5/uiuc-covid19-prediction-county/master/covid19-prediction-county.csv'
  print(url)
  s = requests.get(url,headers=headers).content
  df = pd.read_csv(io.StringIO(s.decode('utf-8')))
  fips_set = set(df['County_FIPS'].dropna().astype(int))
  date_range = sorted(list(set(df['date'])))
  df_conf = pd.DataFrame(columns=['fips']+date_range)
  df_conf.index=df_conf['fips']
  df_deaths = pd.DataFrame(columns=['fips']+date_range)
  df_deaths.index=df_conf['fips']
  for county in fips_set:
      df1 = df[df['County_FIPS']==county].iloc[:,[1,2,3]]
      df1.index=df1['date']
      dfc1=df1.transpose().iloc[[1],:]
      dfd1=df1.transpose().iloc[[2],:]
      dfc1['fips']=dfd1['fips']=county
      df_conf = df_conf.append(dfc1,sort=False)
      df_deaths = df_deaths.append(dfd1,sort=False)
  df_conf.index=df_conf['fips']
  df_deaths.index=df_deaths['fips']
  return [df_conf,df_deaths]


def main():
    if not os.path.exists('./data'):
        os.makedirs('./data')

    if not os.path.exists('./generated'):
        os.makedirs('./generated')
    countyData("./data/gz_2010_us_050_00_20m.json")

if __name__ == "__main__":
    main()
    
   