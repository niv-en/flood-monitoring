import pytest
from flood_monitoring import Temperature 

VALID_ID = '1412'


def test_instantiation():

    ''' Testiing that a Temperature object can be instantiated correctly '''
    station = Temperature(VALID_ID) 
    assert isinstance(station, Temperature ) 


def test_mean_temperature(): 
	''' similar to test_tidal_range() double checking that mean temperature returns a float '''
	assert isinstance(Temperature(VALID_ID).average_temp(), float ) 