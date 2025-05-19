from .station import station 



class RiverLevel(station):

	def __init__(self, station_id): 

		super().__init__(station_id, parameter = 'level', qualifier = ['Stage', 'Downstream Stage', 'Height' ], measure_type = 'River Level'  ) 


if __name__ == '__main__': 
	
    river_level_station = '1491TH'
	
    RiverLevelStation = RiverLevel(river_level_station) 
	

    fig, ax = RiverLevelStation.plot_data_range() 
    fig.tight_layout() 
    plt.show(block = True ) 
