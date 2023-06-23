import numpy as np
import pandas as pd
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Desviaciones():
    def calcDesviaciones(startDate, endDate, realDemand, modelpred, ofipred):

        numOfMonths = relativedelta(endDate, startDate).months

        newDate = startDate
        desviaciones = {'model': [], 'MC': [], 'resolucion': []}
        desviacionesNum = {'model': [], 'MC': [], 'resolucion': []}

        if numOfMonths > 0:
            for month in range(numOfMonths):
                _, dias = calendar.monthrange(newDate.year, newDate.month)
                for threshold, creg in zip([0.04, 0.05], ['CREG 100', 'CREG 025']):
                    x1 = [np.abs(sum(modelpred[idx:idx+24]) - sum(realDemand[idx:idx+24])) for idx in range(0, len(realDemand), 24) if np.abs(sum(modelpred[idx:idx+24]) - sum(realDemand[idx:idx+24])) / sum(realDemand[idx:idx+24]) > threshold]
                    x2 = [np.abs(sum(ofipred[idx:idx+24]) - sum(realDemand[idx:idx+24])) for idx in range(0, len(realDemand), 24) if np.abs(sum(ofipred[idx:idx+24]) - sum(realDemand[idx:idx+24])) / sum(realDemand[idx:idx+24]) > threshold]
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
                    x1 = [np.abs(sum(realDemand[idx:idx+24]) - sum(modelpred[idx:idx+24])) for idx in range(0, len(realDemand), 24) if np.abs(sum(realDemand[idx:idx+24]) - sum(modelpred[idx:idx+24])) / sum(realDemand[idx:idx+24]) > threshold]
                    x2 = [np.abs(sum(ofipred[idx:idx+24]) - sum(realDemand[idx:idx+24])) for idx in range(0, len(realDemand), 24) if np.abs(sum(ofipred[idx:idx+24]) - sum(realDemand[idx:idx+24])) / sum(realDemand[idx:idx+24]) > threshold]
                    x3 = [np.abs(modelpred[idx]-realVal) for idx, realVal in enumerate(realDemand) if np.abs(modelpred[idx]-realVal)/np.abs(realVal) > threshold]
                    x4 = [np.abs(ofipred[idx]-realVal) for idx, realVal in enumerate(realDemand) if np.abs(ofipred[idx]-realVal)/realVal > threshold]
                    
                    desviaciones['model'].append([round(sum(x3), 4), round(sum(x1), 4)])
                    desviaciones['MC'].append([round(sum(x4), 4), round(sum(x2), 4)])
                    desviaciones['resolucion'].append(f"{creg} {newDate.strftime('%B')}")
                    
                    desviacionesNum['model'].append([len(x3), len(x1)])
                    desviacionesNum['MC'].append([len(x4), len(x2)])
                    desviacionesNum['resolucion'].append(f"{creg} {newDate.strftime('%B')}")
        
        desviaciones = pd.DataFrame(desviaciones)
        desviacionesNum = pd.DataFrame(desviacionesNum)

        return desviaciones, desviacionesNum