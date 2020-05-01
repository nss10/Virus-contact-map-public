import pandas as pd
import numpy as np
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime

def select_area(ncov_df, group="Date", places=None, excluded_places=None,
                start_date=None, end_date=None, date_format="%d%b%Y"):
    """
    Select the records of the palces.
    @ncov_df <pd.DataFrame>: the clean data
    @group <str or None>: group-by the group, or not perform (None)
    @places <list[tuple(<str/None>, <str/None>)]: the list of places
        - if the list is None, all data will be used
        - (str, str): both of country and province are specified
        - (str, None): only country is specified
        - (None, str) or (None, None): Error
    @excluded_places <list[tuple(<str/None>, <str/None>)]: the list of excluded places
        - if the list is None, all data in the "places" will be used
        - (str, str): both of country and province are specified
        - (str, None): only country is specified
        - (None, str) or (None, None): Error
    @start_date <str>: the start date or None
    @end_date <str>: the start date or None
    @date_format <str>: format of @start_date and @end_date
    @return <pd.DataFrame>: index and columns are as same as @ncov_df
    """
    # Select the target records
    df = ncov_df.copy()
    c_series = df["Country"]
    p_series = df["Province"]
    if places is not None:
        df = pd.DataFrame(columns=ncov_df.columns)
        for (c, p) in places:
            if c is None:
                raise Exception("places: Country must be specified!")
            if p is None:
                new_df = ncov_df.loc[c_series == c, :]
            else:
                new_df = ncov_df.loc[(c_series == c) & (p_series == p), :]
            df = pd.concat([df, new_df], axis=0)
    if excluded_places is not None:
        for (c, p) in excluded_places:
            if c is None:
                raise Exception("excluded_places: Country must be specified!")
            if p is None:
                df = df.loc[c_series != c, :]
            else:
                c_df = df.loc[(c_series == c) & (p_series != p), :]
                other_df = df.loc[c_series != c, :]
                df = pd.concat([c_df, other_df], axis=0)
    if group is not None:
        df = df.groupby(group).sum().reset_index()
    # Range of date
    if start_date is not None:
        df = df.loc[df["Date"] >= datetime.strptime(start_date, date_format), :]
    if end_date is not None:
        df = df.loc[df["Date"] <= datetime.strptime(end_date, date_format), :]
    return df


def create_target_df(ncov_df, total_population, places=None,
                     excluded_places=None, start_date=None, date_format="%d%b%Y"):
    """
    Select the records of the palces, calculate the number of susceptible people,
     and calculate the elapsed time [day] from the start date of the target dataframe.
    @ncov_df <pd.DataFrame>: the clean data
    @total_population <int>: total population in the places
    @places <list[tuple(<str/None>, <str/None>)]: the list of places
        - if the list is None, all data will be used
        - (str, str): both of country and province are specified
        - (str, None): only country is specified
        - (None, str) or (None, None): Error
    @excluded_places <list[tuple(<str/None>, <str/None>)]: the list of excluded places
        - if the list is None, all data in the "places" will be used
        - (str, str): both of country and province are specified
        - (str, None): only country is specified
        - (None, str) or (None, None): Error
    @start_date <str>: the start date or None
    @date_format <str>: format of @start_date
    @return <tuple(2 objects)>:
        - 1. start_date <pd.Timestamp>: the start date of the selected records
        - 2. target_df <pd.DataFrame>:
            - column T: elapsed time [min] from the start date of the dataset
            - column Susceptible: the number of patients who are in the palces but not infected/recovered/died
            - column Infected: the number of infected cases
            - column Recovered: the number of recovered cases
            - column Deaths: the number of death cases
    """
    # Select the target records
    df = select_area(ncov_df, places=places, excluded_places=excluded_places, start_date=start_date)
    if start_date is not None:
        df = df.loc[df["Date"] >= datetime.strptime(start_date, date_format), :]
    start_date = df.loc[df.index[0], "Date"]
    # column T
    df["T"] = ((df["Date"] - start_date).dt.total_seconds() / 60).astype(int)
    # coluns except T
    df["Susceptible"] = total_population - df["Infected"] - df["Recovered"] - df["Deaths"]
    response_variables = ["Susceptible", "Infected", "Recovered", "Deaths"]
    # Return
    target_df = df.loc[:, ["T", "Date", *response_variables]]
    return (start_date, target_df)

