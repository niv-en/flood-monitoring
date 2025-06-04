from flood_monitoring import RiverLevel, RiverFlow, TidalLevel, Temperature 
import pytest 

from matplotlib.figure import Figure 
from matplotlib.axes import Axes 

import numpy as np 


''' 
test_generic will be used to test the methods which are shared between each of the child classes, 
to ensure that each child class is correctly calling the inhertited methods. 
'''

river_flow = RiverFlow('2200TH') 
river_level = RiverLevel('F1906') 
temperature = Temperature('1412') 
tidal_level = TidalLevel('E71524') 


@pytest.mark.parametrize("measure_station_class", [
    river_flow,
    river_level,
    temperature,
    tidal_level
])
def test_inherited_plot_data(measure_station_class): 

    fig, ax = measure_station_class.plot_data() 

    assert isinstance(fig, Figure) 

    assert isinstance(ax, np.ndarray) or isinstance(ax, Axes)


@pytest.mark.parametrize("measure_station_class", [
    river_flow,
    river_level,
    temperature,
    tidal_level
])
def test_inherited_plot_data_range(measure_station_class): 

    fig, ax = measure_station_class.plot_data() 

    assert isinstance(fig, Figure) 

    assert isinstance(ax, np.ndarray) or isinstance(ax, Axes)


@pytest.mark.parametrize("measure_station_class", [
    river_flow,
    river_level,
    temperature,
    tidal_level
])
def test_inherited_get_least_measurement(measure_station_class): 

    latest_measurement = measure_station_class.get_latest_measurement() 

    assert isinstance(latest_measurement, dict ) 