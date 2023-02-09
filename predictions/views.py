from django.shortcuts import render
from datetime import datetime
import pickle
import pandas as pd
import numpy as np
#Train
from predictions.models import Demand_Data
from predictions.train_model import Train
from predictions.get_predictors import Weather
#Save model
from predictions.Google_Cloud import *
from predictions.Google_Cloud.googleCloudInstance import Google_Cloud_Drive

lista_weather_variables = [
    "temperature_2m",
    "relativehumidity_2m",
    "dewpoint_2m",
    "apparent_temperature",
    "pressure_msl",
    "surface_pressure",
    "precipitation",
    "rain",
    "snowfall",
    "cloudcover",
    "cloudcover_high",
    "cloudcover_mid",
    "cloudcover_low",
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "direct_normal_irradiance"
]

lista_demand_variables = [
    "24_HRS",
    "1d_bef",
    "7d_bef"
]

# Create your views here.
def predictions(request):
    return render(request, 'forecasting/test.html')

def train_model(request):
    #Entradas del modelo
    if request.method == 'POST':
        
        #MC
        MC = request.POST["mc"]

        #Modelo
        model = request.POST["model"]

        #Datos de fechas
        try:
            start_train_date = datetime.strptime(request.POST["train_start"], "%Y-%m-%d").date()
            end_train_date = datetime.strptime(request.POST["train_finish"], "%Y-%m-%d").date()
            start_test_date = datetime.strptime(request.POST["test_start"], "%Y-%m-%d").date()
            end_test_date = datetime.strptime(request.POST["test_finish"], "%Y-%m-%d").date()
        except:
            return render(request, 'forecasting/train.html',{
                'error': 'Debe seleccionar las fechas de entrenamiento y testeo'
            })
        
        #Selección de coordenadas
        latitude = request.POST['latitud']
        longitud = request.POST['longitud']
        
        #Hiperparametros del modelo
        kernel = request.POST['kernel']
        epsilon = float(request.POST['eps'])
        gamma = float(request.POST['gam'])
        C = int(request.POST['C'])

        #Predictores de demanda
        Demand_chosen = []
        for i in lista_demand_variables:
            try:
                request.POST[i]
                Demand_chosen.append(i)
            except:
                pass

        #Variables metereológicas
        weather_chosen = []
        for i in lista_weather_variables:
            try:
                request.POST[i]
                weather_chosen.append(i)
            except:
                pass
              
        #Obtener datos metereológicos
        #Train
        Weather_data_train = Weather(start_train_date, end_train_date, latitude, longitud).get_weather_data(weather_chosen)
        #Test
        Weather_data_test = Weather(start_test_date, end_test_date, latitude, longitud).get_weather_data(weather_chosen)
        
        if model == 'SVR':
            #Entrenar modelo SVR
            train_model = Train()

            SVRModel, testPredictions, Score, Mape, Mae, Mse, Data_model, testRealValues = train_model.build_SVR(Weather_data_train,Weather_data_test, Demand_chosen, MC, kernel, C, epsilon, gamma)
            #Demanda predecida no normalizada
            testPredictions = testPredictions*max(Data_model['Demand'])
            testRealValues = testRealValues*max(Data_model['Demand'])
            
            results = {'time': np.array(Weather_data_test['time']),
                       'testRealValues': np.array(testRealValues),
                       'testPredictions': np.array(testPredictions)}

            results = pd.DataFrame(results)
            results.to_excel('static/models/results.xlsx', sheet_name='predicciones', index=False)   
            today = datetime.now()
            year = today.year
            month = today.month
            day = today.day
            hour = today.hour   
            dateName = f'{day}_{month}_{year}_{hour}'
            rawFileName = f'static/models/SVR_{dateName}'
            SVRFileName = rawFileName+'.sav' 
            pickle.dump(SVRModel, open(SVRFileName, 'wb'))

            googleDriveInstance = Google_Cloud_Drive()
            id_folder = '1Iu2CF4PPLc7vxD6b88Y7WZHVmFkiVes3'
            #Guardar modelo SVR
            googleDriveInstance.subir_archivo(SVRFileName, id_folder)

            id_file = "1IB0_RT1jKDs_MTq7hl7MNgvan_PlwJP4"
            #Guardar resultados SVR
            googleDriveInstance.sobreescribir_archivo(id_file, 'static/models/results.xlsx', 'results.xlsx') 
            data = results.to_json(orient='records')
            
            
            metadata = {'MC': MC,
                        'model':model,
                        'start_train_date': start_train_date,
                        'end_train_date': end_train_date,
                        'start_test_date': start_test_date,
                        'end_test_date': end_test_date,
                        'latitude': latitude,
                        'longitud': longitud,
                        'kernel': kernel,
                        'epsilon': epsilon,
                        'gamma': gamma,
                        'C': C,
                        'demand predictors': Demand_chosen,
                        'weather predictors': weather_chosen}
            
            metadata = pd.DataFrame(metadata)
            results.to_csv(f'{rawFileName}.csv', index=False) 
            id_file_metadata = '1Rimaiu4TgcdWKUU0wBTBIzSf8tIvaecg'
            #Guardar metadata
            googleDriveInstance.sobreescribir_archivo(id_file_metadata, f'{rawFileName}.csv', 'metadata.csv') 

            return render(request, 'forecasting/train.html', 
                          {'score' : "%.4f" % np.abs(Score),
                           'MAPE'  : "%.4f" % Mape, 
                           'MAE'   : "%.4f" % Mae,
                           'MSE'   : "%.4f" % Mse,
                           'data'  : data,
                           'inicio': str(list(Weather_data_test['time'].dt.date)[0]),
                           'final' : str(list(Weather_data_test['time'].dt.date)[-1]),
                           'min'   : min(Data_model['Demand']),
                           'max'   : max(Data_model['Demand']),
                           'fileName_': dateName
                           })

        elif model == 'ANN':
            pass

    return render(request, 'forecasting/train.html', 
                {
                 'fileName_': 'SVR_8_2_2023_15'
                })

