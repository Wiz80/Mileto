from django.shortcuts import render
from predictions.models import Demand_Data
from predictions.train_model import Train
from predictions.get_predictors import Weather
from predictions.Google_Cloud import *
from predictions.Google_Cloud.googleCloudInstance import Google_Cloud_Drive
from sklearn.metrics import mean_absolute_percentage_error as MAPE
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta
from predictions.desviaciones import Desviaciones

def getDemandDataFrame(data):
    demandArray = {'hour': [], 'date':[], 'demand': []}
    hour = [f'{i}:00' for i in range(0, 24)]
    for _, dat in data.iterrows():
        demandInDate = [float(dat[i]) for i in [f'P{i}' for i in range(1,25)]]
        date = [dat['Fecha'] for _ in range(0, 24)]
        demandArray['hour'].append(hour)
        demandArray['demand'].append(demandInDate)
        demandArray['date'].append(date)

    for key in demandArray:
        demandArray[key] = np.array(demandArray[key]).reshape(-1)
    
    return pd.DataFrame(demandArray)


def evaluateModels(request):
    demandModel = Demand_Data.objects.all()
    demandModel = pd.DataFrame(list(demandModel.values()))
    UCPBef = demandModel['UCP'].unique()
    if request.method == 'POST':
        mc = request.POST["mc"]
        startDate = datetime.strptime(request.POST["fecha-inicio"], "%Y-%m-%d").date()
        endDate = datetime.strptime(request.POST["fecha-fin"], "%Y-%m-%d").date()
        latitude = request.POST['latitud']
        longitud = request.POST['longitud']

        demandModel = demandModel[demandModel['UCP'] == mc]
        demandModel = demandModel[(demandModel['Fecha'] >= startDate) & (demandModel['Fecha'] <= endDate)]

        ofi = demandModel[demandModel['Variable'] == 'OFI']
        ofi = getDemandDataFrame(ofi)
        predof = np.array(ofi['demand'])

        #importar los modelos
        gCloud = Google_Cloud_Drive()
        idFolderModels = "17BskLL0bgyjnsTTsXv6OkuXASzyylej7"
        listModels = gCloud.listar_folder(idFolderModels)
        predictions = {modelName:[] for modelName in listModels}

        deja = False
        for idx, modelName in enumerate(listModels):
            idModel = gCloud.busca(f"title = '{modelName}'")
            idMetadata = gCloud.busca(f"title = '{modelName[:-4]}.json'")
            model = gCloud.getModel(idModel)
            metadata = gCloud.getMetadata(idMetadata)
                
            if str(metadata['MC']) == mc:   
                weatherData = Weather(startDate, endDate, latitude, longitud).get_weather_data(metadata['weather predictors'], True)      
                predictors = {
                            'demand predictors': metadata['demand predictors'],
                            'weather predictors': metadata['weather predictors'],
                            'time predictors': metadata['time predictors']
                        }
                dataNormalized, dataNotNormalized = Train().get_data_to_train(weatherData, predictors, mc)
                dataPredictors = dataNormalized.drop(columns=['Demand']) 
                testPredictions = model.predict(dataPredictors)
                predictions[modelName] = testPredictions*(max(dataNotNormalized['Demand']))
                
                if not deja:
                    predictions['time'] = list(weatherData['time'])
                    predictions['realDemand'] = list(dataNotNormalized['Demand'])
                    deja = True
        
        newList = []
        for idx, key in enumerate(listModels):
            if len(predictions[key]) == 0:
                del predictions[key]
            else:
                newList.append(key)

        listModels = newList

        
        predictions['OFI'] = predof #(predof/max(predof))*max(dataNotNormalized['Demand'])
        
        #Obtener el modelo con mejor MAPE
        MAPEs = {name: round(MAPE(predictions['realDemand'], predictions[name]),4) for name in listModels} 
        _, idxMinMAPE = min(enumerate(MAPEs.values()), key=lambda x: x[1])
        bestModel = listModels[int(idxMinMAPE)]
        MAPEs['MC'] = round(MAPE(predictions['realDemand'], predictions['OFI']),4)

        modelpred = predictions[bestModel]
        realDemand = predictions['realDemand']
        desviaciones, desviacionesNum = Desviaciones.calcDesviaciones(startDate, endDate, realDemand, modelpred, predof)

        predictions = pd.DataFrame(predictions).to_json(orient='records')
    
        listModels.append('realDemand')
        listModels.append('OFI')


        MAPEs = {key: round(val*100, 3) for key, val in MAPEs.items()}
        return render(request, 'forecasting/evaluate.html',{
            'MCModel': UCPBef,
            'predictions': predictions,
            'min': min(dataNotNormalized['Demand']),
            'max': max(dataNotNormalized['Demand']),
            'inicio': list(weatherData['time'])[0],
            'final': list(weatherData['time'])[-1],
            'modelNames': listModels,
            'best': bestModel,
            'desviaciones': desviaciones,
            'desviacionesNum': desviacionesNum,
            'MAPEs': MAPEs
        })



    return render(request, 'forecasting/evaluate.html',{
        'MCModel': UCPBef
    })

