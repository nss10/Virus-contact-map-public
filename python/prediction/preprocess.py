import pandas as pd
import math
import csv

pd.set_option('display.max_rows', None, 'display.max_columns', None)

df_train = pd.read_csv('./data/novel-corona-virus-2019-dataset/covid_19_data.csv',delimiter=',')
df_train = df_train.fillna("NULL")
df_train['ObservationDate'] = pd.to_datetime(df_train['ObservationDate'])
df_train = df_train[['Province/State', 'Country/Region','ObservationDate', 'Confirmed', 'Deaths']]
df_train_by_place = df_train.groupby(['Country/Region','Province/State'])

places = df_train_by_place.groups.keys()

header_list = []
metric_list = ['Confirmed','Deaths']

country = {}
max_len = 0
gdate_list = None

for place in places:
    (c,s) = place
    if c in country:
        place_df = df_train_by_place.get_group(place)
        state = {}
        state[s] = place_df
        country[c].append(state)
    else:
        country[c] = []
        place_df = df_train_by_place.get_group(place)
        state = {}
        state[s] = place_df
        country[c].append(state)

for c, d in country.items():
    if len(d)==1:
        fname = f'./place_data/{c}.csv'
        header_list.append(c)
        if 'NULL' in d[0]:
            place_df = d[0]['NULL']
            place_df.to_csv(fname, index=False)
            l = len(place_df)
            if max_len < l:
                max_len = l
        else:
            place_df = d[0]['Diamond Princess']
            place_df.to_csv(fname, index=False)
            l = len(place_df)
            if max_len < l:
                max_len = l
    else:
        country_s_conf = None
        country_s_fata = None
        country_name = [c for i in range(0,max_len)]
        state_name = ['NULL' for i in range(0,max_len)]
        date_list = None
        for s in d:
            for k,v in s.items():
                fname = f'./place_data/{c}_{k}.csv'
                header_list.append(f'{c}_{k}')
                place_df = v
                place_df.to_csv(fname, index=False)
                l = len(place_df)
                if max_len < l:
                    max_len = l

                if date_list == None:
                    date_list = place_df['ObservationDate'].tolist()
                if country_s_conf == None:
                    country_s_conf = place_df['Confirmed'].tolist()
                    pass
                else:
                    country_s_conf = [x + y for x, y in zip(country_s_conf, place_df['Confirmed'].tolist())]
                    pass

                if country_s_fata == None:
                    country_s_fata = place_df['Deaths'].tolist()
                else:
                    country_s_fata = [x + y for x, y in zip(country_s_fata, place_df['Deaths'].tolist())]

        country_df = pd.DataFrame({'Province/State':state_name,
                      'Country/Region': country_name,
                      'ObservationDate': date_list,
                      'Confirmed': country_s_conf,
                      'Deaths': country_s_fata})
        country_df['ObservationDate'] = pd.to_datetime(country_df['ObservationDate'])
        fname = f'./place_data/{c}.csv'
        header_list.append(c)
        country_df.to_csv(fname, index=False)
        gdate_list = date_list

for metric in metric_list:
    outfile = f'./processed_stats/{metric}.csv'
    with open(outfile, mode='w') as g_file:
        csv_writer = csv.writer(g_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_header = ['id'] + [str(i) for i in range(0, max_len)]
        csv_writer.writerow(csv_header)

        for h in header_list:
            fname = f'./place_data/{h}.csv'
            df = pd.read_csv(fname,delimiter=',')
            df = df[[metric]]
            l = len(df)
            diff = max_len - l
            append_list = []
            for i in range(0, diff):
                d = {
                    metric: None
                }
                append_list.append(d)

            append_df = pd.DataFrame(append_list)
            df = df.append(append_df, ignore_index=True)
            series = [h] + df[metric].tolist()
            csv_writer.writerow(series)

metadata_df = pd.DataFrame(
    {
        'ObservationDate' : gdate_list,
        'Index' : [str(i) for i in range(0, max_len)]
    }
)

fname = f'./processed_stats/metadata.csv'
metadata_df.to_csv(fname, index=False)