def save_model(request, fileName):
    googleDriveInstance = Google_Cloud_Drive()
    id_folder = "17BskLL0bgyjnsTTsXv6OkuXASzyylej7"
    queryData = f"title = '{fileName}.sav'"
    idData = googleDriveInstance.busca(queryData)
    googleDriveInstance.mover_archivo(idData, id_folder)
    idMetadata = f"title = 'metadata'"
    googleDriveInstance.mover_archivo(idMetadata, id_folder)
    return render(request, 'forecasting/test.html')


def add_data(request):
    if request.method == 'POST':
        cali_real = pd.read_csv('static\cali_pronostico.csv')
        cali_real['FECHA'] = pd.to_datetime(cali_real['FECHA']).dt.strftime('%Y-%m-%d')
        df_records = cali_real.to_dict('records')
        model_instances = [Demand_Data(
            UCP = 'MC-Cali',
            Variable = record['Variable'], 
            Fecha = record['FECHA'],
            Tipo_Dia = record['TIPO_DIA'],
            P1 = record['P1'],
            P2 = record['P2'],
            P3 = record['P3'],
            P4 = record['P4'],
            P5 = record['P5'],
            P6 = record['P6'],
            P7 = record['P7'],
            P8 = record['P8'],
            P9 = record['P9'],
            P10 = record['P10'],
            P11 = record['P11'],
            P12 = record['P12'],
            P13 = record['P13'],
            P14 = record['P14'],
            P15 = record['P15'],
            P16 = record['P16'],
            P17 = record['P17'],
            P18 = record['P18'],
            P19 = record['P19'],
            P20 = record['P20'],
            P21 = record['P21'],
            P22 = record['P22'],
            P23 = record['P23'],
            P24 = record['P24'],
            Total = record['Total'],
            PO19 = record['PO19'],
            PO20 = record['PO20'],
            PO21 = record['PO21'],
        ) for record in df_records]

        Demand_Data.objects.bulk_create(model_instances)
        
    return render(request, 'data_colection/data.html')
