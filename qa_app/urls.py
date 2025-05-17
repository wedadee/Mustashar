from django.urls import path
from . import views

app_name = "qa_app"

urlpatterns = [
    path("", views.qa_view, name="qa_view"),
    path("api/", views.qa_api, name="qa_api"),
]