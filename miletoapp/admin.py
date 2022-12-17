from django.contrib.auth.admin import UserAdmin 
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Weather_track, Weather_data

# Register your models here.

admin.site.register(Weather_track)
admin.site.register(Weather_data)

class Weather_trackInline(admin.StackedInline):
    model = Weather_track
    can_delete = False
    verbose_name_plural = 'Weather trackers'

class Weather_dataInline(admin.StackedInline):
    model = Weather_data
    can_delete = False
    verbose_name_plural = 'Weather data'

