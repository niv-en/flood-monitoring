from .station import station 

class RiverLevel(station):
	
    ''' 
	RiverLevel class which inherits from the station class 
	'''


    def set_in_flood(self) -> None:
        '''
        Queries the flood status of the current stations location
        '''
        query = 'id/floods' 
        params = {'lat' : self.latitude , 'long' : self.longitude , 'dist' : 0 , 'min-severity' : 1 }

        response = self.make_request(query, params) 

        self.__in_flood = True 
        if response['items'] != []: 
            self.__in_flood = False 

    @property
    def in_flood(self):

        return self.__in_flood 

    def __init__(self, station_id : str) -> None: 

        super().__init__(station_id, parameter = 'level', qualifier = ['Stage', 'Downstream Stage', 'Height' ], measure_type = 'River Level'  ) 

        self.set_in_flood() 

    