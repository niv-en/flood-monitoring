from .station import station 

class Temperature(station):

	'''
	Temperaure station which inherits from the station class

	'''

	def __init__(self, station_id : str ) -> None :

		'''
		initialising Temperature station by passing 'temperature' as a parameter and setting measure_type to 'Temperature'
		'''

		super().__init__(station_id, parameter = 'temperature', qualifier = [], measure_type = 'Temperature' ) 


	def average_temp(self, date_range : list | None = None ) -> float :

		'''
		Calculates the average temperature within the date range, if date_range is none
		then the average temperature over the current day calculted. This method extends 
		the functionality of the base station class 

		Inputs: 
			date_range [list] - date range which the temperature is calculated over 

		Returns: 

			average temperature [float] - average temperature over the date range specified
		
		'''


		measure_notation = self.measures[0].notation

		response = self.get_readings(measure_notation= measure_notation, date_range=date_range ) 

		values = [ reading['value'] for reading in response['items']] 

		return sum(values) / len(values)  