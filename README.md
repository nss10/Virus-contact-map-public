> [ReadMe file In-progress]
# Virus-contact-map-public
Virus Contact map is a data visualization platform to see the spread of Covid-19 over a period of time across all the counties in the state of United States. 


# Requirements
1. Python 3.x
2. Pip
3. MongoDB
4. NodeJs


# How to setup 

1. To set up a local version of the application, one needs to clone the repository and change the credentials of the database in [config.py](./python/config.py)

2. Install flask server and set the environment variable FLASK_APP to `API.py`

3. Run <code> pip install -r requirements.txt </code> or <code>python3 -m pip -r 
requirements.txt</code>

4. Run [preprocess.py](./python/preprocess.py) using Python3 to fetch and update all database records in MongoDB.

5. Run Flask Server using <code>python3 -m flask run</code> from the [python](./python) directory

6. Intialize the npm server from the root directory by using the command <code> npm update </code>

7. Run NodeJs server using <code> npm start</code> from the root directory

8. Once Both Flask and Node servers are running, open browser and enter the following url in the address bar http://localhost:3000 to access the application


# Working with Strain Data

* Unlike all the datasets that are publicly available, strain Data is the only dataset that is fetched from a private repository. 
* If you have access to the repo, you can view the dataset here - [Strain_data_csv](https://github.com/gagnonlab/ncov-data/blob/master/gagnon_data.csv)
* In order to fetch strain data to your local server, you would need to get a GIT_AUTH_TOKEN and set it as an environment variable.
* Useful Links 
    - [Creating a personal access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)
    - [How To Set Environment Variables](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html)


# Working with Mobility Data

* Google's mobility data is a public database that can be downloaded from here - [Google Mobility Data](https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv)
* It is the largest dataset that is needed to be downloaded in order to complete the preprocessing part and thus has become a bottleneck for the process. 
* In case you don't require Google's mobility data for your part of work, then open [preprocess.py](./python/preprocess.py) and replace 
``` python
mobility_data = getMobilityData()
```
with
``` python
 mobility_data = [] 
```

