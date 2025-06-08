from flood_monitoring import RiverFlow 


VALID_ID = '2928TH' 


def test_instantiation():

    ''' Testiing that a RiverFlow object can be instantiated correctly '''
    station = RiverFlow(VALID_ID) 

    assert isinstance(station, RiverFlow ) 