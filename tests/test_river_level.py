
from flood_monitoring import RiverLevel
import pytest 

VALID_ID = 'F1906' 

def test_instantiation():

    ''' Testiing that a RiverLevel object can be instantiated correctly '''
    river_level_station = RiverLevel(VALID_ID) 

    assert isinstance(river_level_station, RiverLevel ) 


def test_in_flood():

    ''' Double checking that inflood is a boolean datatype  '''
    river_level_station = RiverLevel(VALID_ID) 

    assert isinstance( river_level_station.in_flood , bool ) 
