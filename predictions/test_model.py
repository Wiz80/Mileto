from predictions.get_predictors import Day_predictors
from predictions.get_predictors import Weather
from predictions.preprocessing import Normalization
import pandas as pd
import numpy as np
import datetime


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

        dataModel = pd.DataFrame(dataModel)[:self.periodo*24]
        
        #dfsDemandPredictors = [pd.read_excel(self.filePredictors, sheet_name=name) for name in demandPredictors]
        datosDemanda = {name:[] for name in demandPredictors}
        for name in demandPredictors:
            dataDemandPred = pd.read_excel(self.filePredictors, sheet_name=name)
            datosDemanda[name] = list(dataDemandPred["Demanda [MW]"])
        
        dataModelRaw = pd.concat([dataModel, pd.DataFrame(datosDemanda)], axis=1)
        dataModel = dataModelRaw.copy()
        normalizacion = Normalization()
        dataModel = normalizacion.normMinMaxExtend(dataModel, dataModel.columns)
        testPredictions = self.MLModel.predict(dataModel)

        testPredictions = testPredictions*max(dataModelRaw[demandPredictors[0]])
        minDemand = min(testPredictions)
        maxDemand = max(testPredictions)
        
        weatherDataTest = weatherDataTest.loc[1:self.periodo*24]
        weatherDataTest['time'] = pd.to_datetime(weatherDataTest['time'])

        # Sumar una hora a la columna de fecha utilizando la función apply() y timedelta
        weatherDataTest['time'] = weatherDataTest['time'].apply(lambda x: x + datetime.timedelta(hours=datetime.datetime.now().hour))

        testPredictions = [round(pred, 3) for pred in testPredictions]
        return list(weatherDataTest['time']), minDemand, maxDemand, testPredictions
