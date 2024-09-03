# Streamlit App
## Setup -
Recommended to create a virtual environment. 
Run this initially
```bash
pip install -r requirements.txt
cd WebDev
```
## dummy_data - 
A flask server that generates continuous data. \
This is to emulate the IoT input we will receive. \
The flask server will be such that it will send continuous varying temperatures of 50 different locations. \
To run this (Run this in a separate terminal):
```bash
cd dummy_data
python app.py
```

## map_output - 
This will contain the streamlit file. \
At the moment, it only runs the map aspect of the webpage. \
This will take the data from the flask server and show the locations color coded based on the temperature in an interactive map. \
To run this (Run this in a separate terminal):
```bash
cd map_output
streamlit run app.py
```
