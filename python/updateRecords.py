from preprocess import getConfirmed, getDeaths, getStrainData
from datetime import datetime as dt
from mdb import get_last_updated_date_in_db, add_new_records

def format_and_insert(data_frame, category):
    for _,row in data_frame.iterrows():
        formatted_data = [{"daysElapsed" : d + (last_updated_index-2),"count" : c} for d,c in zip(range(len(date_series)), row[last_updated_index+1:-1])]
        add_new_records(row['CODE'], category, formatted_data)


#Try to keep a value in the server storing the last updated date, update the last
last_updated_date = get_last_updated_date_in_db("cases")
print(last_updated_date)
print("Gettting number of cases in each county")
confirmed_df = getConfirmed()
print("Gettting number of deaths in each county")
deaths_df = getDeaths()


columns = confirmed_df.columns.tolist()
last_updated_index = columns.index(last_updated_date)
date_series = columns[last_updated_index+1:-1]


format_and_insert(confirmed_df, "confirmed_cases")
format_and_insert(deaths_df, "deaths")


