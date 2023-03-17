from django.urls import path
from . import views

urlpatterns = [
    path('testing', views.predictions, name='predictions'),
    path('training', views.train_model, name= 'train'),
    path('test_model', views.test_model, name= 'test'),
    path('save_model', views.save_model, name = 'save_model')
]