def load_and_clean(path):
    raw = pd.read_csv(path)
    data_cols = ["Infected", "Deaths", "Recovered"]
    rate_cols = ["Fatal per Confirmed", "Recovered per Confirmed", "Fatal per (Fatal or Recovered)"]
    variable_dict = {"Susceptible": "S", "Infected": "I", "Recovered": "R", "Deaths": "D"}
    ncov_df = raw.rename({"ObservationDate": "Date", "Province/State": "Province"}, axis=1)
    ncov_df["Date"] = pd.to_datetime(ncov_df["Date"])
    ncov_df["Country"] = ncov_df["Country/Region"].replace(
        {
            "Mainland China": "China",
            "Hong Kong SAR": "Hong Kong",
            "Taipei and environs": "Taiwan",
            "Iran (Islamic Republic of)": "Iran",
            "Republic of Korea": "South Korea",
            "Republic of Ireland": "Ireland",
            "Macao SAR": "Macau",
            "Russian Federation": "Russia",
            "Republic of Moldova": "Moldova",
            "Taiwan*": "Taiwan",
            "Cruise Ship": "Others",
            "United Kingdom": "UK",
            "Viet Nam": "Vietnam",
            "Czechia": "Czech Republic",
            "St. Martin": "Saint Martin",
            "Cote d'Ivoire": "Ivory Coast",
            "('St. Martin',)": "Saint Martin",
            "Congo (Kinshasa)": "Congo",
        }
    )
    ncov_df["Province"] = ncov_df["Province"].fillna("-").replace(
        {
            "Cruise Ship": "Diamond Princess cruise ship",
            "Diamond Princess": "Diamond Princess cruise ship"
        }
    )
    ncov_df["Infected"] = ncov_df["Confirmed"] - ncov_df["Deaths"] - ncov_df["Recovered"]
    ncov_df[data_cols] = ncov_df[data_cols].astype(np.int64)
    ncov_df = ncov_df.loc[:, ["Date", "Country", "Province", *data_cols]]
    return ncov_df

def open_line_list_load_and_clean(path):
    linelist_open_raw = pd.read_csv(path)
    df = linelist_open_raw.loc[:, ~linelist_open_raw.columns.str.startswith("Unnamed:")]
    df = df.dropna(axis=0, how="all")
    df = df.drop(
        [
            # Unnecessary in this notebook
            "ID", "wuhan(0)_not_wuhan(1)", "admin3", "admin2", "admin1", "country_new", "admin_id",
            "data_moderator_initials", "source", "location", "lives_in_Wuhan", "notes_for_discussion",
            "sequence_available", "reported_market_exposure",
            # Maybe useful, but un-used
            "city", "latitude", "longitude", "geo_resolution", "additional_information",
            "travel_history_dates", "travel_history_location",
        ],
        axis=1
    )
    # Personal
    age = linelist_open_raw["age"].str.split("-", expand=True)
    age[0] = pd.to_numeric(age[0], errors="coerce")
    age[1] = pd.to_numeric(age[1], errors="coerce")
    df["Age"] = age.mean(axis=1)
    df["Age"] = df["Age"].fillna(df["Age"].median()).astype(np.int64)
    df["Sex"] = df["sex"].fillna("-").str.replace("4000", "-").str.capitalize()
    # Place
    df["Country"] = df["country"].fillna("-")
    df["Province"] = df["province"].fillna("-")
    # Onset Date
    series = df["date_onset_symptoms"].str.replace("end of December 2019", "31.12.2019").replace("-25.02.2020",
                                                                                                 "25.02.2020")
    series = series.replace("20.02.220", "20.02.2020").replace("none", np.NaN).replace("10.01.2020 - 22.01.2020",
                                                                                       np.NaN)
    df["Onset_date"] = pd.to_datetime(series)
    # Hospitalized date
    series = df["date_admission_hospital"].replace("18.01.2020 - 23.01.2020", np.NaN)
    df["Hospitalized_date"] = pd.to_datetime(series)
    # Confirmed date
    series = df["date_confirmation"].replace("25.02.2020-26.02.2020", np.NaN)
    df["Confirmed_date"] = pd.to_datetime(series)
    # Symptoms/events
    df["Symptoms"] = df["symptoms"].fillna("-").str.lower()
    # Underlying disease
    df["Underlying_disease"] = df[["chronic_disease_binary", "chronic_disease"]].apply(
        lambda x: "No" if x[0] == 0 else x[1] if x[1] is not np.NaN else "-",
        axis=1
    ).str.strip(";").str.replace("; ", ",").str.replace(", ", ",")
    # Outcome
    df["Outcome"] = df["outcome"].replace(
        {
            "discharge": "discharged", "Discharged": "discharged", "death": "died",
            "critical condition, intubated as of 14.02.2020": "severe",
            "treated in an intensive care unit (14.02.2020)": "severe", "05.02.2020": "-",
            "Symptoms only improved with cough. Currently hospitalized for follow-up.": "stable"
        }
    ).fillna("-")
    series = df["date_death_or_discharge"].replace("discharge", np.NaN)
    df["Closed_date"] = pd.to_datetime(series)
    # Show
    use_cols = [
        "Age", "Sex", "Country", "Province", "Onset_date", "Hospitalized_date", "Confirmed_date",
        "Symptoms", "Underlying_disease", "Outcome", "Closed_date"
    ]
    open_linelist_df = df.loc[:, use_cols]
    return open_linelist_df

