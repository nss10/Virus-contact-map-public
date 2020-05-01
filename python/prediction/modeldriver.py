import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pprint import pprint
from simulator import simulation
from estimator import Estimator
from predictor import Predicter
from data_utility import load_and_clean, create_target_df, open_line_list_load_and_clean, line_list_load_and_clean, select_area
from plot_util import line_plot, show_trend
from pyramid import pyramid
import seaborn as sns
from model.SIR import SIR
from model.SIRF import SIRF
from model.SEWIRF import SEWIRF
from datetime import datetime

pd.plotting.register_matplotlib_converters()
time_format = "%d%b%Y %H:%M"

for dirname, _, filenames in os.walk("./data/novel-corona-virus-2019-dataset"):
    for filename in filenames:
        print(os.path.join(dirname, filename))

np.random.seed(2019)
os.environ["PYTHONHASHSEED"] = "2019"

plt.style.use("seaborn-ticks")
plt.rcParams["xtick.direction"] = "in"
plt.rcParams["ytick.direction"] = "in"
plt.rcParams["font.size"] = 11.0
plt.rcParams["figure.figsize"] = (9, 6)

class Driver:
    def __init__(self):
        self.data_cols = ["Infected", "Deaths", "Recovered"]
        self.extended_data_cols = ["Infected", "Deaths", "Recovered", 'Infected, considering 2.3% Mortality', 'Infected, considering 1% Mortality']
        self.rate_cols = ["Fatal per Confirmed", "Recovered per Confirmed", "Fatal per (Fatal or Recovered)"]
        self.variable_dict = {"Susceptible": "S", "Infected": "I", "Recovered": "R", "Deaths": "D"}
        self.ncov_df = load_and_clean("./data/novel-corona-virus-2019-dataset/covid_19_data.csv")
        self.open_linelist_df = open_line_list_load_and_clean("./data/novel-corona-virus-2019-dataset/COVID19_open_line_list.csv")
        self.linelist_df = line_list_load_and_clean("./data/novel-corona-virus-2019-dataset/COVID19_line_list_data.csv")
        self.prmd = pyramid()
        self.population_dict = self.prmd.get_population_dict()
        self.life_out = self.prmd.life_out()


    def cases_over_time(self, country):
        country = "US"
        total_df = self.ncov_df.loc[self.ncov_df["Country"] == country, :].groupby("Date").sum()
        total_df[self.rate_cols[0]] = total_df["Deaths"] / total_df[self.data_cols].sum(axis=1)
        total_df[self.rate_cols[1]] = total_df["Recovered"] / total_df[self.data_cols].sum(axis=1)
        total_df[self.rate_cols[2]] = total_df["Deaths"] / (total_df["Deaths"] + total_df["Recovered"])
        line_plot(total_df[self.data_cols], f"Cases over time (in {country})")

    def rate_over_time(self, country):
        total_df = self.ncov_df.loc[self.ncov_df["Country"] == country, :].groupby("Date").sum()
        total_df[self.rate_cols[0]] = total_df["Deaths"] / total_df[self.data_cols].sum(axis=1)
        total_df[self.rate_cols[1]] = total_df["Recovered"] / total_df[self.data_cols].sum(axis=1)
        total_df[self.rate_cols[2]] = total_df["Deaths"] / (total_df["Deaths"] + total_df["Recovered"])
        line_plot(total_df[self.rate_cols], f"Rate over time (in {country})", ylabel="", math_scale=False)

    def kde_estimate(self, country):
        total_df = self.ncov_df.loc[self.ncov_df["Country"] == country, :].groupby("Date").sum()
        total_df[self.rate_cols[0]] = total_df["Deaths"] / total_df[self.data_cols].sum(axis=1)
        total_df[self.rate_cols[1]] = total_df["Recovered"] / total_df[self.data_cols].sum(axis=1)
        total_df[self.rate_cols[2]] = total_df["Deaths"] / (total_df["Deaths"] + total_df["Recovered"])
        total_df[self.rate_cols].plot.kde()
        plt.title(f"Kernel density estimation of the rates (in {country})")
        plt.show()

    def currentEstimate(self, country, start_date):
        _, df = create_target_df(self.ncov_df,
                                 self.population_dict[country],
                                 places=[(country, None)],
                                 start_date=start_date)

        line_plot(df.set_index("Date")[self.data_cols],
                  f"{country}: current state from {start_date}",
                  math_scale=False)

    def sirEstimate(self, country, places, start_date, excluded, for_days=365):
        estimator = Estimator(
            SIR,
            self.ncov_df,
            self.population_dict[country],
            name=country,
            places=places,
            excluded_places=excluded,
            start_date=start_date
        )
        country_dict = estimator.run()
        print(country_dict)
        #estimator.predict_graph(step_n=for_days,excluded_cols=['Susceptible'])
        return country_dict

    def sirFEstimator(self, country, places, start_date, excluded, tau, for_days=365):
        estimator = Estimator(
            SIRF,
            self.ncov_df,
            self.population_dict[country],
            name=country,
            places=places,
            excluded_places=excluded,
            start_date=start_date,
            tau=tau
        )
        country_dict = estimator.run()
        print(country_dict)
        #estimator.compare_graph()
        estimator.predict_graph(step_n=for_days, excluded_cols=['Susceptible'])
        return country_dict

    def compare(self, date):
        n = 5
        start_date = date
        date_format = "%d%b%Y"
        df = self.ncov_df.loc[self.ncov_df["Date"] > datetime.strptime(start_date, date_format), :]
        country_df = df.pivot_table(
            values="Infected", index="Date", columns="Country", aggfunc=sum
        ).fillna(0).astype(np.int64)
        country_df = country_df.drop("China", axis=1)
        to_add_later = country_df[['India', 'Australia']]
        to_plot = country_df.T.nlargest(n, country_df.index.max()).T
        to_plot['India'] = to_add_later['India']
        to_plot['Australia'] = to_add_later['Australia']
        line_plot(
            to_plot,
            f"Infected in top {n} countries except China (in Log scale), with India and Australia",
            math_scale=False, y_logscale=True
        )

    def sewirFEstimator(self, country, places, start_date, excluded, theta, kappa, sigma, tau, for_days=365):
        param_dict = {}
        param_dict['theta'] = theta
        param_dict['kappa'] = kappa
        param_dict['sigma'] = sigma
        param_dict['tau'] = tau

        print(param_dict)
        estimator = Estimator(
            SEWIRF,
            self.ncov_df,
            self.population_dict[country],
            name=country,
            places=places,
            excluded_places=excluded,
            start_date=start_date,
            **param_dict
        )
        country_dict = estimator.run(700)
        print(country_dict)
        #estimator.compare_graph()
        first_model, info_dict, param_dict = estimator.info()
        predicter = Predicter(**info_dict)
        predicter.add(first_model, end_day_n=None, count_from_last=False, **param_dict)
        predicter.add(first_model, end_day_n=for_days, count_from_last=True, **param_dict)
        predicter.restore_graph(drop_cols=["Susceptible", "Exposed"]) #

    def weighted_average_days_out(self, country):
        self.ec_out_df = self.prmd.weight_average_out(country)
        self.gs_before = self.ec_out_df["Weighted"].sum()
        self.ec_out_lockdown = self.prmd.weight_average_lockdown(country)
        self.gs_after = self.ec_out_lockdown["Weighted_lockdown"].sum()
        #self.ec_out_lockdown.to_csv('lockdown.csv')

    def create_parameters(self):
        period_df = select_area(self.linelist_df, excluded_places=[("China", None)], group=None)
        period_df = period_df.loc[:, ["Exposed_date", "Onset_date", "Confirmed_date"]]
        period_df["Latent [min]"] = (period_df["Onset_date"] - period_df["Exposed_date"]).dt.total_seconds() / 60
        period_df["Waiting [min]"] = (period_df["Confirmed_date"] - period_df["Onset_date"]).dt.total_seconds() / 60
        period_df["Latent [day]"] = period_df["Latent [min]"] / 60 / 24
        period_df["Waiting [day]"] = period_df["Waiting [min]"] / 60 / 24
        period_df["Latent + Waiting [day]"] = period_df["Latent [day]"] + period_df["Waiting [day]"]

        self.period_df = period_df

        self.latent_period = self.period_df["Latent [min]"].median()
        self.waiting_time = self.period_df["Waiting [min]"].median()
        self.latent_waiting_day = period_df["Latent + Waiting [day]"].median()

    def sewirFEstimator_lockdown(self, country, places, start_date, excluded, theta, kappa, sigma, tau, for_days=365):
        param_dict = {}
        param_dict['theta'] = theta
        param_dict['kappa'] = kappa
        param_dict['sigma'] = sigma
        param_dict['tau'] = tau

        print(param_dict)
        estimator = Estimator(
            SEWIRF,
            self.ncov_df,
            self.population_dict[country],
            name=country,
            places=places,
            excluded_places=excluded,
            start_date=start_date,
            **param_dict
        )
        country_dict = estimator.run(700)
        print(country_dict)
        # estimator.compare_graph()
        first_model, info_dict, param_dict = estimator.info()

        beta1_before = param_dict["rho1"] / info_dict["tau"]
        beta1_after = beta1_before * (self.gs_after / self.gs_before)

        info_dict["name"] = country
        changed_param_dict = param_dict.copy()
        changed_param_dict["rho1"] = param_dict["rho1"] * beta1_after / beta1_before
        df = pd.DataFrame.from_dict(
            {"No actions": param_dict, "With actions": changed_param_dict},
            orient="index"
        )
        df = df.loc[:, ["rho1", "rho2", "rho3", "theta", "kappa", "sigma"]]
        df["R0"] = df.apply(lambda x: first_model(**x.to_dict()).calc_r0(), axis=1)
        df["tau"] = info_dict["tau"]
        print(df)

        predicter = Predicter(**info_dict)
        predicter.add(SEWIRF, end_day_n=None, count_from_last=False, vline=True, **param_dict)
        predicter.add(SEWIRF, end_day_n=self.latent_waiting_day, count_from_last=True, vline=True, **param_dict)
        predicter.add(SEWIRF, end_day_n=for_days, count_from_last=True, vline=True, **changed_param_dict)
        predicter.restore_graph(drop_cols=["Susceptible", "Exposed"])

    def trend_analysis(self, country, start_date):
        show_trend(self.ncov_df, variable="Confirmed", places=[(country, None)], n_changepoints=2, start_date=start_date)

    def compare_first_k_days_since_100(self, country_list, k):
        df = self.ncov_df.copy()
        country_df_infected = df.pivot_table(
            values="Infected", index="Date", columns="Country", aggfunc=sum
        ).fillna(0).astype(np.int64)

        d = {}
        for c in country_list:
            series = country_df_infected[c]
            d[c] = [e for e in series if e > k]

        to_plot = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in d.items() ]))
        line_plot(
            to_plot,
            f"Infected in top countries, with Australia and India", xlabel=f'Days since {k} cases',
            math_scale=False, y_logscale=True
        )

    def mortality_analysis(self, country, start_date):
        _, df = create_target_df(self.ncov_df,
                                 self.population_dict[country],
                                 places=[(country, None)],
                                 start_date=start_date)
        df['Infected, considering 2.3% Mortality'] = df['Deaths']*100.0/2.3
        df['Infected, considering 1% Mortality'] = df['Deaths'] * 100.0
        #df['0.1% Mortality'] = df['Deaths'] * 100.0/0.1
        line_plot(df.set_index("Date")[self.data_cols],
                  f"{country}: current state from {start_date}",
                  math_scale=False)
        pass


