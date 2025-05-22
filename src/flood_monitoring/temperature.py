from .station import station 
import statistics as stats 


class Temperature(station):


	def __init__(self, station_id : str ) -> None :

		super().__init__(station_id, parameter = 'temperature', qualifier = [], measure_type = 'Temperature' ) 


	def average_temp(self, date_range : tuple | None = None ) -> float :

		date_range  = self.validate_date_range(date_range) 

		query = f'https://environment.data.gov.uk/flood-monitoring/data/readings' 

		param = {'parameter' : self.parameter, 
				 'stationReference': self.station_id,
				 'today' : None ,
				 'startdate' : date_range[0], 
				 'enddate' : date_range[1] } 

		response = self.make_request(query) 

		values = [ reading['value'] for reading in response['items']] 

		return round(stats.mean(values), 2 ) 
