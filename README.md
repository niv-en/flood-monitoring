# Flood Monitoring API wrapper



## Overview

This module was created in order to simplify accessing and plotting various weather readings such as Tidal/River Levels, Tempeatures and Flow rates.  The functions defined in the module allow interfacting with real time data from the [Enviroment Agency flood monitoring API](https://environment.data.gov.uk/flood-monitoring/doc/reference)

## Features 

- Allows users to interface with the Rich flood monitoring API 

- 4 different `station` classes `RiverLevel`, `RiverFlow`, `TidalLevel`, `Temperature` and a `Forecast` class 

- Fetch information about each weather station. (position, measures etc0 )

- Retrieve readings for each station 

- Plot readings from each Weather Station 

- Predict/Forecast readings




## Getting started 

The package can be installed using pip referencing the repository in Github. 

``` sh
pip install git+https://github.com/niv-en/flood-monitoring
```

## Functionality 

### Different classes 

There are 5 classes : 

There are 4 measure station classes  ``` RiverLevel```, ```RiverFlow```, ```TidalLevel``` , ``` Temperature``` which can be used to instantiate different station types which monitor different measures. There is also a `Forecast` class which provides methods to forecast values for measures. 

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

#plotting the temperature readings from 1st to the 6th of June. 
fig, ax = temperature_station.plot_data_range(['2025-06-01', '2025-06-05'])

#specifying tight_layout so no objects draw over each other 
fig.tight_layout() 


fig.show() 

#or 

fig.save(filepath) 

```

Once again this can be applied to any of the station types, if no dates are passed to `plot_data_range` then the readings for the current day will be plotted. 

### HOW TO: Retrieve readings for a particular measure 

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

Similar to `plot_date_range` if no dates are specied the readings for the current day will be returned. By default the readings are returned as JSON, However if `csv` is set to `True` they will be returned as a csv string. `limit` is an optional parameter, if not provided then all of the readings from the query will be returned. 

## Station Specific Functions 

Some weather station classes have additional methods and attributesto extend the functionality of the base `station` class. E.g. The `Temperature` station class provides a function calculate the mean temperature and the `TidalLevel` station class provides a function to calculuate the tidal range. 

### Temperature 

### HOW TO: Retrive the mean temperature over a given date range. 

``` py 

from flood_monitoring import Temperature 

temperature_station = Temperature('1412') 

avg_temp = temperature_station.mean_temperature(date_range = ['2025-06-01', '2025-06-07']) 

```

If no date_range is specified then the mean temperature of the current day will be computed. 

### Tidal Level 

### HOW TO: Retrive the tidal range over a given date range. 

``` py 

from flood_monitoring import TidalLevel

tidal_station = TidalLevel('E70024') 

tidal_range = tidal_station.calculate_tidal_range(['2025-06-01', '2025-06-07']) 

```

#### Forecast Station 

The ForecastStation, class extends the standard `station` class. It provides methods to forecast measures using a  simple autoregressive linear regression model (produces predictions by using the previous n values ). The class also includes  methods to load and transform the data, as well as visualise and evalute forecasts.

### HOW TO: Create forecasts for a particular measure

``` py 
from flood_monitoring import Forecast

forecast = Forecast() 

# retrieving the noation/id for the particular measure we wish to forecast
measure = 'E70024-level-tidal_level-Mean-15_min-m'

#load readings as a dataframe to be used as training data 
readings = forecast.load_data(measure_notation = measure_notation,
                                      date_range = ['2025-06-01','2025-06-05'] ) 

#transforming out readings into a feature and target arrays, evaluation_split set to False meaning all readings will be used as training data and lag_feature of 3 means the previous 3 values will be used to predict the next. 
X,y = forecast.transform_data(dataframe = readings, 
                                      lag_features = 3, 
                                      evaluation_split = False )

#Fitting our model to the data 
forecast.fit(X, y ) 

#forecasting values, n_predictions is equal to the number of future values we want to predict. 
forecast = forecast.predict(n_predictions = 5 ) 

#priting forecast
print(forecast) 
```

### HOW TO: Visualise Forecasts. 

``` py
import matplotlib.pyplot as plt 

fig, ax = forecast.visualise_predictions(predictions, ground_truth, test_timestamps, measure)  

plt.tight_layout() 

plt.show(block = True ) 

#or 

plt.savefig('filepath')
```

`ground_truth` is an optional parameter,  the `ground_truth` readings are supplied then they are plotted side by side with the predicted values. 

### HOW TO: Evaluate weather forecasts 

``` py 

#selecting a measure from the river_level station initialised previously we wish to predict. 
measure = river_level.measures[0] 


#function will train and evaluate the model and return graph displaying the predictions against the ground truth. 
forecast.evalute_forecast(measure = measure,
                                  date_range = ['2025-06-01', '2025-06-05'],
                                  split_size = 5, 
                                  lag_features = 3 ) 
```

This function orchastrate and strings together  `ForecastStation` methods to evaluate a measure forecast with one function call. 

1. Retrieve and transform the data
2. Train the model
3. Produce predictions
4. Evaluate predictions 

## Additional Documentation 

3 Ipython notebooks are available in the Documentation section, which provide more detail around which methods and attributes are available for each class. 

## Acknowledgements

This is a wrapper built on top of the UK Environemt Agency flood monitoring [API](...) and is not affiliated with the environemnt agency. 