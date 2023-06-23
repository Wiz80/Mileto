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
from sklearn.utils.fixes import loguniform
from sklearn.model_selection import RandomizedSearchCV

#Predictors
from predictions.models import Demand_Data
from predictions.get_predictors import Day_predictors, Demand_predictors
#Normalización
from predictions.preprocessing import Normalization
#Metrics
from sklearn.metrics import mean_absolute_percentage_error as MAPE
from sklearn.metrics import mean_absolute_error as MAE
from sklearn.metrics import mean_squared_error as MSE



class Train:

    def get_data_to_train(self, weather_data, predictors, MC):
        
        Data_model = Day_predictors(weather_data).call_day_predictors(predictors['time predictors'])
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
        for i in predictors['demand predictors']:
            Data_model[i] = Demand_Pred_2.solve_for(i)

        Data_model_train = Data_model.copy()
    
        #Normalización de datos
        columnsWithoutDemand = list(Data_model.columns[Data_model.columns != 'Demand'])
        normalizacion = Normalization()
        Data_model_train = normalizacion.normMinMaxExtend(Data_model_train, columnsWithoutDemand)
        Data_model_train = normalizacion.normMinMax(Data_model_train, ['Demand'])
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
        return Train_predictors, Train_target, Test_predictors, Test_target


    def training_SVR(self, Train_predictors, Train_target, C, C2, epsilon, gamma, gamma2, Test_predictors, Test_target):

        #SVR
        #  Modo RandomizedSearchCV --------------------------------------------------
        model = SVR()

        best_parameters     = []
        best_scores         = []
        grid_param_svc = {'C':loguniform(C,C2), 'gamma': loguniform(gamma, gamma2),'epsilon':[epsilon]} #Search on grid
        pipe_svc = SVR(kernel="rbf")   # Let's specify the grid parameters (implements cross-validation)
        high_machine = RandomizedSearchCV(estimator=pipe_svc, param_distributions=grid_param_svc,scoring= 'neg_mean_absolute_percentage_error' ,refit=True,verbose=2,n_jobs=-1,n_iter=10)
        
        print(Train_predictors)
        print(Train_target)
        
        high_machine.fit(Train_predictors, Train_target.ravel())#Y_train.ravel())             # We fit the estimator
        
        best_parameters.append(high_machine.best_params_)
        best_scores.append(high_machine.best_score_)
    
        #print(best_parameters)                                  
        #print(best_scores)
        SVR_forecast_model = high_machine.best_estimator_

        Score = SVR_forecast_model.score(Test_predictors, Test_target)
        Target_predictions = SVR_forecast_model.predict(Test_predictors)

        best_params = high_machine.best_params_
        C = best_params['C']   
        gamma = best_params['gamma']
        
        Mape = MAPE(Test_target, Target_predictions)
        Mae = MAE(Test_target, Target_predictions)
        Mse = MSE(Test_target, Target_predictions)



        return SVR_forecast_model, Target_predictions, Score, Mape, Mae, Mse, C, gamma


    def build_SVR(self, Weather_data_train, Weather_data_test, predictors, MC, kernel, C, C2, epsilon, gamma, gamma2):
        
        Weather_data = pd.concat([Weather_data_train, Weather_data_test], ignore_index=True)

        #Datos normalizados, Datos no normalizados
        Data_model_train, Data_model = self.get_data_to_train(Weather_data, predictors, MC)
        
        trainPredictors, trainRealValues, testPredictors, testRealValues = self.data_preparation(Data_model_train, Weather_data, Weather_data_train, Weather_data_test)
        #training_SVR(self, Train_predictors, Train_target, C, epsilon, gamma, Test_predictors, #Test_target)
        SVRModel, testPredictions, Score, Mape, Mae, Mse, C, gamma = self.training_SVR(trainPredictors, trainRealValues, C, C2, epsilon, gamma, gamma2, testPredictors, testRealValues)
          
        
        return SVRModel, testPredictions, Score, Mape, Mae, Mse, Data_model, testRealValues, C, gamma

    