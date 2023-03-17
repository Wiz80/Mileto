from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('get-started', views.gettingStarted, name='get-started')
]