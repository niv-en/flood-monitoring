from .station import station 

class RiverFlow(station):

	def __init__(self, station_id): 


		super().__init__(station_id, parameter = 'flow', qualifier = []  ) 

