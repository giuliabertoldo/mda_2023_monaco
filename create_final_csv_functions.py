import pandas as pd
import numpy as np
import boto3
import os

def import_s3_noise_data_export(folder_num):
    """ Import noise data from s3 bucket. Specify folder number: 40, 41, 42"""

    # Connect to s3 bucket
    client = boto3.client('s3')

    response = client.list_objects_v2(
        Bucket='mda.project.monaco',
        Prefix='noise_data/export_%d' %(folder_num))
    
    # Concatenate all csvs in folder
    df = pd.concat([pd.read_csv("s3://mda.project.monaco/"+file['Key'], sep=';')for file in response.get('Contents', [])])

    return(df)

def import_noise_event_data():
    """Import noise event data from s3 bucket and keep only relevant columns for noise events. """
    
    # Import noise event data (folder 41)
    df_event = import_s3_noise_data_export(41)

    # Keep only columns of interest
    df_event = df_event.drop(['#object_id','noise_event_laeq_model_id', 'noise_event_laeq_model_id_unit', 'noise_event_laeq_primary_detected_certainty_unit', 'noise_event_laeq_primary_detected_class_unit' ], axis = 1)

    # CONVERT result_timestamp TO date_time 
    df_event['result_timestamp'] = pd.to_datetime(df_event['result_timestamp'], format="%d/%m/%Y %H:%M:%S.%f")

    return(df_event)

def import_s3_noise_data_month(month):
    """ Import noise data from s3 bucket "noise_data_month" folder where each folder corresponds to one month with noise data. """

    # Connect to s3 bucket
    client = boto3.client('s3')

    response = client.list_objects_v2(
        Bucket='mda.project.monaco',
        Prefix='noise_data_month/%s' %(month))
    
    # Concatenate all csvs in folder
    df = pd.concat([pd.read_csv("s3://mda.project.monaco/"+file['Key'], sep=';')for file in response.get('Contents', [])])

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

def import_meteo(quarter):
    """ Import meteo data from s3 bucket. """

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

def create_final_csv_by_month(month):

    """ 
    Create final csvs, one for each month. Note: when running this function results are saved locally in "data/noise_sub/". For the project the folder has then be manually uploaded in s3 bucket and made public.   
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

def concatenate_noise_sub_csv():
    """ 
    Concatenate all csv in noise_sub folder in s3 bucket. 
    Note: when running this function the csv is saved locally in "data/". For the project, the file has then be manually uploaded in s3 bucket and made public.   
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