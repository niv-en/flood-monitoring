from .station import station 
import pandas as pd 
from io import StringIO

import numpy as np 

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from matplotlib.figure import Figure 
from matplotlib.axes import Axes 


import matplotlib.pyplot as plt 

class ForecastStation(station):

    def __init__(self):


        
        pass
        
        
    def load_transform_data(self, notation : str , 
            date_range : list| None, 
            split_date : str, 
            lag_features : int = 5, 
            period : str | None = None ) -> tuple[np.ndarray,
                                                    np.ndarray,
                                                    np.ndarray,
                                                    np.ndarray,
                                                    np.ndarray]:  
        

        readings = self.get_readings(measure_notation = notation,
                                     date_range = date_range, 
                                     csv = True ) 


        readings = StringIO(readings)
        readings = pd.read_csv(readings) 

        readings['dateTime'] = pd.to_datetime(readings.dateTime) 
        readings.drop(['measure'], inplace = True, axis = 'columns' ) 

        for i in range(1, lag_features + 1 ): 

            readings[f'lag_{i}'] = readings.value.shift(i) 


        readings.dropna(inplace = True ) 
        readings.sort_values('dateTime', ascending = False , inplace = True ) 


        '''
        Creating a time based split of the dataframe 
        ''' 

        split_date = pd.Timestamp(split_date, tz = 'UTC') 

        train_readings = readings[readings.dateTime < split_date ] 
        test_readings = readings[readings.dateTime > split_date ]


        train_y = train_readings['value'].values 
        test_y = test_readings['value'].values 

        X_columns = [ f'lag_{i}' for i in range(1, lag_features + 1 ) ] 


        train_x = train_readings[ X_columns ].values 
        test_x = train_readings[X_columns].values 

        x_last = np.concatenate(( train_x[0, 1:  ],  [train_y[0 ] ]), axis = -1 ) 

        

        return train_x, test_x, train_y, test_y , x_last 
    

    def fit(self, X, y ): 
        
        self.model = LinearRegression() 
   
        self.model.fit(X, y )
        self.test = 1 

    
    def predict(self, x_last : np.ndarray , n_predictions : int) -> np.ndarray: 


        predictions = np.array([]) 

        for pred in range(n_predictions):  

            prediction= self.model.predict([x_last]) 
        
            x_last = np.concatenate( (x_last[1:  ], prediction), axis = 0 )
            
            predictions = np.concatenate((predictions,prediction) ) 

        return predictions 
    

    def visualise_predictions(self, 
                              predictions: list,
                              ground_truth : list,
                              notation : str ) -> tuple[Figure, Axes]: 
        

        fig, ax = plt.subplots(1, figsize = (7,7)) 
        ax.plot(np.arange(len(predictions)), predictions, label  = 'predictions' ) 

        ax.plot(np.arange(len(ground_truth)), ground_truth , label = 'ground truth' ) 

        ax.set_title(f'predictions for {notation}')

        ax.set_xlabel('time') 
        ax.set_ylabel('add something later') 

        fig.legend() 
        return fig, ax 

    


