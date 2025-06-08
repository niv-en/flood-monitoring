from .station import station 

class RiverFlow(station):

	'''
	RiverFlow class which inherits from the station class 
	'''

	def __init__(self, station_id : str) -> None: 
		
		'''
		initialising RiverFlow station by passing 'flow' as a parameter and setting measure_type to 'River Flow'
		'''

		super().__init__(station_id, parameter = 'flow', qualifier = [] , measure_type = 'River Flow') 

