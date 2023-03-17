from django.urls import path
from . import views

urlpatterns = [
    path('login', views.miletoLogin, name='miletoLogin'),
    path('signup', views.miletoSignUp, name='signup')
]