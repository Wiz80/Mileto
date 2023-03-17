from django.shortcuts import render

from predictions.models import Demand_Data
from django.db.models import Subquery, OuterRef, Count
import pandas as pd
from datetime import datetime
from dateutil import relativedelta

def uploadXMData(MC, start, end, files):
    delta = relativedelta.relativedelta(start, end)
    total_months = delta.months + delta.years * 12
    year = start.year 
    month = start.month - 1
    name_months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    name_months_2 = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
    column_names = ['UCP','Variable','FECHA','TIPO_DIA','Total']
    for _ in range(total_months):
        try:
            try:
                nameExcelFile = f"MC-{MC}-OFI-DR-{name_months[month]} {year}-{name_months[month]} {year}.xlsx"
                fileGetted = [file for file in files if file.name == nameExcelFile][0]
                xls = pd.ExcelFile(fileGetted)
            except:
                try:
                    nameExcelFile = f"U{MC.lower()}-OFI-{name_months_2[month]} {year}-{name_months_2[month]} {year}.xlsx"
                    fileGetted = [file for file in files if file.name == nameExcelFile][0]
                    xls = pd.ExcelFile(fileGetted)
                except:
                    nameExcelFile = f"U{MC.lower()}-OFI-{name_months_2[month]} {year}-{name_months_2[month]} {year}.xls"
                    fileGetted = [file for file in files if file.name == nameExcelFile][0]
                    xls = pd.ExcelFile(fileGetted)
            real = pd.read_excel(xls, 'real')
            pronostico = pd.read_excel(xls, 'pronostico')
            col_idx = 0
            for idx, col in enumerate(real.columns):
                if idx > 3 and idx <= 27:
                    real.columns.values[idx] = f"P{idx-3}"
                    pronostico.columns.values[idx] = f"P{idx-3}"
                elif idx <= 3 or idx == 28:
                    real.columns.values[idx] = column_names[col_idx]
                    pronostico.columns.values[idx] = column_names[col_idx]
                    col_idx+=1
            try:
                data_real = pd.concat([data_real, real])
                data_pronostico = pd.concat([data_pronostico, pronostico])
            except NameError: 
                data_real = real 
                data_pronostico = pronostico
        except:
            pass
        month -= 1
        if month == -1: 
            month = 11
            year -= 1

    return data_real, data_pronostico

def deleteDuplicates():
    queryset = Demand_Data.objects.all()
    # Utilizamos el método distinct() para obtener una lista de objetos únicos
    unique_objects = queryset.distinct('Fecha','P1', 'P5', 'P10', 'P15', 'P20')

    # Eliminamos los objetos duplicados del modelo
    for obj in queryset:
        if obj not in unique_objects:
            obj.delete()


def add_data(request):
    querySet = Demand_Data.objects.all()
    demandAll = pd.DataFrame.from_records(querySet.values())
    demandRecords = demandAll[demandAll['Variable'] == 'OFI']
    fechasUCP = demandRecords.groupby('UCP')['Fecha'].agg(['min', 'max'])

    if request.method == 'POST':
        uploadedFiles = request.FILES.getlist('demandFiles')
        UCP = request.POST["UPC-MC"]
        fechaInicio = datetime.strptime(request.POST["fechaInicio"], "%Y-%m-%d").date()
        fechaFinal = datetime.strptime(request.POST["fechaCierre"], "%Y-%m-%d").date()
        dataReal, dataPronostico = uploadXMData(UCP, fechaFinal, fechaInicio, uploadedFiles)
        datos = [dataReal, dataPronostico]
        for data in datos:
            data['FECHA'] = pd.to_datetime(data['FECHA']).dt.strftime('%Y-%m-%d')
            df_records = data.to_dict('records')
            model_instances = [Demand_Data(
                UCP = f'MC-{UCP}',
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
        deleteDuplicates()
        return render(request, 'data_colection/data.html', {
            'successMessage': f'Los archivos del mercado de comerzialión MC-{UCP} fueron añadidos correctamente a la base de datos',
            'fechasUCP': fechasUCP,
            'listaMC': list(demandRecords['UCP'].unique()),
            'registros': len(demandAll)
        })
    return render(request, 'data_colection/data.html', {'successMessage': False,
                                                        'fechasUCP': fechasUCP, 
                                                        'listaMC': list(demandRecords['UCP'].unique()),
                                                        'registros': len(demandAll)})
