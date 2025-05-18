from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = "qa_app"

urlpatterns = [
    path("", views.qa_view, name="qa_view"),
    path("api/", views.qa_api, name="qa_api"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
