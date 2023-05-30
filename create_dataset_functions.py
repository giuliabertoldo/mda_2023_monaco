import pandas as pd
import numpy as np
import boto3
import os
import json
import requests
from datetime import datetime, time
import math

# Initialize API key for Google maps API. This should be generated following the steps:
# 1. Create Google Cloud account and activate free trial
# 2. Create project
# 3. Enable places API in the project 
# 4. Copy your API key 
api_key = "paste yor api key here>"


def import_s3_noise_data_month(month):
    """ 
    Import noise data from s3 bucket "noise_data_month" folder where each folder corresponds to one month with noise data. 
    """

    # Connect to s3 bucket
    client = boto3.client('s3')

    response = client.list_objects_v2(
        Bucket='mda.project.monaco',
        Prefix='noise_data_month/%s' %(month))
    
    # Concatenate all csvs in folder
    df = pd.concat([pd.read_csv("s3://mda.project.monaco/"+file['Key'], sep=';')for file in response.get('Contents', [])])

    return(df)


def lat(descr):
    """ 
    Identify latitude based on description. 
    """

    if "01" in descr:
        latitude = 50.87725045952269
    elif "02" in descr:
        latitude = 50.87667332973864
    elif "03" in descr:
        latitude = 50.875965600507456
    elif "04" in descr:
        latitude = 50.87563410304464   
    elif "05" in descr:
        latitude = 50.87464931652004 
    elif "06" in descr:
        latitude = 50.87424051538546
    elif "07" in descr:
        latitude = 50.873946807679744   
    elif "Vrijthof" in descr:
        latitude = 50.879041132675574
    return(latitude)


def lon(descr):
    """ 
    Identify longitude based on description. 
    """

    if "01" in descr:
        longitude = 4.700713376547312
    elif "02" in descr:
        longitude = 4.700680922840582
    elif "03" in descr:
        longitude = 4.7002780085017495
    elif "04" in descr:
        longitude = 4.700197458227693 
    elif "05" in descr:
        longitude = 4.699889649514398
    elif "06" in descr:
        longitude = 4.700098238567968
    elif "07" in descr:
        longitude = 4.700107077294445 
    elif "Vrijthof" in descr:
        longitude = 4.701208864753383
    return(longitude)


def import_meteo(quarter):
    """ 
    Import meteo data from s3 bucket. 
    """

    # Import meteo data
    df_meteo = pd.read_csv("s3://mda.project.monaco/meteo_data/LC_2022Q%d.csv" %(quarter))

    # Keep only meteo data from station LC-105 (Mathieu de Layensplein, 3000 Leuven)
    df_meteo = df_meteo[df_meteo["ID"] == "LC-105"]

    # Keep only necessary columns
    df_meteo = df_meteo.drop(['ID', 'LC_HUMIDITY', 'LC_n', 'LC_RAD', 'LC_WINDDIR', 'Date', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'LC_RAD60'], axis=1)

    # Change column names to lowercase
    for col in df_meteo.columns:
        df_meteo.rename(columns = {col : col.lower()}, inplace=True)
    
    # Change column names dateutc to result_timestamp  
    df_meteo.rename(columns = {"dateutc" : "result_timestamp"}, inplace=True)

    # Convert result_timestamp to datetime type 
    # Convert "result_timestamp" to date_time format
    df_meteo['result_timestamp'] = pd.to_datetime(df_meteo['result_timestamp'], format="%Y-%m-%d %H:%M:%S")

    return(df_meteo)


