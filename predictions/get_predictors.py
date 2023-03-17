import numpy as np
import pandas as pd
from datetime import datetime
import requests


dias_festivos = [datetime(1900, 1, 1, 0, 0),
                datetime(1900, 1, 10, 0, 0),
                datetime(1900, 3, 21, 0, 0),
                datetime(1900, 4, 14, 0, 0),
                datetime(1900, 4, 15, 0, 0),
                datetime(1900, 5, 1, 0, 0),
                datetime(1900, 5, 30, 0, 0),
                datetime(1900, 6, 20, 0, 0),
                datetime(1900, 6, 27, 0, 0),
                datetime(1900, 7, 4, 0, 0),
                datetime(1900, 7, 20, 0, 0),
                datetime(1900, 8, 7, 0, 0),
                datetime(1900, 8, 15, 0, 0),
                datetime(1900, 10, 17, 0, 0),
                datetime(1900, 11, 7, 0, 0),
                datetime(1900, 11, 14, 0, 0),
                datetime(1900, 12, 8, 0, 0),
                datetime(1900, 12, 25, 0, 0)]


class Weather:
    def __init__(self, inicio, final, latitude, longitude):
        self.inicio = inicio
        self.final = final
        self.latitude = latitude
        self.longitude = longitude 
    
    def get_weather_data(self, weather_chosen_params, isHistorical):
        if isHistorical:
            url = f"https://archive-api.open-meteo.com/v1/era5?latitude={self.latitude}&longitude={self.longitude}&start_date={self.inicio}&end_date={self.final}&hourly="
        else:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.latitude}&longitude={self.longitude}&hourly="
        for i in weather_chosen_params:
            if i == weather_chosen_params[-1]:
                url += f"{i}"
            else:
                url += f"{i},"
        url += "&timezone=auto"
        response = requests.request("GET", url)
        weather_data = response.json()
        weather_data = pd.DataFrame(weather_data['hourly'])
        weather_data['time'] = pd.to_datetime(weather_data['time'])
        return weather_data

class Day_predictors:

    def __init__(self, weather_data):
        self.weather_data = weather_data

    #array para día de la semana
    def create_DayOfTheWeek(self):
        DayOfTheWeek = np.array(pd.to_datetime(self.weather_data['time']).dt.dayofweek)
        return DayOfTheWeek
    
    #array para días festivos
    def create_fest_array(self, DayOfTheWeek):
        fds_fest = []
        for idx, day in enumerate(self.weather_data['time']):
            deja = False
            fest_day_confirm = [True for i in dias_festivos if day.day == i.day and day.month == i.month]
            if fest_day_confirm:
                fds_fest.append(1)
                deja = True
            elif (DayOfTheWeek[idx] == 6 or DayOfTheWeek[idx] == 5) and not deja:
                fds_fest.append(1)
            elif (DayOfTheWeek[idx] == 6 or DayOfTheWeek[idx] == 5) and deja:
                pass
            else:
                fds_fest.append(0)
        return np.array(fds_fest)
    
    #array para obtener la hora 
    def get_hour(self):
        return np.array(self.weather_data['time'].dt.hour)

    def call_day_predictors(self, timePredictors):
        #Predictores de días 
        dayOfTheWeek = self.create_DayOfTheWeek()
        festDay = self.create_fest_array(dayOfTheWeek)
        hour = self.get_hour()

        data_model = {}
        for i in self.weather_data.columns:
            if i != 'time':
                data_model[i] = self.weather_data[i]

        dayPredictorsAssign = {'dayOfTheWeek': dayOfTheWeek, 'festDay': festDay, 'dayHour': hour}
        for timePred in timePredictors:
            data_model[timePred] = dayPredictorsAssign[timePred]

        return data_model

class Demand_predictors:

    def __init__(self, Data):
        self.Data = Data

    #Demanda por horas
    def get_demand(self, Date, Demand_raw):
        self.Data.insert(len(self.Data.columns),"Demand", None)
        Demand = self.Data['Demand']
        unique_dates = Date.unique()
        for date in unique_dates:
            get_demand_in_date = Demand_raw[Demand_raw['Fecha'] == date]
            get_data_in_date = self.Data[Date == date]
            if not get_demand_in_date.empty:
                get_demand_in_date = get_demand_in_date.loc[list(get_demand_in_date.index)[0]]      
                demand_in_date = [float(get_demand_in_date[i]) for i in [f'P{i}' for i in range(1,25)]]
                #Demanda por horas
                Demand.loc[get_data_in_date.index] = demand_in_date[:len(get_data_in_date)]
        return Demand

    #Demanda promedio de las últimas 24 horas
    def get_demand_24_HRS(self):
        Avg_Demand_24 = np.array(self.Data['Demand'])
        for idx in range(len(self.Data['Demand'])):
            if idx <= 24:
                data_24 = list(self.Data['Demand'][:idx+1])
            else:   
                data_24 = list(self.Data['Demand'][idx-24:idx])
            Avg_Demand_24[idx] = sum(data_24)/len(data_24)
        return Avg_Demand_24

    #Demanda de la hora coincidente con un día de anterioridad
    def get_demand_1d_bef(self):
        Demand_1d_bef = np.array(self.Data['Demand'])
        for idx in range(24, len(self.Data['Demand'])):
            Demand_1d_bef[idx] = self.Data['Demand'].loc[idx-24]
        return Demand_1d_bef
    
    #Demanda de la hora coincidente con 7 días de anterioridad
    def get_demand_7d_bef(self):
        Demand_7d_bef = np.array(self.Data['Demand'])
        for idx in range(24*7, len(self.Data['Demand'])):
            Demand_7d_bef[idx] = self.Data['Demand'].loc[idx-24*7]
        return Demand_7d_bef

    def solve_for(self, name:str):
        do = f"get_demand_{name}"
        if hasattr(self, do) and callable(func := getattr(self, do)):
            get_dem = func()
            return get_dem
        
