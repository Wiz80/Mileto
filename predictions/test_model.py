from predictions.get_predictors import Day_predictors
from predictions.get_predictors import Weather
from predictions.preprocessing import Normalization
import pandas as pd
import numpy as np

class Test:

    def __init__(self, metadata, filePredictors, periodo, MLModel) -> None:
        self.metadata = metadata
        self.filePredictors = filePredictors
        self.periodo = periodo
        self.MLModel = MLModel

    def testingModel(self):
        demandPredictors = self.metadata['demand predictors']

        weatherPredictors = self.metadata['weather predictors']

        timePredictors = self.metadata['time predictors']

        weatherDataTest = Weather('', '', self.metadata['latitude'], self.metadata['longitud']).get_weather_data(weatherPredictors, False)

        dataModel = Day_predictors(weatherDataTest).call_day_predictors(timePredictors)

        dataModel = pd.DataFrame(dataModel).loc[:23]
        
        #dfsDemandPredictors = [pd.read_excel(self.filePredictors, sheet_name=name) for name in demandPredictors]
        datosDemanda = {name:[] for name in demandPredictors}
        for name in demandPredictors:
            dataDemandPred = pd.read_excel(self.filePredictors, sheet_name=name)
            if name == '1d_bef' and '24_HRS' in demandPredictors:
                demand1dBef = list(dataDemandPred["Demanda [MW]"])[0]
                h24 = pd.read_excel(self.filePredictors, sheet_name='24_HRS')
                demand1dBefNew = list(h24['Demanda [MW]'])[:0:-1]
                demand1dBefNew.insert(0, demand1dBef)
                datosDemanda['1d_bef'] = demand1dBefNew
            else:
                datosDemanda[name] = list(dataDemandPred["Demanda [MW]"])
        
        dataModelRaw = pd.concat([dataModel, pd.DataFrame(datosDemanda)], axis=1)
        dataModel = dataModelRaw.copy()
        normalizacion = Normalization()
        dataModel = normalizacion.normMinMaxExtend(dataModel, dataModel.columns)
        testPredictions = self.MLModel.predict(dataModel)

        testPredictions = testPredictions*max(dataModelRaw[demandPredictors[0]])
        minDemand = min(testPredictions)
        maxDemand = max(testPredictions)

        
        return list(weatherDataTest['time'].loc[:23]), minDemand, maxDemand, testPredictions
