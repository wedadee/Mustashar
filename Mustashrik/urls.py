"""
Definition of urls for Mustasharik.
"""

from datetime import datetime
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   path("", include("app.urls")),
    path("qa/", include("qa_app.urls")),
    path('contract/', include('contract_analyzer_app.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
