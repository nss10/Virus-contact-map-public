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

4. Run Flask Server using <code>python3 -m flask run</code> from the [python](./python) directory

5. Intialize the npm server from the root directory by using the command <code> npm update </code>

6. Run NodeJs server using <code> npm start</code> from the root directory