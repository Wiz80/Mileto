arrToLook = {'dayOfTheWeek':[1, 7], 'festDay': [0, 1]}

class Normalization:

    def normMinMaxExtend(self, data, dataColumns):
        dataRaw = data.copy(deep=True)
        for column in dataColumns:
            data[column] = 2*((data[column] - min(data[column]))/(max(data[column])-min(data[column])))-1
            if data[column].isna().all():
                data[column] = 2*((dataRaw[column] - arrToLook[column][0])/(arrToLook[column][1]-arrToLook[column][0]))-1
        return data
       
    def normMinMax(self, data, dataColumns):
        for column in dataColumns:
            data[column] = data[column]/max(data[column])
        
        return data