from .station import station 

class TidalLevel(station):

	'''
	TidalLevel station which inherits from the station class
	'''

	def __init__(self, station_id : str) -> None:  

		'''
		Initialising a Tidal Level station by passing 'level' as a paramter and 'Tidal Level' as a qualifer.
		measure_type is set to the station type 'Tidal Level' 
		'''

		super().__init__(station_id, parameter = 'level', qualifier = ['Tidal Level'] , measure_type = 'Tidal Level')  

	def calculate_tidal_range(self, date_range : list | None  = None )-> float: 

		'''
		calculate_tidal_range extends the functionality of the TidalLevel class, it calculates 
		the tidal range within the date range specified, if date_range is none
		then the tidal range for the current day is calculated. 

		Inputs: 
			date_range [list] - date range which the tidal range is calculated over 

		Returns: 

			tidal_range [float] - tidal range stored as a float
		'''

		measure_notation = self.measures[0].notation 
		response = self.get_readings(measure_notation=measure_notation, date_range = date_range ) 

		values = [ reading['value'] for reading in response['items']] 
	
		return max(values) - min(values) 


      

