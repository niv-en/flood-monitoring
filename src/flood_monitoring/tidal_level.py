from .station import station 
import datetime 

class TidalLevel(station):

	def __init__(self, station_id): 

		super().__init__(station_id, parameter = 'level', qualifier = ['Tidal Level'] , measure_type = 'Tidal Level')  


	def calculate_tidal_range(self, date_range = None ): 

		date_range  = self.convert_date_range(date_range) 
		
		query = f'https://environment.data.gov.uk/flood-monitoring/data/readings' 

		params = {'parameter' : self.parameter,
				  'qualifier' : self.qualifier[0] ,
				  'stationReference' : self.station_id,
				  'startdate' : date_range[0], 
				  'enddate' : date_range[1] } 

		response = self.make_request(query, params = params ) 


		values = [ reading['value'] for reading in response['items'] ]

		return round(max(values) - min(values), 2) 




if __name__ == '__main__': 


	tidal_level_station = 'F1906'

	test = TidalLevel(tidal_level_station) 

	fig, ax = test.plot_data_range()

	fig.tight_layout() 

	plt.show(block = True ) 