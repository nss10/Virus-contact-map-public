import pandas as pd
import numpy as np
import os

files = []
for dirname, _, filenames in os.walk("./data/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"):
    for filename in filenames:
        if filename.endswith(".csv"):
           files.append(os.path.join(dirname, filename))

start_no = 1
df = pd.DataFrame(columns=['SNo', 'ObservationDate', 'Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered'])

for f in files:
    print(f)
    daily_df = pd.read_csv(f)
    columns = daily_df.columns.tolist()
    date = f.split('/')[-1].split('.')[0]

    if 'Province_State' in columns:
        daily_df = daily_df.rename(columns={"Province_State": "Province/State"})

    if 'Country_Region' in columns:
        daily_df = daily_df.rename(columns={"Country_Region": "Country/Region"})

    if 'Last_Update' in columns:
        daily_df = daily_df.rename(columns={"Last_Update": "Last Update"})

    daily_df["ObservationDate"] = date.replace('-', '/')

    daily_df = daily_df[['ObservationDate', 'Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered']]

    daily_df.insert(0, 'SNo', range(start_no, start_no + len(daily_df)))

    start_no = start_no + len(daily_df)

    df = pd.concat([df,daily_df])
    print(date)

df = df.fillna(value={'Confirmed': 0, 'Deaths': 0, 'Recovered': 0})
df.to_csv('./data/covid_19_data.csv', index=False)