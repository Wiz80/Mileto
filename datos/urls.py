from django.urls import path
from . import views

urlpatterns = [
    path('data', views.add_data, name='data')
]