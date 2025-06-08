from .station import station 
import pandas as pd 
from io import StringIO

import datetime 

import numpy as np 

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from matplotlib.figure import Figure 
from matplotlib.axes import Axes 

import matplotlib.pyplot as plt 

class Forecast(station):

    def __init__(self):
        pass 

    def load_data(self,
            measure_notation,
            date_range : list| None = None ) -> pd.DataFrame: 

        readings = self.get_readings(measure_notation = measure_notation, 
                                     date_range = date_range, 
                                     csv = True ) 
        
        readings = StringIO(readings)
        readings = pd.read_csv(readings) 

        return  readings 
    

    @staticmethod
    def transform_data(dataframe : pd.DataFrame,
                        lag_features : int,
                        evaluation_split : bool = False, 
                        split_date : str | None  = None, 
                        split_size : int  = 5   ): 
        
        #taking a copy of our dataframe so we arent transforming the original date
        dataframe = dataframe.loc[:, : ]

        dataframe['dateTime64'] = pd.to_datetime(dataframe.dateTime) 
        dataframe.drop(['measure'], inplace = True, axis = 'columns' ) 

        X_columns =  [] 
        for i in range(1, lag_features + 1 ): 
            dataframe[f'lag_{i}'] = dataframe.value.shift(i) 
            X_columns.append(f'lag_{i}' ) 

        dataframe.dropna(inplace = True ) 
        dataframe.sort_values('dateTime', ascending = False , inplace = True ) 

        '''
        Creating a time based split of the dataframe, the default is 
        predicting the last 10 records
        ''' 

        if evaluation_split: 
            train_readings  = dataframe[:-split_size] 
            test_readings = dataframe[-split_size: ] 

            if split_date: 
                split_date = pd.Timestamp(split_date, tz = 'UTC') 
                train_readings = dataframe[dataframe.dateTime64 < split_date ] 
                test_readings = dataframe[dataframe.dateTime64 > split_date ]

            train_y = train_readings['value'].values 
            test_y = test_readings['value'].values 

            test_timestamps = test_readings['dateTime'].values 

            train_x = train_readings[X_columns ].values 

            test_x = np.concatenate(( train_x[0, 1:  ],  [train_y[0 ] ]), axis = -1 ) 
            return train_x, train_y, test_x, test_y , test_timestamps
        
            
        X = dataframe[X_columns ].values 
        y = dataframe['value'].values 

        return X, y 

    def fit(self, X, y ): 
        
        self.model = LinearRegression() 

        self.model.fit(X, y )

        #set a prediction thingy here it has to be done 
    
    def predict(self, x_last : np.ndarray , n_predictions : int) -> np.ndarray: 


        predictions = np.array([]) 

        for pred in range(n_predictions):  

            prediction= self.model.predict([x_last]) 
        
            x_last = np.concatenate( (x_last[1:  ], prediction), axis = 0 )
            
        
            predictions = np.concatenate((predictions,prediction) ) 

        return predictions
    
    @staticmethod
    def timestamps_to_date_str(timestamp):
        datetime_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        
        date_str = datetime_obj.date().strftime('%Y-%m-%d')

        return date_str 
    
    def visualise_predictions(self,
                              predictions: list,
                              ground_truth : list | None ,
                              test_timestamps : list, 
                              measure ) -> tuple[Figure, Axes]: 

        fig, ax = plt.subplots(1, figsize = (7,7)) 
        ax.plot(np.arange(len(predictions)), predictions, label  = 'predictions' )

        '''
        If the ground truth values are provided then they will be plotted alongside 
        the predictions but are an optional input 
        '''

        if isinstance(ground_truth, np.ndarray): 
            ax.plot(np.arange(len(ground_truth)), ground_truth , label = 'ground truth' )

        date_range = [*map(self.timestamps_to_date_str, [test_timestamps[i] for i in [0, -1]]) ] 
        units = self.configure_units(date_range) 

        test_timestamps  = [self.format_date(timestamp, units) for timestamp in test_timestamps] 

        ax.set_xticks( np. arange(len(test_timestamps)),  test_timestamps, rotation = 90 ) 

        ax.set_title(f'predictions for {measure.parameter}')

        ax.set_xlabel('time') 
        ax.set_ylabel(measure.units) 

        fig.legend() 
        return fig, ax
    
    def evaluate_forecast(self,
                         measure,
                         date_range : list | None = None, 
                         split_date  : str | None = None, 
                         split_size : int = 5, 
                         lag_features : int = 3 ): 
    


        date_range = self.validate_date_range(date_range) 
        readings = self.load_data(measure.notation, date_range=date_range) 

        train_x, train_y, test_x, test_y,  test_timestamps = self.transform_data(readings, 
                                                                lag_features=lag_features,
                                                                evaluation_split= True, 
                                                                split_date= split_date, 
                                                                split_size = split_size ) 
        
        self.fit(train_x, train_y) 

        predictions = self.predict(test_x , len(test_y))
        
        fig, ax = self.visualise_predictions(predictions , test_y, test_timestamps,  measure )

        #TODO possibly add code to quantify the accuracy of the predictions, mean squared error etc 

        plt.tight_layout() 



        plt.show(block = True ) 



