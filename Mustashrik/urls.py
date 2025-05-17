"""
Definition of urls for Mustasharik.
"""

from datetime import datetime
from django.urls import path, include

urlpatterns = [
   path("", include("app.urls")),
    path("qa/", include("qa_app.urls")),
    path('contract/', include('contract_analyzer_app.urls')),

]
