# Flood Monitoring API 



## Overview

The Flood Monitoring wrapper is a python module created to simplifying accessing and plotting various weather readings such as Tidal/River Levels, Tempeatures and Flow rates. By using the functions defined in this module users are able to access real time data without having to write any API requireis themselves 

## Features 

- Allows users to interface with the Rich flood monitoring API 

- Allows you instatiate 4 different `station` types `RiverLevel`, `RiverFlow`, `TidalLevel`, `Temperature` 

- Fetch information about each Weather Station 

- Plot readings from each Weather Station 


adding test


## Getting started 

Instaling using pip 

``` sh
pip install git+https://github.com/niv-en/flood-monitoring

```

## Functionality 

### Different weather stations 

Currently the there are 4 primary classes: ``` RiverLevel```, ```RiverFlow```, ```TidalLevel``` and ``` Temperature``` each which inherit from the baseclass ```station```. 

### HOW TO: initialise a RiverLevel monitoring station and retrive the latest measurement 

``` py 

#import the RiverLevel class
from flood_monitoring import RiverLevel 

#pass in a valid StationID into the constructor 
river_level_station = RiverLevel('149TH')

#call the get_latest_measurement method
latest_measurement = river_level_station.get_latest_measurement() 

```

``` get_latest_measurement ``` will retrive all of the measurements related to the RiverLevel for the monitoring station with ID ```149TH```. The procedure defined above isnt unique to the ```RiverLevel``` station class can be applied to any of the station types provided a valid station ID. 

### HOW TO: Plot all readings from Measure Station between a particular range 

``` py

#import a station class 
from flood_monitoring import Temperature 

temperature_station = Temperature('1412') 

#need to add dates hre 
fig, ax = temperature_station.plot_data_range()

#specifying tight_layout so no objects draw over each other 

fig.tight_layout() 


fig.show() 

#or 

fig.save(filepath) 


```

Once again this can be applied to any of the station types, if no dates are specified t
(more explanation here )


## Station Specific Functions 

### HOW TO: Retrive the mean temperature over a given range 

``` py 

from flood_monitoring import Temperature 

temperature_station = Temperature('1412') 

avg_temp = temperature_station.mean_temperature() 


```


### HOW TO: Retrive the Tidal range over the last day

``` py 

from flood_monitoring import TidalLevel

tidal_station = TidalLevel('E70024') 

tidal_range = tidal_station.calculate_tidal_range() 

```


### HOW TO: Retrieve Readings for a particular measure 


```py
from flood_monitoring import station 

#initialising a generic station 
generic_station = station('1412') 

#selecting the id/notation from a one of the stations measures 
particular_meausre = generic_station.measures[0].notation 

#retrieving readings in the date range 
readings = generic_station.get_readings(measure_notation = particular_measure, 
                                        date_range = ['2025-06-01','2025-06-05'] ) 


#retrieving the readings from the date range specified in csv format 
readings_csv = generic_station.get_readings(measure_notation = particular_measure, 
                                        date_range = ['2025-06-01','2025-06-05'],
                                        csv = True ) 

#retrieving the last 10 readings for the current day as no date_range specified
readings_limit_10 = generic_station.get_readings(measure_notation = particular_measure,
                                                 limit = 10 )
```

### HOW TO: Create forecasts for a particular measure

``` py 
from flood_monitoring import ForecastStation

forecast_station = ForecastStation('1412') 

# retrieving a measure we wish to forecast

measure = forecast_station.measures[0].notation 

#load readings which will be used as training data 

readings = forecast_station.load_data(measure_notation = measure_notation,
                                      date_range = ['2025-06-01','2025-06-05'] ) 

#transforming out readings into a feature and target variable array 

X,y = forecast_station.transform_data(dataframe = readings, 
                                      lag_features = 3, 
                                      evaluation_split = False )

#fitting a linear regression model to the training data 
forecast_station.fit(X, y ) 
#predicting the next 5 values 
forecast = forecast_station.predict(n_predictions = 5 ) 

print(forecast) 
```

### HOW TO: Visualise Forecasts. 

``` py
import matplotlib.pyplot as plt 

fig, ax = forecast_station.visualise_predictions(predictions) 

plt.tight_layout() 

plt.show(block = True ) 

#or 

plt.savefig('filepath')
```

### HOW TO: Evaluate weather forecasts 

``` py 

#selecting measure to predict 

measure = forecast_station.mesures[0]


#lat_feautres = 3 , using last 3 values to predict the next 


forecast_station.evalute_forecast(measure = measure,
                                  date_range = ['2025-06-01', '2025-06-05'],
                                  split_size = 5, 
                                  lag_features = 3 ) 

```

## Additional Documentation 

Ipython notebooks are available in the Documentation section, which provide more detail around how to use each class etc. 


## Acknowledgements

This is a wrapper built on top of the UK Environemt Agency flood monitoring [API](...) and is not affiliated with the environemnt agency. 
