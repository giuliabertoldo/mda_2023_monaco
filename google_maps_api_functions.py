
import pandas as pd
import json
import requests
import numpy as np
from datetime import datetime, time
import math

# Initialize API key. This should be generated following the steps:
# 1. Create Google Cloud account and activate free trial
# 2. Create project
# 3. Enable places API in the project 
# 4. Copy your API key 
api_key = "paste yor api key here>"

def urls_locations (df):
    """ Given a dataframe with location name, latitude and longitude, return  urls to be used in requests to Google Maps API for the locals within a radius of 100m. """

    radius = "radius=100"
    keyword = "keyword=nightlife"
    key = "key="+api_key

    urls = []
    for i, row in df.iterrows():
        location= "location=" +row["lat"]+"%2C"+row["lon"]
        urls.append("https://maps.googleapis.com/maps/api/place/nearbysearch/json?"+location+"&"+radius+"&"+keyword+"&"+key) 

    return(urls)

def get_ids_places(url):
    """ From Google maps API, obtain ids of the nighlife places (pub, bar, club...) within a radius of 100m from specified location (maximum 20 locals are returns). closestwithin """

    # Send request
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    
    data_ids = json.loads(response.text)

    # Extract the results 
    results_ids = data_ids["results"]

    # Create a list with the ids of all locals
    ids = []
    for r in results_ids:
        ids.append(r["place_id"])
    
    return(ids)

def get_week_hours(id):
    """ Given a nighlife place id, call Google Maps API to obtain the opening hours. """

    # Send request
    url_id = "https://maps.googleapis.com/maps/api/place/details/json?fields=name%2Crating%2Copening_hours&place_id="+id+"&key="+api_key

    payload={}
    headers = {}  
    response_id = requests.request("GET", url_id, headers=headers, data=payload)

    data_id = json.loads(response_id.text)

    # Extract the results 
    results_id = (data_id["result"]) 

    try:
        weekday_hours = results_id["opening_hours"]["weekday_text"]
    except KeyError:
        weekday_hours = None

    return(weekday_hours)

def opening_range(out_time_open, out_time_close):
    """ Given an oepning and closing time, genrates the range of hours where the nighlife place is open."""
    
    open = int(out_time_open.split(":")[0])
    close = int(out_time_close.split(":")[0])


    if open > close:
        range1 = range(open, 24)
        range2 = range(0, (close+1)) 

        range_open = list(np.concatenate([range1, range2]))

    elif open < close:
        range_open = list(range(open, (close + 1)))

    return(range_open)
       
def openings(weekday_hours):
    """ Clean response obtain from Google Maps API with opening hours for further processing. """

    # Initalize output
    out_string = []

    # For each day of the week with the opening hours: 
    for i, wh in enumerate(weekday_hours):

        # Split the string 
        row_splitted = (weekday_hours[i].split())

        # Check if it is closed 
        if wh.split()[1] == "Closed":
            out_string.append("/" + row_splitted[0]+ "100")

        # Check if it is Open 24 hours 
        elif wh.split()[1] == "Open":

            out_range = list(range(0, 24))
            out_range = ' '.join([str(elem) for elem in out_range])
            out_string.append("/" +row_splitted[0]  +  out_range  )

        # Check if there is opening and closing time 
        elif row_splitted[2] == "PM" or row_splitted[2] == "AM": 
        
            # Convert from AM/PM format to 24h format
            open = row_splitted[1] + " " + row_splitted[2]
            in_time_open = datetime.strptime(open, "%I:%M %p")
            out_time_open = datetime.strftime(in_time_open, "%H:%M")

            close = row_splitted[4] + " " + row_splitted[5]
            in_time_close = datetime.strptime(close, "%I:%M %p")
            out_time_close = datetime.strftime(in_time_close, "%H:%M")

            # Generate the range of hours the nighlife place is open. 
            out_range = opening_range(out_time_open, out_time_close)
            out_range = ' '.join([str(elem) for elem in out_range])

            out_string.append("/" +row_splitted[0]  +  out_range)
    
    # Output the string with opening hours 
    openings = ("".join(out_string))
    
    return(openings)

def count_open_bars (location_id):
    """ Generate dataframe with counts of how many nighlife places are open on a certain day of the week and at a specific hour. """

    # Load csv as dataframe
    locals1 = pd.read_csv("s3://mda.project.monaco/location_%s.csv" %(location_id))

    # Create dataframe with all days of the weeks and hours
    x = np.array([(x, y) for x in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] for y in range(0,24)])
    df = pd.DataFrame(x, columns = ['day', 'hour'])
    
    # Add column with counts and initialize at zero 
    df["count"] = 0

    # Add columns with location name
    df["location_name"] = location_id

    # Select only hours we are interested  
    df["hour"] = df["hour"].apply(pd.to_numeric)
    df = df.loc[(df.hour >= 19) | (df.hour <= 7)]

    # Convert hours to string for later string matching
    df['hour'] = df['hour'].apply(str)

    # Select the column with information and convert to list for iteration
    list_locals = locals1['info'].tolist()

    # Add the counts: how many locals are open on that day and hour
    for ll in list_locals:
        
        if type(ll) == str:
            string = ll.split("/")
            del string[0]
            
            for openings in string: 
                times = openings.split(":")
            
                for iter, row in df.iterrows():
                    if row["day"] == times[0] and row["hour"] in times[1].split(" "):
                        df.at[iter,'count'] = df.at[iter,'count'] +1 
                
        else:
            continue

    return(df)