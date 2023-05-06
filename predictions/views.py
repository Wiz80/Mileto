from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
import openpyxl
from datetime import datetime, timedelta
import time
import pickle
import pandas as pd
import numpy as np
import json
import os
#Train
from predictions.train_model import Train
from predictions.get_predictors import Weather
#Test
from predictions.test_model import Test
#Save model
from predictions.models import Demand_Data
from predictions.Google_Cloud import *
from predictions.Google_Cloud.googleCloudInstance import Google_Cloud_Drive

weatherVarList = [
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

demandVarList = [
    "24_HRS",
    "1d_bef",
    "7d_bef",
]

timeVarList = [
    "dayHour",
    "dayOfTheWeek",
    "festDay"
]

@login_required
def predictions(request):
    googleDriveInstance = Google_Cloud_Drive()
    #Google drive id folder de los modelos
    idModelsFolder = '17BskLL0bgyjnsTTsXv6OkuXASzyylej7'
    listaModelos = googleDriveInstance.listar_folder(idModelsFolder)
    idMetadataFolder = '1peyk-9Ym69AJH-qXxyD1cGA7GbFLumI7'
    listaMetadata = np.array(googleDriveInstance.listar_folder(idMetadataFolder))

    if request.method == 'POST':
        model = request.POST["modelSelected"]
        periodo = int(request.POST["periodo"])
        nameToLook = f'{model[:-4]}.json'
        metadataChosen = list(listaMetadata[listaMetadata == nameToLook])[0]
        query = f"title = '{metadataChosen}'"
        id = googleDriveInstance.busca(query)
        metadata = googleDriveInstance.getMetadata(id)
        # Crear un nuevo libro de Excel
        workbook = openpyxl.Workbook()

        now = datetime.now()
        for demandPred in metadata['demand predictors']:
            sheet = workbook.create_sheet(demandPred)
            sheet.append(["Hora", "Demanda [MW]"])
            # Agregar horas y demanda de energía a la hoja "Demanda_24h_anteriores"
            for i in range(periodo*24):
                if demandPred == '24_HRS':
                    date = (now - timedelta(hours=i+1))
                if demandPred == '1d_bef':
                    date = (now - timedelta(hours=24+i))
                if demandPred == '7d_bef':
                    date = now - timedelta(days=7, hours=i)
                sheet.append([date.strftime("%Y-%m-%d %H:%M"), ""])

        # Remueve la hoja del libro de trabajo
        workbook.remove(workbook['Sheet'])    
        # Guardar el archivo de Excel
        workbook.save('static/models/templatePredictorsDemand.xlsx')
        googleDriveInstance = Google_Cloud_Drive()
        id_file = "1KUMoHjPHjbsRNOd1QEQ5xj8fyd0crNHZDDOsxiOTmgU"
        #Guardar template predictores de demanda
        googleDriveInstance.sobreescribir_archivo(id_file, 'static/models/templatePredictorsDemand.xlsx', 'templatePredictorsDemand') 
        metadataJson = json.dumps(metadata)
        #Google drive id folder del metadata 
        return render(request, 'forecasting/test.html', {
                  'listaModelos': listaModelos,
                  'listaMetada': listaMetadata,
                  'metadata': metadata,
                  'metadataJson': metadataJson,
                  'predictores': metadata['demand predictors'],
                  'now': now,
                  'period': periodo,
                  'modelName': model
        })

    return render(request, 'forecasting/test.html', {
                  'listaModelos': listaModelos,
                  'listaMetada': listaMetadata,
                  'metadata': False
    })

@login_required
def test_model(request):
    if request.method == 'POST':
        
        period = int(request.POST["periodo"])

        metadataJson = request.POST.get("input-metadata")
        metadata = json.loads(metadataJson)
        try:
            filePredictors = request.FILES['filePredictors']
        #dfsDemandPredictors = [pd.read_excel(filePredictors, sheet_name=name) for name in demandPredictors]
        except:
            return redirect('predictions')
        
        googleDriveInstance = Google_Cloud_Drive()
        model = request.POST["modelName"]
        idModel = googleDriveInstance.busca(f"title = '{model}'")
        MLModel = googleDriveInstance.getModel(idModel)
        testModelInstance = Test(metadata, filePredictors, period, MLModel)
        timePredictions, minDemand, maxDemand, testPredictions = testModelInstance.testingModel()

        results = pd.DataFrame({'time': np.array(timePredictions),
                                'testPredictions': np.array(testPredictions)})
        
        data = results.to_json(orient='records')
        
        return render(request, 'forecasting/test.html', {
                               'metadata': metadata,
                               'metadataJson': metadata,
                               'period': period,
                               'modelName': model,
                               'inicio': timePredictions[0],
                               'final' : timePredictions[-1],
                               'min'   : minDemand,
                               'max'   : maxDemand,
                               'data'  : data,
                               'results': results
                    })

    return render(request, 'forecasting/test.html')

@user_passes_test(lambda u: u.is_superuser)
def train_model(request):
    #Entradas del modelo
    demandaModel = Demand_Data.objects.all()
    demandaModel = pd.DataFrame(list(demandaModel.values()))
    UCPBef = demandaModel['UCP'].unique()
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


        predictors = {
                        'demand predictors': [],
                        'weather predictors': [],
                        'time predictors': []
                     }
        
        predictorsList = [demandVarList, weatherVarList, timeVarList]
        #Predictores de demanda = []
        for lista, predictorTopic  in zip(predictorsList, predictors):
            for lookedPredictor in lista:
                try:
                    request.POST[lookedPredictor]
                    predictors[predictorTopic].append(lookedPredictor)
                except:
                    pass
                    
        modelName = request.POST['modelName']
        #Obtener datos metereológicos
        #Train
        Weather_data_train = Weather(start_train_date, end_train_date, latitude, longitud).get_weather_data(predictors['weather predictors'], True)
        #Test
        Weather_data_test = Weather(start_test_date, end_test_date, latitude, longitud).get_weather_data(predictors['weather predictors'], True)
        
        if model == 'SVR':
            #Entrenar modelo SVR
            train_model = Train()

            SVRModel, testPredictions, Score, Mape, Mae, Mse, Data_model, testRealValues = train_model.build_SVR(Weather_data_train,Weather_data_test, predictors, MC, kernel, C, epsilon, gamma)
            
            #Demanda predecida no normalizada
            testPredictions = testPredictions*max(Data_model['Demand'])
            testRealValues = testRealValues*max(Data_model['Demand'])
            
            results = {'time': np.array(Weather_data_test['time']),
                       'testRealValues': np.array(testRealValues),
                       'testPredictions': np.array(testPredictions)}

            results = pd.DataFrame(results)
            results.to_excel('static/models/results.xlsx', sheet_name='predicciones', index=False)   
            rawFileName = f'static/models/{modelName}'
            SVRFileName = rawFileName+'.sav' 
            pickle.dump(SVRModel, open(SVRFileName, 'wb'))

            googleDriveInstance = Google_Cloud_Drive()
            id_folder = '1orty5LnDr3sYsPaZ7q_2eihickjlsiva'
            #Guardar modelo SVR
            googleDriveInstance.subir_archivo(SVRFileName, id_folder)

            id_file = "1IB0_RT1jKDs_MTq7hl7MNgvan_PlwJP4"
            #Guardar resultados SVR
            googleDriveInstance.sobreescribir_archivo(id_file, 'static/models/results.xlsx', 'results.xlsx') 
            data = results.to_json(orient='records')
            
            
            metadata = {'MC': MC,
                        'model':model,
                        'start_train_date': str(start_train_date),
                        'end_train_date': str(end_train_date),
                        'start_test_date': str(start_test_date),
                        'end_test_date': str(end_test_date),
                        'latitude': latitude,
                        'longitud': longitud,
                        'kernel': kernel,
                        'epsilon': epsilon,
                        'gamma': gamma,
                        'C': C,
                        'demand predictors': predictors['demand predictors'],
                        'weather predictors': predictors['weather predictors'],
                        'time predictors': predictors['time predictors']}
            
            metadataFileName = rawFileName+'.json'
            with open(metadataFileName, "w") as file:
                json.dump(metadata, file)

            #Guardar metadata
            googleDriveInstance.subir_archivo(f'{rawFileName}.json', id_folder)

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
                           'fileName': modelName,
                           'MCModel': UCPBef

                           })

        elif model == 'ANN':
            pass
    
    return render(request, 'forecasting/train.html', 
                  {
                    'fileName': '_',
                    'MCModel': UCPBef
                  })

@user_passes_test(lambda u: u.is_superuser)
def save_model(request):
    if request.method == 'POST':
        fileName = request.POST['fileNameModel']
        googleDriveInstance = Google_Cloud_Drive()
        #id Drive folder de metadata
        idFolderMetadata = '1peyk-9Ym69AJH-qXxyD1cGA7GbFLumI7'

        #id Drive folder de los modelos
        idFolderData = "17BskLL0bgyjnsTTsXv6OkuXASzyylej7"
        queryData = f"title = '{fileName}.sav'"
        idData = googleDriveInstance.busca(queryData)
        idMetadata = googleDriveInstance.busca(f"title = '{fileName}.json'")

        googleDriveInstance.mover_archivo(idMetadata, idFolderMetadata)
        googleDriveInstance.mover_archivo(idData, idFolderData)

        folder_path = 'static/models'

        # Obtiene todos los archivos en la carpeta
        files = os.listdir(folder_path)

        # Elimina cada archivo individualmente
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)

        return redirect('predictions')
