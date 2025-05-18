from flood_monitoring import RiverFlow 
import pytest 

VALID_ID = '2928TH' 

# @pytest.fixture
# def valid_obj() -> station:
#     test = station(VALID_ID) 

#     return test

def test_instantiation():

    ''' Testiing that a RiverFlow object can be instantiated correctly '''
    station = RiverFlow(VALID_ID) 

    assert isinstance(station, RiverFlow ) 