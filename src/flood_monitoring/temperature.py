from .station import station 


class Temperature(station):

	'''
	Temperaure station which inherits from the station class

	'''


	def __init__(self, station_id : str ) -> None :

		super().__init__(station_id, parameter = 'temperature', qualifier = [], measure_type = 'Temperature' ) 


	def average_temp(self, date_range : tuple | None = None ) -> float :

		'''
		Calculates the average temperature within the date range, if date_range is none
		then the average temperature over the day is calculted. 

		Inputs: 
			date_range [list] - date range which the temperature is calculated over 

		Returns: 

			temperature [float] - temperature which is stored as float 
		
		'''

		measure_notation = self.measures[0].notation

		response = self.get_readings(measure_notation= measure_notation, date_range=date_range ) 

		values = [ reading['value'] for reading in response['items']] 

		return sum(values) / len(values)  