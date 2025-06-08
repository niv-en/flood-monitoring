from .station import station 

class RiverLevel(station):
	
    ''' 
	RiverLevel class which inherits from the station class 
	'''

    def set_in_flood(self) -> None:

        '''
        Queries the flood status of the current stations location, in_flood is set to true 
        if there is a flood within 1km of the station
        '''
        query = 'id/floods' 
        params = {'lat' : self.latitude , 'long' : self.longitude , 'dist' : 1 , 'min-severity' : 1 }

        response = self.make_request(query, params) 

        self.__in_flood = True 

        if response['items'] != []: 
            self.__in_flood = False 

    @property
    def in_flood(self):

        ''' getter method for in_flood using the @property decator, making in_flood a read only attribute '''

        return self.__in_flood 

    def __init__(self, station_id : str) -> None:

        ''' initialsing River Level station by passing the parameter and qualifier values which signify River Level measures 
        to the constructor. measure_type stores the name of the station type'''

        super().__init__(station_id, parameter = 'level', qualifier = ['Stage', 'Downstream Stage', 'Height' ], measure_type = 'River Level'  ) 
        
        ''' 
        extending the functionality of the init function through polymoprhism,
        the flood status is now set during initialisation for RiverLevel stations   ''' 
        self.set_in_flood() 

    