def create_noise_meteo_csv_by_month(month):
    """ 
    Create final csvs, one for each month. Note: when running this function results are saved locally in "data/noise_sub/". The csvs have been uploaded in s3 bucket and made public.   
    """

    # If data/noise_sub folder does not exist, create one
    if not(os.path.exists("data/noise_sub")): 
        os.mkdir("data/noise_sub")

    # Import data for the selected month
    df = import_s3_noise_data_month(month)

    # Keep only necessary columns
    df = df.drop(['lamax_unit', 'laeq_unit', 'lceq_unit', 'lcpeak_unit', "#object_id", 'lamax', 'lceq', 'lcpeak'], axis = 1)

    # Convert "result_timestamp" to date_time format
    df['result_timestamp'] = pd.to_datetime(df['result_timestamp'], format="%d/%m/%Y %H:%M:%S.%f")

    # Groupby 10 minutes and average laeq variable
    df = df.groupby(['description', pd.Grouper(key='result_timestamp', freq='10min')])['laeq'].mean().reset_index() 

    # Create a new column only with the hour 
    df['hour'] = df['result_timestamp'].dt.hour

    # Create a new column only with the month 
    df['month'] = df['result_timestamp'].dt.month

    # Keep only rows between 19:00 and 7:00
    df = df[(df['hour'] >=19 ) | (df['hour'] <=7)]

    # Find the name of the week day
    df['day_of_week'] = df.apply(lambda row: row['result_timestamp'].day_name(),  axis = 1 )

    # Add temporary column "moved_day" 
    df['moved_day'] = df.apply(lambda row: row['result_timestamp'] - pd.Timedelta(days = 1), axis = 1 )

    # Add night_of_week (e.g. the morning hours of Tuesday, correspond to Monday night)
    df['night_of_week'] = np.nan
    
    for index, row in df.iterrows():
        if ((row['hour'] >= 0) and (row['hour'])) <= 7: 
            df['night_of_week'][index] = row['moved_day'].day_name()
        else:
            df['night_of_week'][index] = row['result_timestamp'].day_name()

    # Delete temporary column "moved_day"
    df = df.drop("moved_day", axis = 1)

    # Add if dulci_open
    df['dulci_open'] = np.nan

    for index, row in df.iterrows():
        if((row['night_of_week'] not in ['Friday', "Saturday"]) and (row['hour'] not in [6, 7, 19])):
            df['dulci_open'][index] = 1
        else:
            df['dulci_open'][index] = 0
    
    # Add latitude and longitude variables 
    df_lat_lon = df['description'].drop_duplicates().to_frame()
    df_lat_lon['lat'] = df_lat_lon.apply(lambda row: lat(row['description']), axis = 1 )
    df_lat_lon['lon'] = df_lat_lon.apply(lambda row: lon(row['description']),  axis = 1 )

    # Merge df_lat_lon with df
    df = pd.merge(left = df, right=df_lat_lon, on = "description")

    # Check the quarter of the month
    if month in ["Jan", "Feb", "March"]:
        quarter = 1
    elif month in ["April", "May", "June"]: 
        quarter = 2
    elif month in ["Jul", "Aug", "Sep"]:
        quarter = 3
    elif month in ["Oct", "Nov", "Dec"]:
        quarter = 4
    
    # Import and clean meteo data from the appropriate quarter 
    df_meteo = import_meteo(quarter)

    # Merge df_meteo with df
    df = pd.merge(left = df, right=df_meteo, on = "result_timestamp")

    # Save as csv
    df.to_csv("data/noise_sub/%s_sub.csv" %(month), index = False)

def concatenate_noise_meteo_sub_csv():
    """ 
    Concatenate all csvs in noise_sub folder in s3 bucket. 
    Note: when running this function the csv is saved locally in "data/". It has then been uploaded in s3 bucket and made public.   
    """

    # If data folder does not exist, create one
    if not(os.path.exists("data/")): 
        os.mkdir("data/")
    
    # Connect to s3 bucket
    client = boto3.client('s3')

    response = client.list_objects_v2(
        Bucket='mda.project.monaco',
        Prefix='noise_sub/')
    
    # Concatenate all csvs
    df = pd.concat([pd.read_csv("s3://mda.project.monaco/"+file['Key'])for file in response.get('Contents', [])])

    df.to_csv("data/project_data.csv", index = False)  

