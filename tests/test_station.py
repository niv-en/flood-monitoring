from flood_monitoring import station
import pytest 

from matplotlib.figure import Figure
from matplotlib.axes import Axes 

import numpy as np 

VALID_ID = 'F1906'
INVALID_ID = '999' 


''' 

TESTING THE BASE STATION CLASS 

'''

@pytest.fixture
def valid_obj() -> station:
    test = station(VALID_ID) 

    return test



def test_instance(valid_obj: station):

	''' Double checking that our station has been correctly
	instantiated '''

	assert isinstance(valid_obj, station) 



def test_location(valid_obj: station): 

	''' Checking that the longitude and latitude of the station lie within the correct range'''

	long_range = (-180.0,  180.0 )
	lat_range = (-90.0 , 90.0 ) 

	longitude = valid_obj.longitude
	latitude = valid_obj.latitude 

	assert long_range[1] >=  longitude >= long_range[0]

	assert lat_range[1] >= latitude >= lat_range[0] 

	
''' Adjusing station handling '''
def test_invalid_station_id():
	
	with pytest.raises(Exception, match = 'Incorrect Station ID'): 

		station(INVALID_ID)

''' Testing Generic Functions which are to be inherited by each of the classes '''

def test_get_latest_measurement(valid_obj: station): 

	''' Double checking that the get_latest_measurement method returns a dictoinary '''

	measurements = valid_obj.get_latest_measurement() 

	assert isinstance(measurements, dict) 

def test_plot_data(valid_obj: station): 

	''' Double check that the fig, ax objects returned by the function are instances of the correct classes '''

	fig, ax = valid_obj.plot_data() 
	
	assert isinstance(fig, Figure) 

	assert  (isinstance(ax, np.ndarray) | isinstance(ax, Axes)) 

def test_plot_data_range(valid_obj: station): 

	''' Double check that the fig, ax objects returned by the function are instances of the correct classes '''

	fig, ax = valid_obj.plot_data_range() 
	
	assert isinstance(fig, Figure) 

	assert  (isinstance(ax, np.ndarray) | isinstance(ax, Axes)) 


def test_plot_data_range_invalid_date_format(valid_obj: station):

	''' Passing in non valid date objects to our plot_data_range function '''

	date_range = ('Dinosaur', 'Big Frog') 

	with pytest.raises(Exception, match = 'Invalid Date Format' ): 

		valid_obj.plot_data_range(date_range)


def test_plot_data_range_invalid_order(valid_obj: station):

	''' Passing in a date range where the enddate is earlier than the startdate ''' 

	date_range = ('2023-01-23', '2023-01-02')

	with pytest.raises(Exception, match = 'End date before start date'):
		valid_obj.plot_data_range(date_range) 


# RIVER_LEVEL_STATION = 'F1906'
# RIVER_FLOW_STATION = '2928TH'
# TIDAL_LEVEL_STATION = 'E70024'
# TEMPERATURE_STATION = '1412'

# #Testing the initialisation of each of the station types 
# @pytest.mark.parametrize("stationclass,id", [(RiverLevel, RIVER_LEVEL_STATION),
# 											 (RiverFlow, RIVER_FLOW_STATION), 
# 											 (TidalLevel, TIDAL_LEVEL_STATION), 
# 											 (Temperature, TEMPERATURE_STATION)] ) 
# def test_station_types(stationclass, id):

# 	assert isinstance(stationclass(station_id = id), stationclass ) 


# def test_get_latest_reading():

# 	''' double checking that function returns a dictionary '''

# 	temp = Temperature(TEMPERATURE_STATION) 

# 	assert isinstance(temp.get_latest_measurement() , dict) 


# def test_plot_data(): 

# 	''' Double checking the properties of a particular figure '''

# TidalLevel(TIDAL_LEVEL_STATION) 







