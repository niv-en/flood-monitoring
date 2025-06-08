from .station import FloodMonitoringMixin, station 
import pandas as pd 
from io import StringIO

import datetime 

import numpy as np 

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

from matplotlib.figure import Figure 
from matplotlib.axes import Axes 

import matplotlib.pyplot as plt 

class Forecast(FloodMonitoringMixin):

    def __init__(self):

        '''
        Forecast station requires no initialisation
        '''
        pass 

    def load_data(self,
            measure_notation : str, 
            date_range : list| None = None ) -> pd.DataFrame: 
        
        '''method which utilises get_readings method to transform the readings for the measure specified
        into a dataframe using stringIO '''

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
                        split_size : int  = 5   ) -> tuple: 
        
        '''
        Transforms the dataframe which stores the measure readings into training/testing arrays which are then
        used to fit our Linear Regression model to. 

        Inputs: 

            dataframe [pd.DataFrame] - DataFrame storing the readings retrieved from load_data
            lag_features [int]       - Defines the number of lag features which should be created 
            evaluation_split [bool]  - Boolean flag defining whether or not the arrays should be split into training and testing sets 
            split_date [str]         - Optional parameter if evaluation_split is True, split_date defines point where the train/test datasets are split
            split_size [int]         - if evaluation_split is True, split_size defines how many of the last n values should be placed in the test set . 
                                       An alternative to split_date which allows you to create a test split of a particular size. 

        Output: 

            if evaluation_split is False
            
                X [np.ndarray] - array storing the feature matrix 
                y [np.ndarray] - array storing the target variable 

            if evaluation_split is True

                train_x [np.ndarray]         -  array storing the feature matrix for the training set
                train_y [np.ndarray]         -  array storing the target variable for the training set 
                test_x  [np.ndarray]         -  array stores the last n observations in the trainig set, defined by lag_features 
                test_y  [np.ndarray]         -  array storing the target variable for the test set 
                test_timestamps [np.ndarray] -  array storing the timestamps of the values in test_y 

        '''
        
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


        if evaluation_split: 


            '''
            If evaluation_split is True and neither split_date or split_size are specified then the train/test splits will be created
            using split_size with a value of 5. 
            '''

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

        '''
        if evaluation split is False then simply the feature matrix and target array will be returned. 
        '''
            
        X = dataframe[X_columns ].values 
        y = dataframe['value'].values 

        return X, y 

    def fit(self, 
            X : np.ndarray,
            y : np.ndarray) -> None: 
        
        '''
        instantiates a linerRegression model and fits to the data. 
        '''
        
        self.model = LinearRegression() 

        self.model.fit(X, y )
    
    def predict(self,
                x_last : np.ndarray,
                n_predictions : int) -> np.ndarray: 
        
        '''
        Autoregressively produces predictions based on the values stored in x_last, where the previous predictions are
        fed into future predictions until we have reached the number of predictions defined by n_predictions. 
        '''

        predictions = np.array([]) 

        for _ in range(n_predictions):  

            prediction= self.model.predict([x_last]) 
        
            x_last = np.concatenate( (x_last[1:  ], prediction), axis = 0 )
            
        
            predictions = np.concatenate((predictions,prediction) ) 

        return predictions
    
    @staticmethod
    def timestamps_to_date_str(timestamp : str) -> str:

        '''
        static method to convert the timestamp object into its date in string format which can later be used by other functions. 
        '''
        datetime_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        
        date_str = datetime_obj.date().strftime('%Y-%m-%d')

        return date_str 
    

    @staticmethod
    def compute_metrics(predictions : np.ndarray,
                        ground_truth : np.ndarray) -> dict:
        
        '''
        static method to compute the Mean Squared Error and Mean Absolute Error based of a list of predictions and ground truth values,
        results are returned in dictionary format. 
        '''
            
        mae = mean_absolute_error(predictions, ground_truth) 
        mse = mean_squared_error(predictions, ground_truth)
        
        return {'Mean Squared Error' : round(mse, 2), 
                'Mean Absolute Error' : round(mae, 2)  }
    
    def visualise_predictions(self,
                              predictions: np.ndarray,
                              measure : station.measure_dclass, 
                              test_timestamps : list, 
                              ground_truth : np.ndarray | None ) -> tuple[Figure, Axes]: 
        
        '''
        Function used to plot the values of predictions and their associated timestamp.  ground_truth is an optinal argument to the function,
        if it is provided then metrics will be computed as well as the ground_truth values being plotted alongside the predicted ones. 
        '''

        fig, ax = plt.subplots(1, figsize = (7,7)) 
        ax.plot(np.arange(len(predictions)), predictions, label  = 'predictions' )

        ax.set_title(f'predictions for {measure.parameter}')


        if isinstance(ground_truth, np.ndarray): 

            ax.plot(np.arange(len(ground_truth)), ground_truth , label = 'ground truth' )

            metrics = self.compute_metrics(predictions, ground_truth) 


            metrics_text = ''
            for metric, value in metrics.items(): 
                metrics_text += f'{metric} : {value}\n' 

            ax.text( 0, 1.05  , metrics_text[0:-2], fontsize=9 ,
                    bbox=dict(facecolor='white', alpha=0.5),
                    transform = ax.transAxes )


        date_range = [*map(self.timestamps_to_date_str, [test_timestamps[i] for i in [0, -1]]) ] 
        units = self.configure_units(date_range) 

        test_timestamps  = [self.format_date(timestamp, units) for timestamp in test_timestamps] 

        ax.set_xticks( np. arange(len(test_timestamps)),  test_timestamps, rotation = 90 ) 
        ax.set_xlabel('time') 

        ax.set_ylabel(measure.units) 

        fig.tight_layout() 

        fig.legend() 

        return fig, ax

    def evaluate_forecast(self,
                         measure : station.measure_dclass, 
                         date_range : list | None = None, 
                         split_date  : str | None = None, 
                         split_size : int = 5, 
                         lag_features : int = 3 ) -> tuple[Figure, Axes]:  
    
        '''
        method which strings all of the previous methods together to to perform a full evaluation and plot a figure.
        The function takes a given measure which we want to forecast, a date range for training/eval, either split_size or split date and 
        finally lag features which define the number of previous values we will be using to forecast future values.

        It returns a plot which compares the expected and predicted value and displays metrics. 
        '''

        date_range = self.validate_date_range(date_range) 
        readings = self.load_data(measure.notation, date_range=date_range) 

        train_x, train_y, test_x, test_y,  test_timestamps = self.transform_data(readings, 
                                                                lag_features=lag_features,
                                                                evaluation_split= True, 
                                                                split_date= split_date, 
                                                                split_size = split_size ) 
        
        self.fit(train_x, train_y) 

        predictions = self.predict(test_x , len(test_y))
        
        fig, ax = self.visualise_predictions(predictions,   measure ,test_timestamps, test_y ) 

        return fig, ax 


