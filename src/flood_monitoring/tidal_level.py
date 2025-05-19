from .station import station 

class TidalLevel(station):

	def __init__(self, station_id): 

		print('hello') 


		super().__init__(station_id, parameter = 'level', qualifier = ['Tidal Level'] , measure_type = 'Tidal Level')  


	def calculate_tidal_range(self): 

		query = f'https://environment.data.gov.uk/flood-monitoring/data/readings?today' 

		params = {'parameter' : self.parameter, 'qualifier' : self.qualifier[0] , 'stationReference' : self.station_id} 

		response = self.make_request(query, params = params ) 

		values = [ reading['value'] for reading in response['items'] ]

		return round(max(values) - min(values), 2) 




if __name__ == '__main__': 


	tidal_level_station = 'F1906'

	test = TidalLevel(tidal_level_station) 

	fig, ax = test.plot_data_range()

	fig.tight_layout() 

	plt.show(block = True ) 