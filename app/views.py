from django.shortcuts import render
from django.http import JsonResponse,HttpRequest
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    return render( request, 'app/index.html' )

def about(request):
    return render( request, 'app/about.html' )

def services(request):
    return render( request, 'app/services.html' )
