from .station import station 

class RiverFlow(station):

	'''
	RiverFlow class which inherits from the station class 
	'''

	def __init__(self, station_id : str) -> None: 


		super().__init__(station_id, parameter = 'flow', qualifier = [] , measure_type = 'River Flow') 