def line_list_load_and_clean(path):
    linelist_raw = pd.read_csv(path)
    df = linelist_raw.loc[:, ~linelist_raw.columns.str.startswith("Unnamed:")]
    df = df.drop(["id", "case_in_country", "summary", "source", "link"], axis=1)
    # Date
    case_date_dict = {
        "reporting date": "Confirmed_date",
        "exposure_start": "Exposed_date",
        "exposure_end": "Quarantined_date",
        "hosp_visit_date": "Hospitalized_date",
        "symptom_onset": "Onset_date",
        "death": "Deaths_date",
        "recovered": "Recovered_date"
    }
    df["death"] = df["death"].replace({"0": "", "1": ""})
    df["recovered"] = df["recovered"].replace({"0": "", "1": "", "12/30/1899": "12/30/2019"})
    for (col, _) in case_date_dict.items():
        df[col] = pd.to_datetime(df[col])
    df = df.rename(case_date_dict, axis=1)
    # Location
    df["Country"] = df["country"].fillna("-")
    df["Province"] = df["location"].fillna("-")
    df["Province"] = df[["Country", "Province"]].apply(lambda x: "-" if x[0] == x[1] else x[1], axis=1)
    # Personal
    df["Gender"] = df["gender"].fillna("-").str.capitalize()
    df["Age"] = df["age"].fillna(df["age"].median()).astype(np.int64)  ## Fill in NA with median
    df["From_Wuhan"] = df["from Wuhan"]
    df["To_Wuhan"] = df["visiting Wuhan"]
    # Medical
    df["Events"] = df["symptom"].fillna("-")
    # Order of columns
    linelist_df = df.loc[
                  :,
                  [
                      "Country", "Province",
                      "Exposed_date", "Onset_date", "Hospitalized_date", "Confirmed_date", "Quarantined_date",
                      "Deaths_date", "Recovered_date",
                      "Events",
                      "Gender", "Age", "From_Wuhan", "To_Wuhan"
                  ]
                  ]
    return linelist_df

def growth_factor(ncov_df):
    df = ncov_df.pivot_table(
        index="Date", columns="Country", values="Confirmed", aggfunc="sum"
    ).fillna(method="ffill").fillna(0)
    # Growth factor: (delta Number_n) / (delta Number_n)
    df = df.diff() / df.diff().shift(freq="D")
    df = df.replace(np.inf, np.nan).fillna(1)
    # Rolling mean (window: 7 days)
    df = df.rolling(7).mean()
    df = df.iloc[6:-1, :]
    # round: 0.1
    growth_value_df = df.round(1)
    df = growth_value_df.copy()
    df = df.iloc[-7:, :].T
    day_cols = df.columns.strftime("%d%b%Y")
    df.columns = day_cols
    # Grouping
    more_col, less_col = "GF > 1 [straight days]", "GF < 1 [straight days]"
    df[more_col] = (growth_value_df > 1).iloc[::-1].cumprod().sum(axis=0)
    df[less_col] = (growth_value_df < 1).iloc[::-1].cumprod().sum(axis=0)
    df["Group"] = df[[more_col, less_col]].apply(
        lambda x: "Outbreaking" if x[0] >= 7 else "Stopping" if x[1] >= 7 else "Crossroad",
        axis=1
    )
    # Sorting
    df = df.loc[:, ["Group", more_col, less_col, *day_cols]]
    df = df.sort_values(["Group", more_col, less_col], ascending=False)
    growth_df = df.copy()
    return growth_df
