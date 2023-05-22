import requests
import json
import pandas as pd

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

def return_time (day, string): 
    """ Return opening and closing time based on the day: 0 = Monday, ...., 6 = Sunday. """
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

def get_dataframe_with_info (details):
    """ Convert details obtained from API call to dataframe with opening hours and ratings."""
    
    df_out = pd.DataFrame()
    for i, c in enumerate(details):
        
        df_out.loc[i, "name"] = details[i]["name"]

        try:
            df_out.loc[i, "rating"] = details[i]["rating"]
        except KeyError:
            df_out.loc[i, "rating"] = None 

        try:
            weekday_hours = details[i]["opening_hours"]["weekday_text"]

            df_out.loc[i,"mon_open"] = return_time(0, weekday_hours[0].split())[0]
            df_out.loc[i,"mon_close"] = return_time(0, weekday_hours[0].split())[1]

            df_out.loc[i,"tue_open"] = return_time(0, weekday_hours[1].split())[0]
            df_out.loc[i,"tue_close"] = return_time(0, weekday_hours[1].split())[1]

            df_out.loc[i,"wed_open"] = return_time(0, weekday_hours[2].split())[0]
            df_out.loc[i,"wed_close"] = return_time(0, weekday_hours[2].split())[1]

            df_out.loc[i,"thu_open"] = return_time(0, weekday_hours[3].split())[0]
            df_out.loc[i,"thu_close"] = return_time(0, weekday_hours[3].split())[1]

            df_out.loc[i,"fri_open"] = return_time(0, weekday_hours[4].split())[0]
            df_out.loc[i,"fri_close"] = return_time(0, weekday_hours[4].split())[1]

            df_out.loc[i,"sat_open"] = return_time(0, weekday_hours[5].split())[0]
            df_out.loc[i,"sat_close"] = return_time(0, weekday_hours[5].split())[1]

            df_out.loc[i,"sun_open"] = return_time(0, weekday_hours[6].split())[0]
            df_out.loc[i,"sun_close"] = return_time(0, weekday_hours[6].split())[1]
        
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
        
    return(df_out)
        