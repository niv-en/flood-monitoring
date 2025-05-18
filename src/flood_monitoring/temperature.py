from .station import station 
import statistics as stats 


class Temperature(station):


	def __init__(self, station_id):

		super().__init__(station_id, parameter = 'temperature', qualifier = [] ) 


	def average_temp(self):

		query = f'https://environment.data.gov.uk/flood-monitoring/data/readings' 

		param = {'parameter' : self.parameter, 'stationReference' : self.station_id, 'today' : None }

		response = self.make_request(query) 

		values = [ reading['value'] for reading in response['items']] 

		return round(stats.mean(values), 2 ) 
