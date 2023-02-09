from django.urls import path
from . import views

urlpatterns = [
    path('testing', views.predictions, name='predictions'),
    path('training', views.train_model, name= 'train'),
    path('data', views.add_data, name = 'data'),
    path('save_model/<str:fileName>/', views.save_model, name = 'save_model')
]