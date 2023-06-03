# Noise in Leuven?

## Modern Data Analytics (GOZ39a), KU Leuven

### Team Monaco

Goals: Provide a dashboard to visualize noise levels in Namsestraat, Leuven, during night-time between 19:00 and 7:00, and develop a model that predicts the amount of noise.

#### Repository content:

  + `app`: Folder with scripts to run the Plotly-Dash app with visualizations. The app is deployed at https://mdamonaco.herokuapp.com
  
  + `create_dataset.ipynb`: Notebook to create initial dataset used in further steps of the analytic pipeline. The resulting csv is available at *s3://mda.project.monaco/project_data.csv*

  + `create_dataset_functions.py`: Functions and packages used in *create_dataset.ipynb* notebook.
  
  + `data.py`: Read initial dataset from S3 bucket.
  
  + `model.ipynb`: Notebook with analytic pipeline (preprocessing, modeling, postprocessing). 
