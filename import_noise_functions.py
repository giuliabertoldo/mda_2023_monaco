import pandas as pd
import os
import numpy as np
import datetime 

def import_noise_data(folder_num):
    """ Import noise data in folder structure with numbers (40, 41, 42)"""
    path = "data/noise_data/export_%d" %(folder_num)
    df = pd.concat( [pd.read_csv(os.path.join(path, file), sep=';') for file in os.listdir(path)] )   
    return(df) 

def import_noise_event_data():
    """Create dataframe with only relevant columns for noise events. """
    
    # Import noise event data (folder 41)
    df_event = import_noise_data(41)

    # Keep only columns of interest
    df_event = df_event.drop(['noise_event_laeq_model_id', 'noise_event_laeq_model_id_unit', 'noise_event_laeq_primary_detected_certainty_unit', 'noise_event_laeq_primary_detected_class_unit' ], axis = 1)

    # CONVERT result_timestamp TO date_time 
    df_event['result_timestamp'] = pd.to_datetime(df_event['result_timestamp'], format="%d/%m/%Y %H:%M:%S.%f")
    
    # CREATE SEPARATE COLUMNS: year, month, day, hour, minute, second
    df_event['year'] = df_event['result_timestamp'].dt.year
    df_event['month'] = df_event['result_timestamp'].dt.month
    df_event['day'] = df_event['result_timestamp'].dt.day
    df_event['hour'] = df_event['result_timestamp'].dt.hour
    df_event['minute'] = df_event['result_timestamp'].dt.minute
    df_event['second'] = df_event['result_timestamp'].dt.second

    # Keep only the first event in the minute 
    # Drop "second" column and remove duplicates 
    # Note: A check showed that there was not more than one event in the same minute
    df_event = df_event.drop(["second"], axis = 1)
    df_event = df_event.drop_duplicates()

    return(df_event)

def import_noise_data_by_month(month):
    """ Import latest noise data (folders named by month). """
    path = "data/noise_data_month/%s" %(month)
    df = pd.concat( [pd.read_csv(os.path.join(path, file), sep=';') for file in os.listdir(path)] )   
    return(df) 

def lat(descr):
    """ Identify latitude based on description. """
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
    """ Identify longitude based on description. """
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


def create_complete_noise_data(month, df_event):
    """ Create final csv for one month. """

    # Import data for the selected month
    df = import_noise_data_by_month(month)

    # DELETE UNIT OF MEASUREMENT
    df = df.drop(['lamax_unit', 'laeq_unit', 'lceq_unit', 'lcpeak_unit'], axis = 1) 

    # CONVERT result_timestamp TO date_time 
    df['result_timestamp'] = pd.to_datetime(df['result_timestamp'], format="%d/%m/%Y %H:%M:%S.%f")

    # CREATE SEPARATE COLUMNS: year, month, day, hour, minute, second
    df['year'] = df['result_timestamp'].dt.year
    df['month'] = df['result_timestamp'].dt.month
    df['day'] = df['result_timestamp'].dt.day
    df['hour'] = df['result_timestamp'].dt.hour
    df['minute'] = df['result_timestamp'].dt.minute
    df['second'] = df['result_timestamp'].dt.second

    # MAKE RESOLUTION AT THE LEVEL OF MINUTE
    df = df.groupby(by=["description", "year", "month", "day", "hour", "minute"]).mean().reset_index() 
    # Drop the "second" column
    df = df.drop(["second"], axis = 1) 

    # FIND WEEK DAY NAME
    # Convert result_timestamp back to string
    df['result_timestamp_str'] = df['result_timestamp'].astype(str)
    # Add two columns to separate date and minutes/seconds
    df[['date','date_detail']] = df['result_timestamp_str'].str.split(' ', expand=True)
    # Convert result_timestamp to date_time and delete result_timestamp column
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
    # Keep only date column 
    df_day = df.drop(['#object_id', 'description', 'result_timestamp', 'lamax', 'laeq', 'lceq', 'lcpeak', 'date_detail', 'year', 'month', 'day', 'hour', 'minute', 'result_timestamp_str'], axis = 1)
    # Keep only unique dates
    df_day = df_day.drop_duplicates()
    # Convert from charactert to date format
    df_day['date'] = pd.to_datetime(df_day['date'], format="%d/%m/%Y")
    # Find the name of the week day
    df_day['day_of_week'] = df_day.apply(lambda row: row['date'].day_name(),  axis = 1 )

    # FIND LATITUDE & LONGITUDE
    # Keep only description column 
    df_lat_lon = df.drop(['#object_id','result_timestamp', 'lamax', 'laeq', 'lceq', 'lcpeak', 'date', 'date_detail'], axis = 1)
    # Keep only unique descriptions
    df_lat_lon = df_lat_lon.drop_duplicates()
    # Add latitude and longitude
    df_lat_lon['lat'] = df_lat_lon.apply(lambda row: lat(row['description']),  axis = 1 )
    df_lat_lon['lon'] = df_lat_lon.apply(lambda row: lon(row['description']),  axis = 1 )
    # Keep only relevant columns
    df_lat_lon = df_lat_lon.drop(['year', 'month', 'day', 'hour', 'minute', 'result_timestamp_str'], axis = 1)
    # Drop duplicate rows 
    df_lat_lon = df_lat_lon.drop_duplicates()

    # ADD TO DF 3 COLUMNS: week_day_name, lat, lon
    # Merge the three datasets 
    df = pd.merge(left=df, right=df_day, on = "date")
    df = pd.merge(left = df, right=df_lat_lon, on = "description")

    # Merge with noise event data 
    df = pd.merge(left=df, right=df_event, how = "left", on = ["#object_id", "description", "result_timestamp"])
    # Keep only relevant columns
    df = df.drop(['year_y', 'month_y', 'day_y', 'hour_y', 'minute_y'], axis = 1)

    # SAVE AS CSV
    df.to_csv("data/noise_sub/%s_sub.csv" %(month), index = False)    
    
    

