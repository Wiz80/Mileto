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
                testPredictions = model.predict(dataPredictors)*max(dataNotNormalized['Demand'])
                predictions[modelName] = testPredictions

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

        ofi = demandModel[demandModel['Variable'] == 'OFI']
        ofi = getDemandDataFrame(ofi)
        predictions['OFI'] = list(ofi['demand'])
        
        #Obtener el modelo con mejor MAPE
        MAPEs = {name: round(MAPE(predictions['realDemand'], predictions[name]),4) for name in listModels} 
        _, idxMinMAPE = min(enumerate(MAPEs.values()), key=lambda x: x[1])
        bestModel = listModels[int(idxMinMAPE)]
        MAPEs['MC'] = round(MAPE(predictions['realDemand'], predictions['OFI']),4)
        
        desviaciones = {'model': [], 'MC': [], 'resolucion': []}
        desviacionesNum = {'model': [], 'MC': [], 'resolucion': []}

        numOfMonths = relativedelta(endDate, startDate).months

        newDate = startDate
        modelpred = predictions[bestModel]
        ofipred = predictions['OFI']
        realDemand = predictions['realDemand']

        if numOfMonths > 0:
            for month in range(numOfMonths):
                _, dias = calendar.monthrange(newDate.year, newDate.month)
                for threshold, creg in zip([0.04, 0.05], ['CREG 100', 'CREG 025']):
                    x1 = [np.abs(sum(modelpred[idx:idx+24]) - sum(realDemand[idx:idx+24])) for idx in range(0, len(realDemand), 24) if abs(sum(modelpred[idx:idx+24]) - sum(realDemand[idx:idx+24])) / sum(realDemand[idx:idx+24]) > threshold]
                    x2 = [np.abs(sum(ofipred[idx:idx+24]) - sum(realDemand[idx:idx+24])) for idx in range(0, len(realDemand), 24) if abs(sum(ofipred[idx:idx+24]) - sum(realDemand[idx:idx+24])) / sum(realDemand[idx:idx+24]) > threshold]
                    x3 = [np.abs(modelpred[idx]-realVal) for idx, realVal in enumerate(realDemand) if np.abs(modelpred[idx]-realVal)/realVal > threshold]
                    x4 = [np.abs(ofipred[idx]-realVal) for idx, realVal in enumerate(realDemand) if np.abs(ofipred[idx]-realVal)/realVal > threshold]

                    desviaciones['model'].append([round(sum(x3), 4), round(sum(x1), 4)])
                    desviaciones['MC'].append([round(sum(x4), 4), round(sum(x2), 4)])
                    desviaciones['resolucion'].append(f"{creg} {newDate.strftime('%B')}")

                    desviacionesNum['model'].append([len(x3), len(x1)])
                    desviacionesNum['MC'].append([len(x4), len(x2)])
                    desviacionesNum['resolucion'].append(f"{creg} {newDate.strftime('%B')}")
            
                newDate = newDate + timedelta(days=dias)
                modelpred = modelpred[dias*24:]
                ofipred = ofipred[dias*24:]
                realDemand = realDemand[dias*24:]
        else:
            for threshold, creg in zip([0.04, 0.05], ['CREG 100', 'CREG 025']):
                    x1 = [np.abs(sum(predictions['realDemand'][idx:idx+24]) - sum(predictions[bestModel][idx:idx+24])) for idx in range(0, len(predictions['realDemand']), 24) if abs(sum(predictions['realDemand'][idx:idx+24]) - sum(predictions[bestModel][idx:idx+24])) / sum(predictions['realDemand'][idx:idx+24]) > threshold]
                    x2 = [np.abs(sum(predictions['OFI'][idx:idx+24]) - sum(predictions['realDemand'][idx:idx+24])) for idx in range(0, len(predictions['realDemand']), 24) if abs(sum(predictions['OFI'][idx:idx+24]) - sum(predictions['realDemand'][idx:idx+24])) / sum(predictions['realDemand'][idx:idx+24]) > threshold]
                    x3 = [np.abs(predictions[bestModel][idx]-realVal) for idx, realVal in enumerate(predictions['realDemand']) if np.abs(predictions[bestModel][idx]-realVal)/realVal > threshold]
                    x4 = [np.abs(predictions['OFI'][idx]-realVal) for idx, realVal in enumerate(predictions['realDemand']) if np.abs(predictions['OFI'][idx]-realVal)/realVal > threshold]
                    
                    desviaciones['model'].append([round(sum(x3), 4), round(sum(x1), 4)])
                    desviaciones['MC'].append([round(sum(x4), 4), round(sum(x2), 4)])
                    desviaciones['resolucion'].append(f"{creg} {newDate.strftime('%B')}")
                    
                    desviacionesNum['model'].append([len(x3), len(x1)])
                    desviacionesNum['MC'].append([len(x4), len(x2)])
                    desviacionesNum['resolucion'].append(f"{creg} {newDate.strftime('%B')}")
            

        desviaciones = pd.DataFrame(desviaciones)
        desviacionesNum = pd.DataFrame(desviacionesNum)

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

