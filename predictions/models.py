from django.db import models

# Create your models here.
class Demand_Data(models.Model):
    UCP = models.CharField(max_length = 200)
    Variable = models.CharField(max_length = 200)
    Fecha = models.DateField(auto_now=False, auto_now_add=False)
    Tipo_Dia = models.CharField(max_length = 200)
    P1 = models.FloatField()
    P2 = models.FloatField()
    P3 = models.FloatField()
    P4 = models.FloatField()
    P5 = models.FloatField()
    P6 = models.FloatField()
    P7 = models.FloatField()
    P8 = models.FloatField()
    P9 = models.FloatField()
    P10 = models.FloatField()
    P11 = models.FloatField()
    P12 = models.FloatField()
    P13 = models.FloatField()
    P14 = models.FloatField()
    P15 = models.FloatField()
    P16 = models.FloatField()
    P17 = models.FloatField()
    P18 = models.FloatField()
    P19 = models.FloatField()
    P20 = models.FloatField()
    P21 = models.FloatField()
    P22 = models.FloatField()
    P23 = models.FloatField()
    P24 = models.FloatField()
    Total = models.FloatField()
    PO19 = models.FloatField()
    PO20 = models.FloatField()
    PO21 = models.FloatField()