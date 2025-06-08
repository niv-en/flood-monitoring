
from abc import ABC

import requests 
import datetime 

import matplotlib.pyplot as plt 
from matplotlib.figure import Figure
from matplotlib.axes import Axes 

from enum import Flag 
from dataclasses import dataclass 

import numpy as np 

import pprint 


class station(ABC):

	''' station class inheriting from abstract base class as it is not meant to be called invividually 
		but rather inherited by each of the station type classes
	'''


	'''
	Defining helper function as staticmethods, as they do not interact with the class attributes
	themseves and are encapsulated within the station class. 
	'''

	@staticmethod 
	def format_date(date : str , frmt : str) -> str:

		'''
		format_date: formats date strings returned by the API into datetime objects,
		with are then reformatted with the string format passed to the function
		
		'''
		date_ = datetime.datetime.strptime(date , '%Y-%m-%dT%H:%M:%SZ')

		return date_.strftime(frmt )
	
	@staticmethod
	def convert_to_datetime(date: str):
		return datetime.datetime.strptime(date , '%Y-%m-%dT%H:%M:%SZ')


	@staticmethod
	def make_request( query : str , params : dict  = {} , return_json = True ) -> dict :


		'''
		Function to send and process a requests using the python requests library.
		Query string and parameter dictionary are provided to the function. 
		'''

		base_url = 'https://environment.data.gov.uk/flood-monitoring/' 
		query = base_url + query 

		response = requests.get(query, params = params) 
		if response.status_code != 200: 
			raise Exception(f'Invalid Query, status code : {response.status_code}')
		
		if return_json: 
			return response.json() 
		
		return response.text

	@staticmethod
	def validate_date_range(date_range : list | None , return_str : bool = True  ) -> list[datetime.datetime] | None: 

		''' 
		If date_range is None, then no format/order checks are required as the
		date_range is replaced with the current date in the correct format 

		'''

		if date_range == None: 
			current_date = datetime.datetime.now().date().strftime('%Y-%m-%d') 
			date_range =  [current_date, current_date ]


		'''
		If a date_range is not None, then check the format of the dates as well as the order 
		'''

		try: 
			date_range_converted = [ (lambda x : datetime.datetime.strptime(x, '%Y-%m-%d'))(date) for date in date_range ]
		except: 
			raise Exception('Invalid Date Format') 

		if date_range_converted[0] > date_range_converted[1]: 
			raise Exception('End date before start date') 

		'''
		if no execptions are raised i.e the date range was valid then either the string/datetime objects range 
		is passed back depending on the return_str parameter

		'''
		if return_str: 
			return date_range 

		return date_range_converted
	


	@staticmethod
	def configure_units(date_range):

		''' 
		Function calculates the most appropriate units from a given date range, E.g if the date range s
		pecified is from the 1st of setember to the 13th the graph units will show the date, hour, minute etc. 
		'''

		date_range = [ (lambda x : datetime.datetime.strptime(x, '%Y-%m-%d'))(date) for date in date_range ]

		label_format = '' 
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
	
	def get_station_metadata(self) -> dict: 

		query = 'id/stations' 
		params = {'stationReference' : self.station_id} 

		response = self.make_request(query, params)['items']

		# if items is empty its likely that the stationID Queried for doesnt exist 	

		if response == []: 
			raise Exception('Incorrect Station ID') 
		
		return response
	
	@staticmethod
	def parse_position(response : str) -> tuple:  

		latitude, longitude  = ( response[0][orientation] for orientation in ['lat', 'long' ] ) 
		
		''' setting both latitude and longitude as using the dunder method so that both cannot
			 be modified as they do not have setter methods '''
		
		return (latitude , longitude ) 
	
	@staticmethod
	def parse_metadata(response : str  ) -> tuple:

		pass 
	
	@dataclass 
	class measure_dclass:

		notation : str
		parameter : str 
		qualifier : str
		units : str
		value_type : str

		def __str__(self) -> str:
			return f'\n----Measure Summary----\n\nMeasure ID : {self.notation}\nParameter : {self.parameter}\nQualifier : {self.qualifier}\nUnits : {self.units}\nValue Type : {self.value_type}'
		

	def set_measures(self) -> None:  

		'''
		set_meaures retrives all measures which are available for a given station id and then filters for the
		parameters and qualifiers specified for a particular station type. E.g. this will be used to initialise a 
		TidalLevel station by specifying 'Tidal Level' as the parameter. 
		'''

		'''
		Converting the reponse object into a list in the case only one measure was returned as we wish to loop through
		each of our measures to assign them to our station object
		'''

		query = 'id/measures'
		params = {'stationReference' : self.station_id} 

		response = self.make_request(query = query , params = params  )['items']

		# pprint.pprint(response) 

		measures, data, timestamps = [], [] , [] 

		for measure in response: 

			valid_measure = True 

			if self.parameter: 
				valid_measure =  (measure['parameter'] == self.parameter   ) 
			if self.qualifier:  
				valid_measure = ( measure['parameter'] == self.parameter and measure['qualifier'] in self.qualifier )

			if valid_measure:

				measure_info_ = measure_dclass(
	
					notation = measure.get('notation', ''),
					parameter = measure.get('parameter', ''),
					qualifier = measure.get('qualifier',''),
					units = measure.get('unitName', ''),
					value_type= measure.get('ValueType','') 
				)

				latest_reading = measure.get('latestReading', {} ) 

				measures.append(measure_info_)
				data.append(latest_reading.get('value')) 
				timestamps.append(latest_reading.get('dateTime')) 



		'''
		if no measures are returned its likely that the parameters and qualifiers supplied didnt match any
		measures at the station
		'''	

		if len(measures) == 0: 
			raise Exception('Incorrect StationID No measurments found relating to the station type')

		self.measures = measures 
		self.data = data
		self.timestamps = timestamps 




	def __init__(self, station_id : str , 
					   parameter :str = '' , 
					   qualifier : list[str] | None = None,
					   measure_type: str = '' ): 
		
		#setting stations parameter
		self.station_id = station_id 
		self.parameter = parameter 
		self.qualifier = qualifier 
		self.measure_type = measure_type 

		response = self.get_station_metadata() 

		lat,long = self.parse_position(response) 
		self.__lat = lat 
		self.__long = long 

		# pprint.pprint(response) 
		self.set_measures() 



	'''
	using @property methods so that both the latitude and longitude of a station can be accessed
	but not directly modified by users 
	'''

	def __str__(self) -> str: 

		return f'\n----Station Summary----\n\nStation Type : {self.measure_type}\nStation ID : {self.station_id}\nLocation : {(self.__lat, self.__long)}\n\n-----Summary Ended-----\n'

	@property
	def latitude(self) -> float:
		return self.__lat

	@property 
	def longitude(self) -> float: 
		return self.__long 
	

	def get_readings(self,
				measure_notation : str,
				date_range : list[datetime.datetime] | None  = None, 
				limit : int | None = None, 
				csv : bool =  False) -> dict | str: 
		
		'''
		Creating a get readings helper funciton, which returns readings for a particular measure
		provided a date_range and a record limit. Also with the option to return results as a csv for analysis 

		Inputs: 

			measure_notation [str] - particular measure you wish to retrieve readings for 
			date_range [list] - range of dates which you wish to retreive the readings for 
			limit [int] - maximum number of records you would like returned 
			csv [bool] - if True will return results of query in csv format 

		Output: 

			result [dict | str] - returns results as either a JSON object or a csv string. 
		'''

		params= {}
		query = f'id/measures/{measure_notation}/readings'
		return_json = True 

		if csv: 
			query = f'id/measures/{measure_notation}/readings.csv'
			return_json = False 

		if limit: 
			params['_limit'] = limit 

		date_range_= self.validate_date_range(date_range, return_str = True )

		params['startdate'] = date_range_[0]
		params['enddate'] = date_range_[1] 	

		result = self.make_request(query, params , return_json ) 

		return result 

	def get_latest_measurement(self, limit : int = 1 ) -> dict:

		''' Returns a dictionary which stores the latest measurements from a particular station'''

		latest_measurements = {}

		for measure in self.measures: 

			measure_notation = measure.notation

			try:
				reading = self.get_readings(measure_notation, limit = 1 )['items'][0]['value'] 
		
			except: 
				reading = None 

			latest_measurements[measure_notation] = reading

		return latest_measurements
	

	def plot_data(self) -> tuple[Figure, np.ndarray ]: 

		'''

		plot_date will plot all values for all of the measures for a particular measure station between a user
		specified date_range provided they are available. By default if no date range is specified then all readings
		from the current day will be requested from the API and plotted. 

		
		Inputs:
			date_range [list] - date range to plot measures over 

		Returns: 

			(fig, ax) - Returns fig, ax tuple which stores our plot 

		'''
		current_measures  = [ *zip(self.measures, self.data , self.timestamps) ] 
		mask = [*map( all , current_measures ) ] 
		filtered_measures = [measure for  measure, flag in zip(current_measures, mask) if flag  ]

		if len(filtered_measures) == 0: 
			raise Exception('No Readings data available for station at the point of initialisation ')


		fig, ax = plt.subplots(len(filtered_measures)) 

		ax = np.array([ax]) if len(filtered_measures) == 1 else  ax 

		# Iterating through each of the measures with values and plotting the results. 
		for idx, ( measure, value, time ) in enumerate(filtered_measures):


			if value == None or time == None: 
				continue 

			ax[idx].bar( self.format_date(time, "%H:%M" ) , value, width = 0.2 )

			ax[idx].set_ylabel(measure.units)   

			ax[idx].set_xlabel('time') 

			ax[idx].set_title(f'{measure.notation}') 


		plt.suptitle(f'{self.measure_type}@{self.station_id}') 
		plt.tight_layout() 

		return (fig, ax )

	def plot_data_range(self, date_range : list | None = None  ) -> tuple[Figure, np.ndarray]:

		''' 
		plot_date_range will plot all values for all of the measures for a particular measure station between a user
		specified date_range provided they are available. By default if no date range is specified then all readings
		from the current day will be requested from the API and plotted. 

		
		Inputs:
			date_range [list] - date range to plot measures over 

		Returns: 

			(fig, ax) - Returns fig, ax tuple which stores our plot 

		'''


		available_readings = []

	
		#Applying the valid_date_range static method to validate and transform date range
		date_range = self.validate_date_range(date_range, return_str = True ) 

		#calculating the correct unit required given our date range
		label_format = self.configure_units(date_range)

		''' 
		First we are iterating through all measures attached to the class and retrieving all of the readings
		within the date range specified, if the readings are none for particular measures then the readings are
		ignored 
		
		'''
		for idx, measure in enumerate(self.measures):

			measure_notation = measure.notation
			response = self.get_readings(measure_notation= measure_notation, date_range = date_range)

			values = [ reading['value'] for reading in response['items'] ] 
			times = [ reading['dateTime'] for reading in response['items'] ]

			#if both values and times are avaialble for a given measure append to available readings
			if values != [] and times != []:

				available_readings.append({'measure' : measure , 'values' : values, 'times' : times  } ) 
		

		''' In the case that there are no readings available for any of an objects methods
		then we wiill raise the following error '''

		if len(available_readings) == 0:

			raise Exception('No Readings data available for station currently')

		'''
		Creating as many subplots as available readings and looping through our available readings and plotting
		them all 
		
		'''
		fig, ax = plt.subplots(len(available_readings)) 

		
		''' given that we want to index our list of axes we will cast it to an array incase 
		it happens to be a single axis '''

		ax = np.array([ax]) if len(available_readings) == 1 else  ax 

		for idx, measure_reading in enumerate(available_readings): 

			times = measure_reading['times']
			values = measure_reading['values']

			ax[idx].plot(times, values  )

			step_size =   int((len(times) / 10) ) 

			if len(times) < 10: 
				step_size = 1


			labels = [ self.format_date(date, label_format) for date in times[::step_size] ] 


			ax[idx].set_xticks([*range(0, len(times), step_size ) ],labels  , rotation = 90 ) 

			ax[idx].set_title(f'{measure_reading["measure"].notation}' ) 

			ax[idx].set_ylabel(measure_reading["measure"].units) 


		fig.suptitle(f'{self.measure_type}@{self.station_id}') 
		fig.supxlabel('time')

		return fig, ax 