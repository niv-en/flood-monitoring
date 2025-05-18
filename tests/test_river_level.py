from flood_monitoring import RiverLevel
import pytest 

VALID_ID = 'F1906' 

def test_instantiation():

    ''' Testiing that a RiverLevel object can be instantiated correctly '''
    station = RiverLevel(VALID_ID) 

    assert isinstance(station, RiverLevel ) 