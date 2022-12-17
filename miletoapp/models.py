from django.db import models

# Create your models here.

class Weather_track(models.Model):
    id = models.AutoField(primary_key = True)
    Last_Date = models.DateField(auto_now=False, auto_now_add=False)
    updated_at = models.DateField()
    
    def __str__(self):
        return self.Last_Date

class Weather_data(models.Model):
    id = models.AutoField(primary_key=True)
    Date = models.DateField(auto_now=False, auto_now_add=False)
    Time = models.TimeField(auto_now=False, auto_now_add=False)
    Temperature = models.FloatField()
    Dew_Point = models.FloatField()
    Humidy = models.FloatField()
    Wind_Speed = models.FloatField()
    Wind_Gust = models.FloatField()
    Pressure = models.FloatField()

    def __str__(self):
        return self.Date