import requests 
import datetime 

import pprint 

import matplotlib.pyplot as plt 


from matplotlib.figure import Figure
from matplotlib.axes import Axes 

from abc import ABC

import numpy as np 


#TODO change our invalid dis are spotted in the code to ensure that it is isnt silent 
class station(ABC):


	''' station class inheriting from abstract baseclass as it is not meant to be called invividually 
		but rather inherited by each of the station type classes ''' 


	@staticmethod 
	def format_date(date, frmt):

		date = datetime.datetime.strptime(date , '%Y-%m-%dT%H:%M:%SZ')

		return date.strftime(frmt )  

	@staticmethod
	def make_request( query : str , params : dict  = {} ) -> dict :

		'''
		Helper function used to make requets usign the pythons request package, 
		takes in 
		'''

		response = requests.get(query, params = params) 
		if response.status_code != 200: 

			raise Exception(f'Invalid Query, status code : {response.status_code}')

		return response.json() 

	@staticmethod
	def validate_date_range(date_range : tuple , return_str : bool = True  ): 

		''' 
		If not date_range is None, then no format/order checks are required as the 
		date_range is replaced with the current date in the correct format 

		'''

		if date_range == None: 
			current_date = datetime.datetime.now().date().strftime('%Y-%m-%d') 
			date_range =  (current_date, current_date )


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




	#setting the position of our station through querying for metdata 
	def set_position(self) -> None: 

		query = 'https://environment.data.gov.uk/flood-monitoring/id/stations'
		params = {'stationReference' : self.station_id}

		response = self.make_request(query, params)['items'] 

		''' 
		Given that items stores the metadata for a given station if it is an empty 
		list then the station id is likely invalid so we will raise an exception 
		
		'''

		if response == []: 
			raise Exception('Incorrect Station ID')
		
		latitude, longitude  = ( response[0][orientation] for orientation in ['lat', 'long' ] ) 
		
		''' setting both latitude and longitude as using the dunder method so that both cannot
			 be modified as they do not have setter methods '''
		
		self.__lat  = latitude
		self.__long = longitude 


	'''
	using @property methods so that both the latitude and longitude of a station can be accessed
	but not directly modified by users 
	
	'''

	@property
	def latitude(self) -> float:
		return self.__lat

	@property 
	def longitude(self) -> float: 
		return self.__long 


	def set_measures(self) -> None: 

		'''
		Function which is used to retrieve all measures which are available for a given station id and then
		filter those for particular parameters, qualifiers desired. this functionality is mainly impleted to allow
		for the initialisation of specific measure stations which only measure the TidalLevel for example. 
		'''

		measures = [] 
		data = []
		timestamps = []

		query = 'https://environment.data.gov.uk/flood-monitoring/id/measures'
		params = {'stationReference' : self.station_id } 

		response_measures = self.make_request(query, params )['items'] 

		'''
		Converting the reponse object into a list in the case only one measure was returned as we wish to loop through
		our results and assign them as attributes to our object
		'''

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

	def __init__(self, station_id : str , 
					   parameter :str = '' , 
					   qualifier : list[str] | None = None,
					   measure_type: str = '' ): 
		
		#setting stations parameter
		self.station_id = station_id 
		self.parameter = parameter 
		self.qualifier = qualifier 
		self.measure_type = measure_type 

		#setting the position 
		self.set_position() 

		#setting in flood using the stations position set with the set_position call 
		self.set_in_flood() 

		#setting measures avaiable at the station + meeting any requirements defined by the parameters and qualifiers 
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

			latest_measurements[measure["notation"] ] = value 

		return latest_measurements


	def plot_data(self) -> tuple[Figure, list[Axes] ] : 

		''' 
		This function will plot all of current values stored the measures, data, timestamps attributes of 
		our object using matplotlib
		'''


		''' 
		First we will filtered through the current values stored as attributes and filter 
		for any measuers will missing values and these will be excluded from our plot 

		'''
		current_measures  = [ *zip(self.measures, self.data , self.timestamps) ] 
		mask = [*map( all , current_measures ) ] 
		filtered_measures = [measure for  measure, flag in zip(current_measures, mask) if flag  ]


		'''
		Iterating through each of the measures with values and plotting the results. 

		'''

		if len(filtered_measures) == 0: 

			raise Exception('No Readings data available for station at the point of initialisation ')


		fig, ax = plt.subplots(len(filtered_measures)) 

		ax = np.array([ax]) if len(filtered_measures) == 1 else  ax 


		for idx, ( measure_dict, value, time ) in enumerate(filtered_measures):


			if value == None or time == None: 
				continue 

			ax[idx].bar( self.format_date(time, "%H:%M" ) , value, width = 0.2 )

			ax[idx].set_ylabel(measure_dict['units'])   

			ax[idx].set_xlabel('time') 

			ax[idx].set_title(f'{measure_dict["notation"]}') 


		plt.suptitle(f'{self.measure_type}@{self.station_id}') 


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


	def plot_data_range(self, date_range : tuple[str] | None   = None  ) -> tuple[Figure, list[Axes]]:

		''' 
		plot_date_range will plot all values for all of the measures for a particular measure station between a user
		specified date_range provided they are available. By default if no date range is specified then all readings
		from the current day will be requested from the API and plotted. 
		'''


		'''
		First we will request all of the readings from the flood monitoring API so we can filter from measures with no available
		readings and then plot all available readings. 
		'''


		available_readings = []

		'''
		Applying the valid_date_range static method to validate and transform date range
		'''
		date_range = self.validate_date_range(date_range, return_str = True ) 

		label_format = self.configure_units(date_range)



		''' 
		First we are iterating through all measures attached to the class and retrieving all of the readings
		within the date range specified, if the readings are none for particular measures then the readings are
		ignored 
		
		'''

		params = {'startdate' : date_range[0] , 'enddate' : date_range[1] } 
		for idx, measure in enumerate(self.measures):

			query = f'https://environment.data.gov.uk/flood-monitoring/id/measures/{measure["notation"]}/readings'
			response = self.make_request(query, params )  

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

			ax[idx].set_title(f'{measure_reading["measure"]["notation"]}' ) 

			ax[idx].set_ylabel(measure_reading["measure"]["units"]) 


		fig.suptitle(f'{self.measure_type}@{self.station_id}') 
		fig.supxlabel('time')

		return fig, ax 