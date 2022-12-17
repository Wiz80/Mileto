from django.urls import path
from . import views

urlpatterns = [
    path('get_predictions', views.predictions, name='predictions'),
    path('training', views.train_model, name= 'train'),
    path('data', views.add_data, name = 'data')
]