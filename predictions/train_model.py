#General libraries
import numpy as np 
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import pickle
from datetime import datetime
#SVR
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
#Predictors
from predictions.models import Demand_Data
from predictions.get_predictors import Day_predictors, Demand_predictors
#Metrics
from sklearn.metrics import mean_absolute_percentage_error as MAPE
from sklearn.metrics import mean_absolute_error as MAE
from sklearn.metrics import mean_squared_error as MSE



class Train:

    def get_data_to_train(self, weather_data, Demand_chosen_pred, MC):
        #Predictores de días 
        day_predictors = Day_predictors(weather_data)
        DayOfTheWeek = day_predictors.create_DayOfTheWeek()
        FestDay = day_predictors.create_fest_array(DayOfTheWeek)
        Hour = day_predictors.get_hour()

        Data_model = {}
        for i in weather_data.columns:
            if i != 'time':
                Data_model[i] = weather_data[i]
        
        Data_model['DayOfTheWeek'] = DayOfTheWeek
        Data_model['FestDay'] = FestDay
        Data_model['Hour'] = Hour
        Data_model = pd.DataFrame(Data_model)
        
        #Obtener datos de demanda desde la base de datos
        data_raw = Demand_Data.objects.filter(UCP=MC, Variable="Demanda_Real")
        data_raw = pd.DataFrame.from_records(data_raw.values())
        #calcular predictores de demanda de energía 
        Demand_Pred = Demand_predictors(Data_model)
        Data_model['Demand'] = Demand_Pred.get_demand(weather_data['time'].dt.date, data_raw)
        
        #cambiar OUTLIERS por el percentile 98 y los valores nan por la mediana 
        for i in Data_model.columns:
            Data_model[i].loc[Data_model[Data_model[i].isna()].index.tolist()] = Data_model[i].median()
            if i == 'Demand':
                max_98th = Data_model[i].quantile(0.98)
                Data_model[i].loc[Data_model[Data_model[i] >= max_98th].index] = max_98th 
        

        Demand_Pred_2 = Demand_predictors(Data_model)
        for i in Demand_chosen_pred:
            Data_model[i] = Demand_Pred_2.solve_for(i)

        
        Data_model_train = Data_model.copy()
    
        #Normalización de datos
        for column in Data_model_train.columns:
            if column == 'Demand':
                Data_model_train[column] = Data_model[column]/max(Data_model[column])
            else:
                Data_model_train[column] = 2*((Data_model[column] - min(Data_model[column]))/(max(Data_model[column])-min(Data_model[column])))-1
        
        return Data_model_train, Data_model


    def data_preparation(self, Data_model_train, Weather_data, Weather_data_train, Weather_data_test):
        
        Data_predictors = Data_model_train.drop(columns=['Demand'])
        Data_target = Data_model_train['Demand']

        train_time = list(Weather_data_train['time'].dt.date)
        test_time = list(Weather_data_test['time'].dt.date)

        Train_idx = Data_model_train[(Weather_data['time'].dt.date >= train_time[0]) & (Weather_data['time'].dt.date <= train_time[-1])].index

        Test_idx = Data_model_train[(Weather_data['time'].dt.date >= test_time[0]) & (Weather_data['time'].dt.date <= test_time[-1])].index
        
        Train_predictors = Data_predictors.loc[Train_idx]
        Train_target = Data_target.loc[Train_idx]

        Test_predictors = Data_predictors.loc[Test_idx]
        Test_target = Data_target.loc[Test_idx]
        print(Test_target)
        return Train_predictors, Train_target, Test_predictors, Test_target


    def training_SVR(self, Train_predictors, Train_target, C, epsilon, gamma, Test_predictors, Test_target):

        #SVR
        SVR_forecast_model = SVR(C=C, epsilon=epsilon, gamma=gamma)
        SVR_forecast_model.fit(Train_predictors, Train_target)
        Score = SVR_forecast_model.score(Test_predictors, Test_target)
        Target_predictions = SVR_forecast_model.predict(Test_predictors)
        print(Target_predictions)
        Mape = MAPE(Test_target, Target_predictions)
        Mae = MAE(Test_target, Target_predictions)
        Mse = MSE(Test_target, Target_predictions)

        return SVR_forecast_model, Target_predictions, Score, Mape, Mae, Mse


    def build_SVR(self, Weather_data_train, Weather_data_test, Demand_chosen_pred, MC, kernel, C, epsilon, gamma):
        
        Weather_data = pd.concat([Weather_data_train, Weather_data_test], ignore_index=True)

        #Datos normalizados, Datos no normalizados
        Data_model_train, Data_model = self.get_data_to_train(Weather_data, Demand_chosen_pred, MC)
        
        trainPredictors, trainRealValues, testPredictors, testRealValues = self.data_preparation(Data_model_train, Weather_data, Weather_data_train, Weather_data_test)
        
        print(trainPredictors)
        print(testPredictors)
        print(trainRealValues)
        print(testRealValues)

        #training_SVR(self, Train_predictors, Train_target, C, epsilon, gamma, Test_predictors, #Test_target)
        SVRModel, testPredictions, Score, Mape, Mae, Mse = self.training_SVR(trainPredictors, trainRealValues, C, epsilon, gamma, testPredictors, testRealValues)
          
        
        return SVRModel, testPredictions, Score, Mape, Mae, Mse, Data_model, testRealValues

    