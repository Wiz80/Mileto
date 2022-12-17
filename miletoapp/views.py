from wsgiref.util import request_uri
from django.shortcuts import render, HttpResponse,redirect
from django.forms.models import model_to_dict

# Create your views here.

def index(request):
    return render(request, 'data_colection/data.html')


# Create your views here.
