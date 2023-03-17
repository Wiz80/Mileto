from django.urls import path
from . import views

urlpatterns = [
    path('evaluate', views.evaluateModels, name='evaluate'),
]