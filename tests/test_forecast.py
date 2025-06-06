from flood_monitoring import ForecastStation
import pytest 

from matplotlib.figure import Figure 
from matplotlib.axes import Axes 

import numpy as np 
import pandas as pd 

from io import StringIO 

from sklearn.linear_model import LinearRegression

VALID_ID = 'F1906' 

@pytest.fixture
def valid_obj() -> ForecastStation:

    forecast_station = ForecastStation(VALID_ID) 

    return forecast_station

def test_isinstance(valid_obj : ForecastStation):


    '''
    Double checking that the forecast station has be instantiated correctly 
    '''

    assert isinstance(valid_obj, ForecastStation)

def test_load_data(valid_obj : ForecastStation):

    measure = valid_obj.measures[0] 
    readings = valid_obj.load_data(measure) 

    print(readings)
    assert isinstance(readings, pd.DataFrame) 

'''
using ytest fixture to define a sample dataframe of readings retrieved from the api 
'''

@pytest.fixture
def sample_data():

    sample_data = '''dateTime,measure,value
    2025-06-05T00:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,10.6
    2025-06-05T01:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,10.5
    2025-06-05T02:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,10.6
    2025-06-05T03:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,10.5
    2025-06-05T04:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,10.6
    2025-06-05T05:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,10.6
    2025-06-05T06:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,10.7
    2025-06-05T07:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,11.1
    2025-06-05T08:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,11.0
    2025-06-05T09:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,11.6
    2025-06-05T10:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,13.4
    2025-06-05T11:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,13.5
    2025-06-05T12:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,14.6
    2025-06-05T13:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,12.8
    2025-06-05T14:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,14.7
    2025-06-05T15:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,15.0
    2025-06-05T16:00:00Z,http://environment.data.gov.uk/flood-monitoring/id/measures/1412-temperature-dry_bulb-i-1_h-deg_C,14.5'''

    sample_data = StringIO(sample_data) 
    sample_dataframe = pd.read_csv(sample_data) 

    return sample_dataframe 



def test_transform_data(valid_obj : ForecastStation, sample_data):

    transformed_data = valid_obj.transform_data(dataframe= sample_data,
                                                lag_features=3) 
    
    assert isinstance(transformed_data, tuple ) 

    X, y = transformed_data

    assert isinstance( X, np.ndarray ) 
    assert isinstance(y, np.ndarray ) 

def test_transform_data_evaluation_set(valid_obj : ForecastStation, sample_data):
    
    transformed_data = valid_obj.transform_data(dataframe= sample_data, 
                                                lag_features=3,
                                                evaluation_split = True, 
                                                split_size = 3 ) 
    
    assert isinstance(transformed_data, tuple ) 

    train_x, train_y , test_x, test_y , test_timestamps = transformed_data

    assert isinstance( train_x, np.ndarray ) 
    assert isinstance(train_y, np.ndarray ) 
    assert isinstance( test_x , np.ndarray) 
    assert isinstance( test_y , np.ndarray ) 
    assert isinstance(test_timestamps, np.ndarray) 


def test_visualise_predictions(valid_obj : ForecastStation): 

    predictions = [*range(1,10)]
    ground_truth = [*range(1,10)] 
    test_timestamps = [f'2025-06-0{i}T00:00:00Z' for i in range(1, 10) ] 
    measure = valid_obj.measures[0] 

    fig, ax = valid_obj.visualise_predictions(predictions=predictions,
                                              ground_truth=ground_truth,
                                              test_timestamps=test_timestamps,
                                              measure = measure )
    
    
    assert isinstance(fig, Figure) 
    assert isinstance(ax, Axes )




@pytest.fixture
def sample_training_data(): 

    X = np.random.random((20, 3 )) 
    y = np.random.random((20)) 

    return X, y 

def test_fit_model(valid_obj, sample_training_data): 

    X,y = sample_training_data

    valid_obj.fit(X, y ) 

    #checking if the model object is an instance of linear regression 
    assert isinstance(valid_obj.model, LinearRegression) 

    #checking if the number of coefficients learnt is equal to the dimonsion of training data 

    coefficients = valid_obj.model.coef_

    assert len(coefficients) == 3 




def test_predict(valid_obj, sample_training_data): 


    
