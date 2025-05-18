import pytest 
from flood_monitoring import TidalLevel 

VALID_ID = 'E70024'

def test_instantiation():

    ''' Testiing that a TidalLevel object can be instantiated correctly '''
    station = TidalLevel(VALID_ID) 

    assert isinstance(station, TidalLevel) 


def test_tidal_range():

	''' Testing that the tidal range function returns a float '''

	assert isinstance(TidalLevel(VALID_ID).calculate_tidal_range(), float ) 

