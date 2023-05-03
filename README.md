# Noise in Leuven?

## Modern Data Analytics (GOZ39a), KU Leuven

### Team Monaco

Goal: Provide insights into what contributes to noise in the Naamsestraat (Leuven) during the nightime.

### Data 

* Final dataset is saved in s3 bucket: <a href="https://s3.eu-central-1.amazonaws.com/mda.project.monaco/project_data.csv">https://s3.eu-central-1.amazonaws.com/mda.project.monaco/project_data.csv</a>

  + Read using `df = pd.read_csv("s3://mda.project.monaco/project_data.csv")`

  + Dataset description in `data_description.txt`

* Just in case you would like to re-run the notebook to create the final dataset, note: 

  + <ins> I think I reached the free tier usage limit of 2000 LIST requests, so **run the code only if really necessary, please :)** </ins>

  + The code to create the final csv is in `create_final_csv_functions.py` and `create_final_csv_project_data.ipynb`
  
  + All the noise data and meteo data that we were given are stored in a public s3 bucket:
    
    + <a href="https://s3.eu-central-1.amazonaws.com/mda.project.monaco/meteo_data/">https://s3.eu-central-1.amazonaws.com/mda.project.monaco/meteo_data/</a>
    
    + <a heref="https://s3.eu-central-1.amazonaws.com/mda.project.monaco/noise_data_month/">https://s3.eu-central-1.amazonaws.com/mda.project.monaco/noise_data_month/</a>
    
    + <a href="https://s3.eu-central-1.amazonaws.com/mda.project.monaco/noise_data/">https://s3.eu-central-1.amazonaws.com/mda.project.monaco/noise_data/</a>: Data in this folder were not used to create the final dataset. 
  
  + Running the notebook takes a lot of time (more than one hour).
  
  + After running the notebook the processed data will be saved locally in the `data` folder. The processed data were then manually uploaded in the public s3 bucket: 
  
    + <a href="https://s3.eu-central-1.amazonaws.com/mda.project.monaco/noise_sub/">https://s3.eu-central-1.amazonaws.com/mda.project.monaco/noise_sub/</a> 
    
    + <a href="https://s3.eu-central-1.amazonaws.com/mda.project.monaco/project_data.csv">https://s3.eu-central-1.amazonaws.com/mda.project.monaco/project_data.csv</a>
  
 