country = "India"
start_date = "28Mar2020"
fdays = 60
places = [(country, None)]
excluded = None


drv = Driver()

#drv.trend_analysis(country, start_date)
#drv.compare(start_date)
#drv.compare_first_k_days_since_100(['US', 'Italy', 'Spain', 'UK', 'India', 'Australia'], 1000)
#drv.currentEstimate(country, start_date)
#
#
#
SIR_country_dict = drv.sirEstimate(country,
                                   places,
                                   start_date,
                                   excluded,
                                   for_days=fdays)


SIRF_country_dict = drv.sirFEstimator(country,
                                      places,
                                      start_date,
                                      excluded,
                                      tau = SIR_country_dict['tau'],
                                      for_days=fdays)

#
# drv.sewirFEstimator(country,
#                     places,
#                     start_date,
#                     excluded,
#                     theta = SIRF_country_dict['theta'],
#                     kappa = SIRF_country_dict['kappa'],
#                     sigma = SIRF_country_dict['sigma'],
#                     tau = SIRF_country_dict['tau'],
#                     for_days=fdays)

# Effect of lockdown delay
# drv.create_parameters()
# drv.weighted_average_days_out(country)
# drv.sewirFEstimator_lockdown(country,
#                     places,
#                     start_date,
#                     excluded,
#                     theta = SIRF_country_dict['theta'],
#                     kappa = SIRF_country_dict['kappa'],
#                     sigma = SIRF_country_dict['sigma'],
#                     tau = SIRF_country_dict['tau'],
#                     for_days=fdays)
# Effect of seasonality
# Effcet of social distancing

