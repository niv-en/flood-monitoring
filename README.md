# Flood Monitoring API 



## Overview

The Flood Monitoring wrapper is a python module created to simplifying accessing and plotting various weather readings such as Tidal/River Levels, Tempeatures and Flow rates. By using the functions defined in this module users are able to access real time data without having to write any API requireis themselves 

## Features 

- Allows users to interface with the Rich flood monitoring API 

- Allows you instatiate 4 different `station` types `RiverLevel`, `RiverFlow`, `TidalLevel`, `Temperature` 

- Fetch information about each Weather Station 

- Plot readings from each Weather Station 




## Getting started 

Once installated run the following commands in your bash/zsh terminal, which will install of the dependencies required to run the module 

Installing the depencies in your current environment 

``` sh

#enter the package directory 
cd flood_monitoring 

#export requirements.txt 

poetry export > requirements.txt

pip install requirements.txt 

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

## Additional Documentation 

Ipython notebooks are available in the Documentation section, which provide more detail around how to use each class etc. 


## Acknowledgements

This is a wrapper built on top of the UK Environemt Agency flood monitoring [API](...) and is not affiliated with the environemnt agency. 