def coordinates_locations():
    """ 
    Create a dataframe with name, latitude and longitude of the given locations. 
    """
 
    df_coordinates = pd.DataFrame(
        [["01", "50.87725045952269", "4.700713376547312"],
        ["02", "50.87667332973864", "4.700680922840582"],
        ["03", "50.875965600507456", "4.7002780085017495"],
        ["04", "50.87563410304464", "4.700197458227693"],
        ["05", "50.87464931652004", "4.699889649514398"],
        ["06", "50.87424051538546", "4.700098238567968"],
        ["07", "50.873946807679744", "4.700107077294445"],
        ["Vrijthof", "50.879041132675574", "4.701208864753383"]
        ], 
        columns = ["location_name", "lat", "lon"]
    )
    return (df_coordinates) 

def urls_locations (df):
    """ 
    Given a dataframe with location name, latitude and longitude, return  urls to be used in requests to Google Maps API for the locals within a radius of 100m. 
    """

    radius = "radius=100"
    keyword = "keyword=nightlife"
    key = "key="+api_key

    urls = []
    for i, row in df.iterrows():
        location= "location=" +row["lat"]+"%2C"+row["lon"]
        urls.append("https://maps.googleapis.com/maps/api/place/nearbysearch/json?"+location+"&"+radius+"&"+keyword+"&"+key) 

    return(urls)


def get_ids_places(url):
    """ 
    From Google maps API, obtain ids of the nighlife places (pub, bar, club...) within a radius of 100m from specified location (maximum 20 locals are returns). closestwithin 
    """

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
    """ 
    Given a nighlife place id, call Google Maps API to obtain the opening hours. 
    """

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
    """ 
    Given an opening and closing time, generate the range of hours where the nighlife place is open.
    """
    
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
    """ 
    Clean response obtained from Google Maps API with opening hours. 
    """

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
    """ 
    Generate dataframe with counts of how many nighlife places are open on a certain day of the week and at a specific hour. 
    """

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

def opening_hours_locations_csv (urls, names):  
    """ 
    Given the url to send request to Google maps API and location name, find the opening hours of bars, pubs, clubs... and save as separate csv file for each location. 
    """

    for j, url in enumerate(urls):
        # For each location (url), obtain ids of niglife places within a radius of 100 m. 
        ids = get_ids_places(url)
        
        # Initialize output
        df_info = pd.DataFrame()

        # For each nighlife place, obtain opening times. 
        for i, id in enumerate(ids):
            weekday_hours = get_week_hours(id) 

            # If the opening hours are available, clean them to be ready for further processing.
            if weekday_hours is not None: 
                info = openings(weekday_hours)
                df_info.loc[i, "info"] = info
            
            elif weekday_hours is None: 
                df_info.loc[i, "info"] = None
        
        # Save opening hours of nighlife places close to targe location in a csv for later analysis. 
        df_info.to_csv("data/location_%s.csv" %(names[j]), index=False)

def merger(df, df_openings):
    """ 
    Merge noise + meteo data with opening hours data. 
    """

    # Delete dulci_open variable 
    df = df.drop('dulci_open', axis=1)

    # Rename day into day_of_week
    df_openings = df_openings.rename(columns={"day": "day_of_week"})

    # Add to df a column "location_name" that can be used as key when joining
    for i, row in df.iterrows(): 
        if "01" in row["description"]:
            df.at[i,'location_name'] = "01"
        elif "02" in row["description"]:
            df.at[i,'location_name'] = "02"
        elif "03" in row["description"]:
            df.at[i,'location_name'] = "03"
        elif "04" in row["description"]:
            df.at[i,'location_name'] = "04"
        elif "05" in row["description"]:
            df.at[i,'location_name'] = "05"
        elif "06" in row["description"]:
            df.at[i,'location_name'] = "06"
        elif "07" in row["description"]:
            df.at[i,'location_name'] = "07"
        elif "Vrijthof" in row["description"]:
            df.at[i,'location_name'] = "Vrijthof"

    # Merge 
    df_merged = pd.merge(left = df, right=df_openings, on = ["day_of_week", "hour", "location_name"])

    # Remove location_name variable
    df_merged = df_merged.drop('location_name', axis=1)

    return(df_merged)