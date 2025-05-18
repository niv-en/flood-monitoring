import requests 
import datetime 

import pprint 

import matplotlib.pyplot as plt 


from matplotlib.figure import Figure
from matplotlib.axes import Axes 

from abc import ABC


''' station class inheriting from abstract baseclass as it is not meant to be called invividually 
	but rather inherited by each of the station type classes ''' 


class station(ABC):

	''' initialising two staticmethods which will be used by the class
		but do not require any of its attributes ''' 


	@staticmethod 
	def format_date(date, frmt):

		date = datetime.datetime.strptime(date , '%Y-%m-%dT%H:%M:%SZ')
		return date.strftime(frmt )  

	#used to call the API using python requests package, passing a dictionary which stores query parameters 
	@staticmethod
	def make_request( query : str , params : dict  = {} ) -> dict :

		response = requests.get(query, params = params) 
		if response.status_code != 200: 

			raise Exception(f'Invalid Query, status code : {response.status_code}')

		return response.json() 

	#setting the position of our station through querying for metdata 
	def set_position(self) -> None: 

		query = 'https://environment.data.gov.uk/flood-monitoring/id/stations'
		params = {'stationReference' : self.station_id}

		response = self.make_request(query, params) 


		latitude, longitude  = ( response['items'][0][orientation] for orientation in ['lat', 'long' ] ) 
		
		''' setting both latitude and longitude as using the dunder method so that both cannot
			 be modified as they do not have setter methods '''
		self.__lat  = latitude
		self.__long = longitude 

	@property
	def latitude(self) -> float:
		return self.__lat

	@property 
	def longitude(self) -> float: 
		return self.__long 


	def set_measures(self) -> None: 

		#initialing our set of measures, the associated data and timestamps 

		measures = [] 
		data = []
		timestamps = []

		query = 'https://environment.data.gov.uk/flood-monitoring/id/measures'
		params = {'stationReference' : self.station_id } 

		response_measures = self.make_request(query, params )['items'] 

		'''
		Looping through response_measures so in the edge case where it is only one single dictionary rather than a list, 
		we would like to convert it '''
		if isinstance(response_measures, dict ): 

			response_measures = [response_measures] 


		for measure in response_measures:

			valid_measure = True 

			if self.parameter: 
				valid_measure =  (measure['parameter'] == self.parameter   ) 

			if self.qualifier:  
				valid_measure = ( measure['parameter'] == self.parameter and measure['qualifier'] in self.qualifier ) 


			if valid_measure: 

				measure_info = {'qualifier' : measure.get('qualifier'), 
								'units' : measure.get('unitName'), 
								'value_type' : measure.get('valueType'),
								'notation' : measure.get('notation')  }

				latest_reading = measure.get('latestReading', {} ) 

				measures.append(measure_info)
				data.append(latest_reading.get('value')) 
				timestamps.append(latest_reading.get('dateTime')) 

	
		if len(measures) == 0: 

			raise Exception('Incorrect StationID No measurments found relating to the station type')


		self.measures = measures
		self.data = data 
		self.timestamps = timestamps 



	def set_in_flood(self) -> None:

		query = f'https://environment.data.gov.uk/flood-monitoring/id/floods' 
		params = {'lat' : self.__lat , 'long' : self.__long , 'dist' : 0 , 'min-severity' : 1 }

		response = self.make_request(query, params) 

		# Once again und
		self.__in_flood = False 
		if response['items'] != []: 
			self.__in_flood = True 

	@property
	def in_flood(self):
		return self.__in_flood 

	def __init__(self, station_id : str , parameter :str = '' , qualifier : list[str] | None = None ): 


		self.station_id = station_id 
		self.parameter = parameter 
		self.qualifier = qualifier 


		self.set_position() 

		self.set_in_flood() 

		self.set_measures() 


	def get_latest_measurement(self) -> dict:

		''' Returns a dictionary which stores the latest measurements from a particular station'''

		latest_measurements = {}
		for measure in self.measures: 

			query = f'https://environment.data.gov.uk/flood-monitoring/id/measures/{measure["notation"]}/readings?latest'

			result = self.make_request(query )

			if result['items'] == []:
				#returning None if latest reading is not available for a particular mesurement 
				value = None 
			else:
				value = result['items'][0].get('value' ) 

			latest_measurements[measure["qualifier"] ] = value 

		return latest_measurements


	def plot_data(self) -> tuple[Figure, list[Axes] ] : 


		unique_measures = set( measure['units'] for measure in self.measures)

		fig, ax = plt.subplots(len(unique_measures)) 

		if len(unique_measures) == 1: 
			ax = [ax]  

		axes_mapping = { measure : idx for idx, measure in enumerate(unique_measures)}

		for measure_dict, value, time in zip(self.measures, self.data , self.timestamps): 


			if value == None or time == None: 
				continue 

			axes = axes_mapping[measure_dict['units'] ] 

			ax[axes].bar( f"{measure_dict['qualifier']} " , value, width = 0.2 ) 

			if ax[axes].get_xlabel() == '':


				ax[axes].set_ylabel(measure_dict['units'])   


				ax[axes].set_title(f'{self.parameter}@{self.format_date(time, "%H:%M" )}') 


		plt.suptitle(f'station : {self.station_id}') 
		plt.xlabel('(qualifier')

		plt.tight_layout() 


		return fig, ax

	''' Plots all of the measurements associated to given station over the date range specified, 
		if no range is specified then it will plot all data from the current day '''


	''' 
	Staticmethod which doesnt interact with the class itself, but instead calculates the most appropriate 
	units from a given date range, E.g if the date range specified is from the 1st of setember to the 13th
	the graph units will show the date, hour, minute etc. 
	'''

	@staticmethod
	def configure_units(date_range):

		#some code here to double check dataranges

		
		label_format = '' 

		try: 
			date_range = [ (lambda x : datetime.datetime.strptime(x, '%Y-%m-%d'))(date) for date in date_range ]
		except: 
			raise Exception('Invalid Date Format') 

		if date_range[0] > date_range[1]: 
			raise Exception('End date before start date') 
			
		units_of_time = ['year', 'month', 'day' ] 
		datetime_formats = ['%Y-', '%m-', '%d ' ] 

		#flag determines if we have found the order of magnitude where the two dates align e.g same year, month, day 

		flag = False

		for frmt, unit in zip(datetime_formats, units_of_time): 

			if getattr(date_range[0], unit) != getattr(date_range[1] , unit ):
				flag = True 

			if flag == True:
				label_format += frmt 


		label_format += '%H:%M'

		return label_format 

	def plot_data_range(self, date_range : list[str] | None   = None  ) -> tuple[Figure, list[Axes]]:

		fig, ax = plt.subplots(len(self.measures)) 

		#converting axes object to a list in the case we only have one axes so we can still iterate through it 
		ax = [ax] if len(self.measures) == 1 else  ax 

		if not date_range:
			current_date = datetime.datetime.now().date().strftime('%Y-%m-%d')
			date_range = (current_date, current_date )

		params = {'startdate' : date_range[0] , 'enddate' : date_range[1] } 
		
		label_format = self.configure_units(date_range)

		for idx, measure in enumerate(self.measures):
			query = f'https://environment.data.gov.uk/flood-monitoring/id/measures/{measure["notation"]}/readings'
			response = self.make_request(query, params )  

			values = [ reading['value'] for reading in response['items'] ] 
			times = [ reading['dateTime'] for reading in response['items'] ] 

			ax[idx].plot(times, values )

			step_size =   int((len(times) / 10) ) 

			if len(times) < 10: 
				step_size = 1

			labels = [ self.format_date(date, label_format) for date in times[::step_size] ] 

			ax[idx].set_xticks([*range(0, len(times), step_size ) ],labels  , rotation = 90 ) 

			ax[idx].set_title(f'{measure["qualifier"]}' ) 

			ax[idx].set_ylabel(measure["units"]) 

		fig.suptitle(self.parameter) 
		fig.supxlabel('time')

		return fig, ax 



if __name__ == '__main__': 


	tidal_level_station = '2928TH'

	test = station(tidal_level_station) 

	print(test.measures ) 