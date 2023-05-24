
import pandas as pd
import json
import requests

# Initialize API key. This should be generated following the steps:
# 1. Create Google Cloud account and activate free trial
# 2. Create project
# 3. Enable places API in the project 
# 4. Copy your API key 
api_key = "<paste your key here>"

def get_data_first (url):
    """ Get data from Google places API without a token. """
    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)

    return(data)

def get_data_with_token(token, results, api_key):
    """ Get data from Google places API with a token. """
    new_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken="+ token + "&key=" + api_key

    new_data = get_data_first(new_url)

    new_results = new_data["results"]

    return([new_results, token])

def return_time (string): 
    """ Return opening and closing time"""
    if string[1] == "Closed": 
        open = "Closed"
        close = "Closed"
    elif string[1] == "Open": 
        open = "00:00"
        close = "23:59"
    else:
        open = string[1]
        close = string[4]
    return ([open, close])

def locals_details(url):
    """ Given a location, obtain information on opening hours and ratings of locals around the location."""
    # Obtain the ids of all locals in radius specified in url
    data_ids = get_data_first(url)

    # Extract the results 
    results_ids = data_ids["results"]

    # Create a list with the ids of all locals
    ids = []
    for r in results_ids:
        ids.append(r["place_id"])

    # For each local (id) extract name, rating and opening hours
    df_out = pd.DataFrame()
    for i, id in enumerate(ids):
        url_id = "https://maps.googleapis.com/maps/api/place/details/json?fields=name%2Crating%2Copening_hours&place_id="+id+"&key="+api_key

        payload={}
        headers = {}
        response_id = requests.request("GET", url_id, headers=headers, data=payload)

        data_id = json.loads(response_id.text)

        results_id = (data_id["result"]) 

        # Name
        df_out.loc[i, "name"] = results_id["name"]

        # Rating
        try:
            df_out.loc[i, "rating"] = results_id["rating"]
        except KeyError:
            df_out.loc[i, "rating"] = None 
        
        # Opening times
        try:
            weekday_hours = results_id["opening_hours"]["weekday_text"]

            df_out.loc[i,"mon_open"] = return_time(weekday_hours[0].split())[0]
            df_out.loc[i,"mon_close"] = return_time(weekday_hours[0].split())[1]

            df_out.loc[i,"tue_open"] = return_time(weekday_hours[1].split())[0]
            df_out.loc[i,"tue_close"] = return_time(weekday_hours[1].split())[1]

            df_out.loc[i,"wed_open"] = return_time(weekday_hours[2].split())[0]
            df_out.loc[i,"wed_close"] = return_time(weekday_hours[2].split())[1]

            df_out.loc[i,"thu_open"] = return_time(weekday_hours[3].split())[0]
            df_out.loc[i,"thu_close"] = return_time(weekday_hours[3].split())[1]

            df_out.loc[i,"fri_open"] = return_time(weekday_hours[4].split())[0]
            df_out.loc[i,"fri_close"] = return_time(weekday_hours[4].split())[1]

            df_out.loc[i,"sat_open"] = return_time(weekday_hours[5].split())[0]
            df_out.loc[i,"sat_close"] = return_time(weekday_hours[5].split())[1]

            df_out.loc[i,"sun_open"] = return_time(weekday_hours[6].split())[0]
            df_out.loc[i,"sun_close"] = return_time(weekday_hours[6].split())[1]
                
        except KeyError:

            df_out.loc[i,"mon_open"] = None
            df_out.loc[i,"mon_close"] = None

            df_out.loc[i,"tue_open"] = None
            df_out.loc[i,"tue_close"] = None

            df_out.loc[i,"wed_open"] = None
            df_out.loc[i,"wed_close"] = None

            df_out.loc[i,"thu_open"] = None
            df_out.loc[i,"thu_close"] = None

            df_out.loc[i,"fri_open"] = None
            df_out.loc[i,"fri_close"] = None

            df_out.loc[i,"sat_open"] = None
            df_out.loc[i,"sat_close"] = None

            df_out.loc[i,"sun_open"] = None
            df_out.loc[i,"sun_close"] = None
        
    
    # Return df
    return(df_out) 