from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_pdf, name='contract-view'),
]